import os
import socket
import warnings
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from textwrap import dedent
from urllib.parse import urljoin, urlparse, urlunparse

import jinja2

import jupyterhub
from jupyterhub.spawner import Spawner

from marathon import MarathonClient
from marathon.exceptions import NotFoundError
from marathon.models.app import MarathonApp, MarathonHealthCheck, PortDefinition
from marathon.models.constraint import MarathonConstraint
from marathon.models.container import (
    MarathonContainer,
    MarathonContainerVolume,
    MarathonDockerContainer,
)

import requests

from tornado import gen
from tornado.concurrent import run_on_executor

from traitlets import Any, Float, Integer, List, Unicode, default, observe

from .exceptions import UCRSpawnerException
from .mesosslave import MesosSlave
from .utils import remove_zeros
from .volumenaming import default_format_volume_name

_jupyterhub_xy = '%i.%i' % (jupyterhub.version_info[:2])


class UCRSpawner(Spawner):

    app_image = Unicode("jupyterhub/singleuser:%s" %
                        _jupyterhub_xy, config=True)

    app_prefix = Unicode(
        "jupyter",
        help=dedent(
            """
            Prefix for app names. The full app name for a particular
            user will be <prefix>/<username>/notebook.
            """
        )
    ).tag(config=True)

    marathon_host = Unicode(
        u'',
        help="Hostname of Marathon server").tag(config=True)

    marathon_constraints = List(
        [],
        help='Constraints to be passed through to Marathon').tag(config=True)

    mesos_master_host = Unicode(
        None,
        help=dedent(
            """
            Hostname of Mesos Master server.
            Leave it empty if you want to use Mesos leader UI URL of Marathon config.
            """
        ), allow_none=True).tag(config=True)

    unreachable_strategy = Any(
        None,
        help='Unreachable strategy to be passed through to Marathon').tag(config=True)

    volumes = List(
        [],
        help=dedent(
            """
            A list in Marathon REST API format for mounting volumes into the docker container.
            [
                {
                    "containerPath": "/foo",
                    "hostPath": "/bar",
                    "mode": "RW"
                }
            ]

            Note that using the template variable {username} in containerPath,
            hostPath or the name variable in case it's an external drive
            it will be replaced with the current user's name.
            """
        )
    ).tag(config=True)

    max_cpu = Float(2, config=True)
    cpu = Float(1, config=True)

    max_mem = Float(4096, config=True)
    mem = Float(1024, config=True)

    max_disk = Float(20000, config=True)
    disk = Float(5000, config=True)

    max_gpu = Integer(0, config=True)
    gpu = Integer(0, config=True)

    max_user_port = Integer(2, config=True)
    user_port = Integer(0, config=True)

    mesos_user = Unicode(None, config=True, allow_none=True)

    hub_ip_connect = Unicode(
        "",
        help="Public IP address of the hub"
    ).tag(config=True)

    @observe('hub_ip_connect')
    def _ip_connect_changed(self, change):
        if jupyterhub.version_info >= (0, 8):
            warnings.warn(
                "UCRSpawner.hub_ip_connect is no longer needed with JupyterHub 0.8."
                "  Use JupyterHub.hub_connect_ip instead.",
                DeprecationWarning,
            )

    hub_port_connect = Integer(
        -1,
        help="Public PORT of the hub"
    ).tag(config=True)

    @observe('hub_port_connect')
    def _port_connect_changed(self, change):
        if jupyterhub.version_info >= (0, 8):
            warnings.warn(
                "UCRSpawner.hub_port_connect is no longer needed with JupyterHub 0.8."
                "  Use JupyterHub.hub_connect_port instead.",
                DeprecationWarning,
            )

    format_volume_name = Any(
        help="""Any callable that accepts a string template and a Spawner
        instance as parameters in that order and returns a string.
        """
    ).tag(config=True)

    @default('format_volume_name')
    def _get_default_format_volume_name(self):
        return default_format_volume_name

    # fix default port to 8888, used in the container
    @default('port')
    def _port_default(self):
        return 8888

    # default to listening on all-interfaces in the container
    @default('ip')
    def _ip_default(self):
        return '0.0.0.0'

    _executor = None

    @property
    def executor(self):
        cls = self.__class__
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(5)
        return cls._executor

    def __init__(self, *args, **kwargs):
        super(UCRSpawner, self).__init__(*args, **kwargs)
        self.marathon = MarathonClient(self.marathon_host)
        self.get_state()
        self.env_keep = []  # env_keep doesn't make sense in Mesos

    @property
    def app_id(self):
        return '/%s/%s/notebook' % (self.app_prefix, self.user.name)

    def get_state(self):
        state = super(UCRSpawner, self).get_state()
        state['user_options'] = self.stored_user_options = self.user_options
        return state

    def load_state(self, state):
        super(UCRSpawner, self).load_state(state)
        self.stored_user_options = state.get('user_options', {})

    def get_health_checks(self):
        health_checks = []
        health_checks.append(MarathonHealthCheck(
            protocol='TCP',
            port_index=0,
            grace_period_seconds=300,
            interval_seconds=30,
            timeout_seconds=20,
            max_consecutive_failures=0
        ))
        return health_checks

    def get_volumes(self):
        volumes = []
        for v in self.volumes:
            mv = MarathonContainerVolume.from_json(v)
            mv.container_path = self.format_volume_name(
                mv.container_path, self)
            mv.host_path = self.format_volume_name(mv.host_path, self)
            if mv.external and 'name' in mv.external:
                mv.external['name'] = self.format_volume_name(
                    mv.external['name'], self)
            volumes.append(mv)
        return volumes

    def get_constraints(self):
        constraints = [MarathonConstraint.from_json(c) for c in self.marathon_constraints]
        unsupported = [c for c in constraints if c.operator not in ('LIKE', 'UNLIKE', 'IS')]
        if len(unsupported) > 0:
            raise UCRSpawnerException(
                'Unsupported constraint operators: %s'
                % sorted(list(set([c.operator for c in unsupported]))))
        return constraints

    def get_ip_and_port(self, app_info):
        assert len(app_info.tasks) == 1
        ip = socket.gethostbyname(app_info.tasks[0].host)
        return (ip, app_info.tasks[0].ports[0])

    @run_on_executor
    def get_app_info(self, app_id):
        try:
            app = self.marathon.get_app(app_id, embed_tasks=True)
        except NotFoundError:
            self.log.info(
                "The %s application has not been started yet", app_id)
            return None
        else:
            return app

    def _public_hub_api_url(self):
        uri = urlparse(self.hub.api_url)
        port = self.hub_port_connect if self.hub_port_connect > 0 else uri.port
        ip = self.hub_ip_connect if self.hub_ip_connect else uri.hostname
        return urlunparse((
            uri.scheme,
            '%s:%s' % (ip, port),
            uri.path,
            uri.params,
            uri.query,
            uri.fragment
        ))

    def get_args(self):
        args = super().get_args()
        if self.hub_ip_connect:
            # JupyterHub 0.7 specifies --hub-api-url
            # on the command-line, which is hard to update
            for idx, arg in enumerate(list(args)):
                if arg.startswith('--hub-api-url='):
                    args.pop(idx)
                    break
            args.append('--hub-api-url=%s' % self._public_hub_api_url())
        for idx, arg in enumerate(list(args)):
            if arg.startswith('--port='):
                args.pop(idx)
                break
        args.append('--port=$PORT_NOTEBOOK')
        return args

    def options_from_form(self, formdata):
        options = {}
        options['app_image'] = formdata['app_image'][0] or None
        if 'force_pull_image' in formdata:
            options['force_pull_image'] = formdata['force_pull_image'][0] == 'on'
        options['cpu'] = float(formdata['cpu'][0])
        options['mem'] = float(formdata['mem'][0])
        options['disk'] = float(formdata['disk'][0])
        options['gpu'] = int(formdata['gpu'][0])
        options['user_port'] = int(formdata['user_port'][0])
        return options

    @property
    def options_form(self):
        return self.options_form_template().render(
            default_app_image=self.app_image,
            app_image=self.stored_user_options.get('app_image', None) or '',
            min_cpu=0.1,
            max_cpu=self.max_cpu,
            cpu=remove_zeros(str(self.stored_user_options.get('cpu', self.cpu))),
            min_mem=32.0,
            max_mem=self.max_mem,
            mem=remove_zeros(str(self.stored_user_options.get('mem', self.mem))),
            min_disk=1000.0,
            max_disk=self.max_disk,
            disk=remove_zeros(str(self.stored_user_options.get('disk', self.disk))),
            min_gpu=0,
            max_gpu=self.max_gpu,
            gpu=self.stored_user_options.get('gpu', self.gpu),
            min_user_port=0,
            max_user_port=self.max_user_port,
            user_port=self.stored_user_options.get('user_port', self.user_port),
        )

    @lru_cache()
    def options_form_template(self):
        template_filename = 'options_form.html'
        try:
            template = self.user.settings['jinja2_env'].get_template(template_filename)
            self.log.info('Use the template from JupyterHub settings')
            return template
        except jinja2.exceptions.TemplateNotFound:
            self.log.debug('Fallback to the default template')
            return jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
            ).get_template(template_filename)

    @gen.coroutine
    def start(self):
        app_image = self.user_options.get('app_image', None) or self.app_image
        force_pull_image = self.user_options.get('force_pull_image', False)
        self.log.info("starting a Marathon app with image=%s" % app_image)

        container_params = {'image': app_image,
                            'force_pull_image': force_pull_image}
        docker_container = MarathonDockerContainer(**container_params)

        app_container = MarathonContainer(
            docker=docker_container,
            type='MESOS',
            volumes=self.get_volumes())

        cpu = self.user_options.get('cpu', None)
        mem = self.user_options.get('mem', None)
        disk = self.user_options.get('disk', None)
        gpu = self.user_options.get('gpu', None)
        user_port = self.user_options.get('user_port', None)
        self.log.info("resource: (cpu=%s, mem=%s, disk=%s, gpu=%s)" %
                      (cpu, mem, disk, gpu))

        cmd = self.cmd + self.get_args()
        env = self.get_env()

        port_definitions = [PortDefinition(
            port=0,
            protocol='tcp',
            name='notebook',
        )]

        port_definitions += [PortDefinition(port=0, protocol='tcp', name=str(i)) for i in range(user_port)]

        app_request = MarathonApp(
            id=self.app_id,
            # cmd does not use Docker image's default entrypoint
            cmd=' '.join(cmd),
            env=env,
            cpus=cpu,
            mem=mem,
            disk=disk,
            gpus=gpu,
            user=self.mesos_user,
            container=app_container,
            port_definitions=port_definitions,
            networks=[{'mode': 'host'}],
            constraints=self.get_constraints(),
            health_checks=self.get_health_checks(),
            unreachable_strategy=self.unreachable_strategy,
            backoff_seconds=5,
            backoff_factor=2,
            max_launch_delay_seconds=3600,
            instances=1
        )

        app_info = self.get_app_info(self.app_id)
        try:
            if app_info:
                self.marathon.update_app(self.app_id, app_request, force=True)
            else:
                self.marathon.create_app(self.app_id, app_request)
        except Exception as e:
            self.log.error(
                "Failed to create application for %s: %s", self.app_id, e)
            raise e

        while True:
            app_info = yield self.get_app_info(self.app_id)
            if app_info is None:
                raise UCRSpawnerException(
                    "Application %s is lost", self.app_id)
            elif app_info.instances == 0:
                raise UCRSpawnerException(
                    "No instance for application %s", self.app_id)
            elif app_info.tasks_healthy == 1:
                ip, port = self.get_ip_and_port(app_info)
                break
            yield gen.sleep(1)
        return (ip, port)

    @gen.coroutine
    def stop(self, now=False):
        try:
            self.marathon.update_app(
                self.app_id, MarathonApp(instances=0), force=True)
        except Exception as e:
            self.log.error("Failed to delete application %s", self.app_id)
            raise e
        else:
            if not now:
                while True:
                    app_info = yield self.get_app_info(self.app_id)
                    if app_info is None:
                        # Stopping application is lost, just ignore it!
                        break
                    elif len(app_info.deployments) == 0:
                        # This is the success case.
                        break
                    yield gen.sleep(1)

    @gen.coroutine
    def poll(self):
        app_info = yield self.get_app_info(self.app_id)

        if app_info is None:
            self.log.error("Application %s is lost", self.app_id)
            return 3

        for deployment in app_info.deployments:
            for current_action in deployment.current_actions:
                if current_action.action == 'StopApplication':
                    self.log.error(
                        "Application %s is shutting down", self.app_id)
                    return 1

        if app_info.tasks_healthy == 0:
            self.log.error(
                "No healthy instance for application %s", self.app_id)
            return 2

        return None

    def get_mesos_slaves(self):
        if self.mesos_master_host:
            mesos_master_host = self.mesos_master_host
        else:
            info = self.marathon.get_info()
            mesos_master_host = info.marathon_config.mesos_leader_ui_url

        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(urljoin(mesos_master_host, '/slaves'), headers=headers)
        json = response.json()
        slaves = [MesosSlave(j) for j in json['slaves']]
        for c in self.get_constraints():
            slaves = [s for s in slaves if s.match(c)]
        return slaves
