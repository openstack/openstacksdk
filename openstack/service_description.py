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

import warnings

import os_service_types

from openstack import _log
from openstack import exceptions
from openstack import proxy

__all__ = [
    'ServiceDescription',
]

_logger = _log.setup_logging('openstack')
_service_type_manager = os_service_types.ServiceTypes()


class ServiceDescription(object):

    #: Dictionary of supported versions and proxy classes for that version
    supported_versions = None
    #: main service_type to use to find this service in the catalog
    service_type = None
    #: list of aliases this service might be registered as
    aliases = []

    def __init__(self, service_type, supported_versions=None, aliases=None):
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
        self.supported_versions = (
            supported_versions
            or self.supported_versions
            or {})

        self.aliases = aliases or self.aliases
        self.all_types = [service_type] + self.aliases

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.service_type not in instance._proxies:
            instance._proxies[self.service_type] = self._make_proxy(instance)
            instance._proxies[self.service_type]._connection = instance
        return instance._proxies[self.service_type]

    def _make_proxy(self, instance):
        """Create a Proxy for the service in question.

        :param instance:
          The `openstack.connection.Connection` we're working with.
        """
        config = instance.config

        # First, check to see if we've got config that matches what we
        # understand in the SDK.
        version_string = config.get_api_version(self.service_type)
        endpoint_override = config.get_endpoint(self.service_type)

        # If the user doesn't give a version in config, but we only support
        # one version, then just use that version.
        if not version_string and len(self.supported_versions) == 1:
            version_string = list(self.supported_versions)[0]

        proxy_obj = None
        if endpoint_override and version_string and self.supported_versions:
            # Both endpoint override and version_string are set, we don't
            # need to do discovery - just trust the user.
            proxy_class = self.supported_versions.get(version_string[0])
            if proxy_class:
                proxy_obj = config.get_session_client(
                    self.service_type,
                    constructor=proxy_class,
                    task_manager=instance.task_manager,
                )
            else:
                warnings.warn(
                    "The configured version, {version} for service"
                    " {service_type} is not known or supported by"
                    " openstacksdk. The resulting Proxy object will only"
                    " have direct passthrough REST capabilities.".format(
                        version=version_string,
                        service_type=self.service_type),
                    category=exceptions.UnsupportedVersionWarning)
        elif endpoint_override and self.supported_versions:
            temp_adapter = config.get_session_client(
                self.service_type
            )
            api_version = temp_adapter.get_endpoint_data().api_version
            proxy_class = self.supported_versions.get(str(api_version[0]))
            if proxy_class:
                proxy_obj = config.get_session_client(
                    self.service_type,
                    constructor=proxy_class,
                    task_manager=instance.task_manager,
                )
            else:
                warnings.warn(
                    "Service {service_type) has an endpoint override set"
                    " but the version discovered at that endpoint, {version}"
                    " is not supported by openstacksdk. The resulting Proxy"
                    " object will only have direct passthrough REST"
                    " capabilities.".format(
                        version=api_version,
                        service_type=self.service_type),
                    category=exceptions.UnsupportedVersionWarning)

        if proxy_obj:

            if getattr(proxy_obj, 'skip_discovery', False):
                # Some services, like swift, don't have discovery. While
                # keystoneauth will behave correctly and handle such
                # scenarios, it's not super efficient as it involves trying
                # and falling back a few times.
                return proxy_obj

            data = proxy_obj.get_endpoint_data()
            # If we've gotten here with a proxy object it means we have
            # an endpoint_override in place. If the catalog_url and
            # service_url don't match, which can happen if there is a
            # None plugin and auth.endpoint like with standalone ironic,
            # we need to be explicit that this service has an endpoint_override
            # so that subsequent discovery calls don't get made incorrectly.
            if data.catalog_url != data.service_url:
                ep_key = '{service_type}_endpoint_override'.format(
                    service_type=self.service_type)
                config.config[ep_key] = data.service_url
                proxy_obj = config.get_session_client(
                    self.service_type,
                    constructor=proxy_class,
                    task_manager=instance.task_manager,
                )
            return proxy_obj

        # Make an adapter to let discovery take over
        version_kwargs = {}
        if version_string:
            version_kwargs['version'] = version_string
        elif self.supported_versions:
            supported_versions = sorted([
                int(f) for f in self.supported_versions])
            version_kwargs['min_version'] = str(supported_versions[0])
            version_kwargs['max_version'] = '{version}.latest'.format(
                version=str(supported_versions[-1]))

        temp_adapter = config.get_session_client(
            self.service_type,
            constructor=proxy.Proxy,
            allow_version_hack=True,
            **version_kwargs
        )
        found_version = temp_adapter.get_api_major_version()
        if found_version is None:
            # Maybe openstacksdk is being used for the passthrough
            # REST API proxy layer for an unknown service in the
            # service catalog that also doesn't have any useful
            # version discovery?
            warnings.warn(
                "Service {service_type) has no discoverable version."
                " The resulting Proxy object will only have direct"
                " passthrough REST capabilities.".format(
                    version=api_version,
                    service_type=self.service_type),
                category=exceptions.UnsupportedVersionWarning)
            return temp_adapter
        proxy_class = self.supported_versions.get(str(found_version[0]))
        if not proxy_class:
            proxy_class = proxy.Proxy
        return config.get_session_client(
            self.service_type,
            constructor=proxy_class,
            task_manager=instance.task_manager,
            allow_version_hack=True,
            **version_kwargs
        )

    def __set__(self, instance, value):
        raise AttributeError('Service Descriptors cannot be set')

    def __delete__(self, instance):
        raise AttributeError('Service Descriptors cannot be deleted')
