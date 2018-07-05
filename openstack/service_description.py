# Copyright 2018 Red Hat, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import importlib

import os_service_types

from openstack import _log
from openstack import proxy

__all__ = [
    'OpenStackServiceDescription',
    'ServiceDescription',
]

_logger = _log.setup_logging('openstack')
_service_type_manager = os_service_types.ServiceTypes()


class ServiceDescription(object):

    #: Proxy class for this service
    proxy_class = proxy.Proxy
    #: main service_type to use to find this service in the catalog
    service_type = None
    #: list of aliases this service might be registered as
    aliases = []

    def __init__(self, service_type, proxy_class=None, aliases=None):
        """Class describing how to interact with a REST service.

        Each service in an OpenStack cloud needs to be found by looking
        for it in the catalog. Once the endpoint is found, REST calls can
        be made, but a Proxy class and some Resource objects are needed
        to provide an object interface.

        Instances of ServiceDescription can be passed to
        `openstack.connection.Connection.add_service`, or a list can be
        passed to the `openstack.connection.Connection` constructor in
        the ``extra_services`` argument.

        All three parameters can be provided at instantation time, or
        a service-specific subclass can be used that sets the attributes
        directly.

        :param string service_type:
            service_type to look for in the keystone catalog
        :param proxy.Proxy proxy_class:
            subclass of :class:`~openstack.proxy.Proxy` implementing
            an interface for this service. Defaults to
            :class:`~openstack.proxy.Proxy` which provides REST operations
            but no additional features.
        :param list aliases:
            Optional list of aliases, if there is more than one name that might
            be used to register the service in the catalog.
        """
        self.service_type = service_type or self.service_type
        self.proxy_class = proxy_class or self.proxy_class
        if self.proxy_class:
            self._validate_proxy_class()
        self.aliases = aliases or self.aliases
        self.all_types = [service_type] + self.aliases
        self._proxy = None

    def _validate_proxy_class(self):
        if not issubclass(self.proxy_class, proxy.Proxy):
            raise TypeError(
                "{module}.{proxy_class} must inherit from Proxy".format(
                    module=self.proxy_class.__module__,
                    proxy_class=self.proxy_class.__name__))

    def get_proxy_class(self, config):
        return self.proxy_class

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.service_type not in instance._proxies:
            config = instance.config
            proxy_class = self.get_proxy_class(config)
            instance._proxies[self.service_type] = config.get_session_client(
                self.service_type,
                constructor=proxy_class,
                task_manager=instance.task_manager,
                allow_version_hack=True,
            )
            instance._proxies[self.service_type]._connection = instance
        return instance._proxies[self.service_type]

    def __set__(self, instance, value):
        raise AttributeError('Service Descriptors cannot be set')

    def __delete__(self, instance):
        raise AttributeError('Service Descriptors cannot be deleted')


class OpenStackServiceDescription(ServiceDescription):
    def __init__(self, service_filter_class, *args, **kwargs):
        """Official OpenStack ServiceDescription.

        The OpenStackServiceDescription class is a helper class for
        services listed in Service Types Authority and that are directly
        supported by openstacksdk.

        It finds the proxy_class by looking in the openstacksdk tree for
        appropriately named modules.

        :param service_filter_class:
            A subclass of :class:`~openstack.service_filter.ServiceFilter`
        """
        super(OpenStackServiceDescription, self).__init__(*args, **kwargs)
        self._service_filter_class = service_filter_class

    def get_proxy_class(self, config):
        # TODO(mordred) Replace this with proper discovery
        if self.service_type == 'block-storage':
            version_string = config.get_api_version('volume')
        else:
            version_string = config.get_api_version(self.service_type)
        version = None
        if version_string:
            version = 'v{version}'.format(version=version_string[0])
        service_filter = self._service_filter_class(version=version)
        module_name = service_filter.get_module() + "._proxy"
        module = importlib.import_module(module_name)
        return getattr(module, "Proxy")
