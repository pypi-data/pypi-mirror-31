from __future__ import absolute_import

import abc
import contextlib
import importlib

import pyzmp
from pyros_config import ConfigHandler

from pyros_common.exceptions import PyrosException


# TODO : cleaner design by using pyzmp.Node as delegate to make all interface explicit here...
class PyrosBase(pyzmp.Node):
    """
    Base Interface in pure python ( No ROS needed ).
    Encapsulate another process for isolated execution
    Also handles a package bound configuration (since the child process might want to reload it in its own memory space)
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 name=None,
                 interface_class=None,
                 context_manager=None,
                 args=None,
                 kwargs=None,
                 instance_path=None,
                 instance_relative_config=True,
                 root_path=None,
                 default_config=None):
        """
        :param name: name of the node
        :param interface_class: the class of the interface to instantiate (in child process)
                OR a tuple (module_name, class_name), useful if the module should be imported only in child process
                OR a tuple (package_name, module_name, class_name), usseful if the module name is relative
                The interface class should be a child of BaseInterface.
        :param context_manager: a context manager to enter when starting, and exit when the node stops
        :param args: the args to pass to the setup function (that instantiate the interface class)
        :param kwargs: the kwargs to pass to the setup function (that instantiate the interface class)
        :param instance_path: the path to the running instance of the running app. configurations and resources will be expected there.
                By default it will automatically use a suitable 'instance/' folder.
                The configuration strategy follows flask configuration strategy.
                More information there : http://flask.pocoo.org/docs/0.10/config/#instance-folders
        :param instance_relative_config: whether the configuration is relative to the instance_path (if not it will be relative to the root_path)
        :param root_path: the root_path. by default the package location.
        :param default_config: a dict containing the values to use as default configuration values
        :return:
        """
        super(PyrosBase, self).__init__(name or 'pyros', context_manager=context_manager, args=args or (), kwargs=kwargs or {})

        self.last_update = 0
        self.update_interval = 1  # seconds to wait between each update

        # we delegate config related behavior (including defaults)
        self.config_handler = ConfigHandler(
            name or 'pyros',
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
            default_config=default_config,
        )

        self.provides(self.msg_build)
        # BWCOMPAT
        self.provides(self.topic)
        self.provides(self.topics)
        #
        self.provides(self.publisher)
        self.provides(self.publishers)
        self.provides(self.subscriber)
        self.provides(self.subscribers)
        self.provides(self.service)
        self.provides(self.services)
        self.provides(self.param)
        self.provides(self.params)
        self.provides(self.setup)


        if not isinstance(interface_class, tuple) and not (
                # TODO : we should pre check all the used members are present...
                hasattr(interface_class, 'services')
                # TODO : etc.
        ):
            raise PyrosException("The interface passed to the Node is not a tuple or is missing some members to be used as an interface : {interface_class}".format(**locals()))
        else:
            self.interface_class = interface_class
        self.interface = None  # delayed interface creation
        # interface should be created in child process only to maintain isolation.
        # BUT in a context to have everything setup after returning from start() call.

    #
    # Delegating configuration management
    #

    @property
    def import_name(self):
        return self.config_handler.import_name

    @property
    def config(self):
        return self.config_handler.config

    @property
    def instance_path(self):
        return self.config_handler.instance_path

    @property
    def instance_relative_config(self):
        return self.config_handler.instance_relative_config

    @property
    def root_path(self):
        return self.config_handler.root_path

    # TODO : review API : configure and setup are similar, but on different processes, at different times...
    def configure(self, config=None):
        # We default to using a config file named after the import_name:
        config = config or self.name + '.cfg'
        self.config_handler.configure(config)
        return self

    #
    # These should match the design of PyrosClient and Protocol so we are consistent between pipe and python API
    #
    @abc.abstractmethod
    def msg_build(self, name):
        return

    # BWCOMPAT
    @abc.abstractmethod
    def topic(self, name, msg_content=None):
        return

    @abc.abstractmethod
    def topics(self):
        return

    @abc.abstractmethod
    # CAREFUL : accessing a publisher means we want to receive a message from it
    def publisher(self, name):
        return

    @abc.abstractmethod
    def publishers(self):
        return

    @abc.abstractmethod
    # CAREFUL : accessing a subscriber means we want to send message to it
    def subscriber(self, name, msg_content):
        return

    @abc.abstractmethod
    def subscribers(self):
        return

    # a simple string echo service
    @abc.abstractmethod
    def service(self, name, rqst_content=None):
        return

    @abc.abstractmethod
    def services(self):
        return

    @abc.abstractmethod
    def param(self, name, value=None):
        return

    @abc.abstractmethod
    def params(self):
        return

    def start(self, timeout=None):
        """
        Startup of the node.
        :param join: optionally wait for the process to end (default : True)
        :return: None
        """

        assert super(PyrosBase, self).start(timeout=timeout)
        # Because we currently use this to setup connection
        return self.name

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        """
        Dynamically reset the interface to expose the services / topics / params whose names are passed as args
        The interface class can be specified with a module to be dynamically imported
        :param publishers:
        :param subscribers:
        :param services:
        :param topics: BW COMPAT ONLY !
        :param params:
        :return:
        """

        #BWCOMPAT
        if kwargs.get('topics'):
            if kwargs.get('publishers'):
                kwargs['publishers'] = kwargs.get('publishers', []) + kwargs.get('topics', [])
            else:
                kwargs['publishers'] = kwargs.get('topics', [])
            if kwargs.get('subscribers'):
                kwargs['subscribers'] = kwargs.get('subscribers', []) + kwargs.get('topics', [])
            else:
                kwargs['subscribers'] = kwargs.get('topics', [])
        kwargs.pop('topics')

        # We can now import RosInterface and setup will be done ( we re in another process ).
        # TODO : context to make it cleaner (maybe use zmp.Node context ?)
        if isinstance(self.interface_class, tuple):
            m = None
            class_name = self.interface_class[-1]  # last element is always the class_name
            if len(self.interface_class) >= 3:
                # load the relative module, will raise ImportError if module cannot be loaded
                m = importlib.import_module(self.interface_class[1], self.interface_class[0])
            elif len(self.interface_class) == 2:
                # load the relative module, will raise ImportError if module cannot be loaded
                m = importlib.import_module(self.interface_class[0])
            # get the class, will raise AttributeError if class cannot be found
            self.interface_class = getattr(m, class_name)

        if not (
                # TODO : we should pre check all the used members are present...
                hasattr(self.interface_class, 'services')
                # TODO : etc.
        ):
            raise PyrosException("The interface class is missing some members to be used as an interface. Aborting Setup. {interface_class}".format(**locals()))

        self.interface = self.interface_class(*args, **kwargs)
        return self.interface

    @contextlib.contextmanager
    def child_context(self, *args, **kwargs):
        """
        Context setup first in child process, before returning from start() call in parent.
        Result is passed in as argument of update
        :return:
        """

        # Now we can extract config values
        expected_args = {
            'services': [],
            'topics': [],  # bwcompat
            'subscribers': [],
            'publishers': [],
            'params': [],
            # TODO : all of them !
        }

        ifargs = {
            arg: self.config_handler.config.get(arg.upper(), default) for arg, default in expected_args.items()
        }

        # overriding with kwargs
        ifargs.update(kwargs)

        # storing passed args in config in case of reset

        # calling setup on child context enter call
        if self.interface is None:
            #for BW compat
            # TODO : change API to use the child_context from pyzmp coprocess
            self.setup(*args, **ifargs)

        with super(PyrosBase, self).child_context(*args, **kwargs) as cctxt:
            yield cctxt

    def shutdown(self, join=True, timeout=None):
        """
        Clean shutdown of the node.
        :param join: optionally wait for the process to end (default : True)
        :return: last exitcode from update method
        """
        if self.interface is not None:
            self.interface.stop()

        return super(PyrosBase, self).shutdown(join, timeout=timeout)

    def update(self, timedelta, *args, **kwargs):
        """
        Update function to call from a looping thread.
        Note : the interface is lazily constructed here
        :param timedelta: the time past since the last update call
        """

        # TODO move time management somewhere else...
        self.last_update += timedelta
        # if shutdown we want to bypass the update_interval check
        # if shutting_down:
        #     self.interface.update(shutting_down=shutting_down)
        #     return 0  # return 0 as success since we arrived here without exception
        # else
        if self.last_update > self.update_interval:
            self.last_update = 0
            self.interface.update()

        # No return here means we need to keep looping


