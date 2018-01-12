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

__all__ = [
    'OpenStackServiceDescription',
    'ServiceDescription',
]

import importlib
import warnings

import os_service_types

from openstack import _log
from openstack import proxy

_logger = _log.setup_logging('openstack')
_service_type_manager = os_service_types.ServiceTypes()


def _get_all_types(service_type, aliases=None):
    # We make connection attributes for all official real type names
    # and aliases. Three services have names they were called by in
    # openstacksdk that are not covered by Service Types Authority aliases.
    # Include them here - but take heed, no additional values should ever
    # be added to this list.
    # that were only used in openstacksdk resource naming.
    LOCAL_ALIASES = {
        'baremetal': 'bare_metal',
        'block_storage': 'block_store',
        'clustering': 'cluster',
    }
    all_types = set(_service_type_manager.get_all_types(service_type))
    if aliases:
        all_types.update(aliases)
    if service_type in LOCAL_ALIASES:
        all_types.add(LOCAL_ALIASES[service_type])
    return all_types


class ServiceDescription(object):

    #: Proxy class for this service
    proxy_class = proxy.BaseProxy
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
        :param proxy.BaseProxy proxy_class:
            subclass of :class:`~openstack.proxy.BaseProxy` implementing
            an interface for this service. Defaults to
            :class:`~openstack.proxy.BaseProxy` which provides REST operations
            but no additional features.
        :param list aliases:
            Optional list of aliases, if there is more than one name that might
            be used to register the service in the catalog.
        """
        self.service_type = service_type
        self.proxy_class = proxy_class or self.proxy_class
        self.all_types = _get_all_types(service_type, aliases)

        self._validate_proxy_class()

    def _validate_proxy_class(self):
        if not issubclass(self.proxy_class, proxy.BaseProxy):
            raise TypeError(
                "{module}.{proxy_class} must inherit from BaseProxy".format(
                    module=self.proxy_class.__module__,
                    proxy_class=self.proxy_class.__name__))


class OpenStackServiceDescription(ServiceDescription):

    def __init__(self, service, config):
        """Official OpenStack ServiceDescription.

        The OpenStackServiceDescription class is a helper class for
        services listed in Service Types Authority and that are directly
        supported by openstacksdk.

        It finds the proxy_class by looking in the openstacksdk tree for
        appropriately named modules.

        :param dict service:
            A service dict as found in `os_service_types.ServiceTypes.services`
        :param openstack.config.cloud_region.CloudRegion config:
            ConfigRegion for the connection.
        """
        super(OpenStackServiceDescription, self).__init__(
            service['service_type'])
        self.config = config
        service_filter = self._get_service_filter()
        if service_filter:
            module_name = service_filter.get_module() + "._proxy"
            module = importlib.import_module(module_name)
            self.proxy_class = getattr(module, "Proxy")

    def _get_service_filter(self):
        service_filter_class = None
        for service_type in self.all_types:
            service_filter_class = self._find_service_filter_class()
            if service_filter_class:
                break
        if not service_filter_class:
            return None
        # TODO(mordred) Replace this with proper discovery
        version_string = self.config.get_api_version(self.service_type)
        version = None
        if version_string:
            version = 'v{version}'.format(version=version_string[0])
        return service_filter_class(version=version)

    def _find_service_filter_class(self):
        package_name = 'openstack.{service_type}'.format(
            service_type=self.service_type).replace('-', '_')
        module_name = self.service_type.replace('-', '_') + '_service'
        class_name = ''.join(
            [part.capitalize() for part in module_name.split('_')])
        try:
            import_name = '.'.join([package_name, module_name])
            service_filter_module = importlib.import_module(import_name)
        except ImportError as e:
            # ImportWarning is ignored by default. This warning is here
            # as an opt-in for people trying to figure out why something
            # didn't work.
            warnings.warn(
                "Could not import {service_type} service filter: {e}".format(
                    service_type=self.service_type, e=str(e)),
                ImportWarning)
            return None
        service_filter_class = getattr(service_filter_module, class_name, None)
        if not service_filter_class:
            _logger.warn(
                'Unable to find class %s in module for service %s',
                class_name, self.service_type)
            return None
        return service_filter_class
