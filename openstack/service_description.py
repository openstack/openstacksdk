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

import typing as ty
import warnings

import os_service_types

from openstack import _log
from openstack import exceptions
from openstack import proxy as proxy_mod
from openstack import warnings as os_warnings

__all__ = [
    'ServiceDescription',
]

_logger = _log.setup_logging('openstack')
_service_type_manager = os_service_types.ServiceTypes()


class _ServiceDisabledProxyShim:
    def __init__(self, service_type, reason):
        self.service_type = service_type
        self.reason = reason

    def __getattr__(self, item):
        raise exceptions.ServiceDisabledException(
            "Service '{service_type}' is disabled because its configuration "
            "could not be loaded. {reason}".format(
                service_type=self.service_type, reason=self.reason or ''
            )
        )


class ServiceDescription:
    #: Dictionary of supported versions and proxy classes for that version
    supported_versions: dict[str, type[proxy_mod.Proxy]] = {}
    #: main service_type to use to find this service in the catalog
    service_type: str
    #: list of aliases this service might be registered as
    aliases: list[str] = []

    def __init__(
        self,
        service_type: str,
        supported_versions: ty.Optional[
            dict[str, type[proxy_mod.Proxy]]
        ] = None,
        aliases: ty.Optional[list[str]] = None,
    ):
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

        :param service_type: service_type to look for in the keystone catalog
        :param aliases: Optional list of aliases, if there is more than one
            name that might be used to register the service in the catalog.
        """
        self.service_type = service_type or self.service_type
        self.supported_versions = (
            supported_versions or self.supported_versions or {}
        )

        self.aliases = aliases or self.aliases
        self.all_types = [service_type] + self.aliases

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.service_type not in instance._proxies:
            proxy = self._make_proxy(instance)
            if not isinstance(proxy, _ServiceDisabledProxyShim):
                # The keystone proxy has a method called get_endpoint
                # that is about managing keystone endpoints. This is
                # unfortunate.
                try:
                    endpoint = proxy_mod.Proxy.get_endpoint(proxy)
                except IndexError:
                    # It's best not to look to closely here. This is
                    # to support old placement.
                    # There was a time when it had no status entry
                    # in its version discovery doc (OY) In this case,
                    # no endpoints get through version discovery
                    # filtering. In order to deal with that, catch
                    # the IndexError thrown by keystoneauth and
                    # set an endpoint_override for the user to the
                    # url in the catalog and try again.
                    self._set_override_from_catalog(instance.config)
                    proxy = self._make_proxy(instance)
                    endpoint = proxy_mod.Proxy.get_endpoint(proxy)
                if instance._strict_proxies:
                    self._validate_proxy(proxy, endpoint)
                proxy._connection = instance
            instance._proxies[self.service_type] = proxy
        return instance._proxies[self.service_type]

    def _set_override_from_catalog(self, config):
        override = config._get_endpoint_from_catalog(
            self.service_type,
            proxy_mod.Proxy,
        )
        config.set_service_value(
            'endpoint_override',
            self.service_type,
            override,
        )

    def _validate_proxy(self, proxy, endpoint):
        exc = None
        service_url = getattr(proxy, 'skip_discovery', None)
        try:
            # Don't go too wild for e.g. swift
            if service_url is None:
                service_url = proxy.get_endpoint_data().service_url
        except Exception as e:
            exc = e
        if exc or not endpoint or not service_url:
            raise exceptions.ServiceDiscoveryException(
                "Failed to create a working proxy for service {service_type}: "
                "{message}".format(
                    service_type=self.service_type,
                    message=exc or "No valid endpoint was discoverable.",
                )
            )

    def _make_proxy(self, instance):
        """Create a Proxy for the service in question.

        :param instance:
          The `openstack.connection.Connection` we're working with.
        """
        config = instance.config

        if not config.has_service(self.service_type):
            return _ServiceDisabledProxyShim(
                self.service_type,
                config.get_disabled_reason(self.service_type),
            )

        # We don't know anything about this service, so the user is
        # explicitly just using us for a passthrough REST adapter.
        # Skip all the lower logic.
        if not self.supported_versions:
            temp_client = config.get_session_client(
                self.service_type,
                allow_version_hack=True,
            )
            return temp_client

        # Check to see if we've got config that matches what we
        # understand in the SDK.
        version_string = config.get_api_version(self.service_type)
        endpoint_override = config.get_endpoint(self.service_type)

        # If the user doesn't give a version in config, but we only support
        # one version, then just use that version.
        if not version_string and len(self.supported_versions) == 1:
            version_string = list(self.supported_versions)[0]

        proxy_obj = None
        if endpoint_override and version_string:
            # Both endpoint override and version_string are set, we don't
            # need to do discovery - just trust the user.
            proxy_class = self.supported_versions.get(version_string[0])
            if proxy_class:
                proxy_obj = config.get_session_client(
                    self.service_type,
                    constructor=proxy_class,
                )
            else:
                warnings.warn(
                    f"The configured version, {version_string} for service "
                    f"{self.service_type} is not known or supported by "
                    f"openstacksdk. The resulting Proxy object will only "
                    f"have direct passthrough REST capabilities.",
                    category=os_warnings.UnsupportedServiceVersion,
                )
        elif endpoint_override:
            temp_adapter = config.get_session_client(self.service_type)
            api_version = temp_adapter.get_endpoint_data().api_version
            proxy_class = self.supported_versions.get(str(api_version[0]))
            if proxy_class:
                proxy_obj = config.get_session_client(
                    self.service_type,
                    constructor=proxy_class,
                )
            else:
                warnings.warn(
                    f"Service {self.service_type} has an endpoint override "
                    f"set but the version discovered at that endpoint, "
                    f"{api_version}, is not supported by openstacksdk. "
                    f"The resulting Proxy object will only have direct "
                    f"passthrough REST capabilities.",
                    category=os_warnings.UnsupportedServiceVersion,
                )

        if proxy_obj:
            if getattr(proxy_obj, 'skip_discovery', False):
                # Some services, like swift, don't have discovery. While
                # keystoneauth will behave correctly and handle such
                # scenarios, it's not super efficient as it involves trying
                # and falling back a few times.
                return proxy_obj

            data = proxy_obj.get_endpoint_data()
            if not data and instance._strict_proxies:
                raise exceptions.ServiceDiscoveryException(
                    "Failed to create a working proxy for service "
                    f"{self.service_type}: No endpoint data found."
                )

            # If we've gotten here with a proxy object it means we have
            # an endpoint_override in place. If the catalog_url and
            # service_url don't match, which can happen if there is a
            # None plugin and auth.endpoint like with standalone ironic,
            # we need to be explicit that this service has an endpoint_override
            # so that subsequent discovery calls don't get made incorrectly.
            if data.catalog_url != data.service_url:
                ep_key = '{service_type}_endpoint_override'.format(
                    service_type=self.service_type.replace('-', '_')
                )
                config.config[ep_key] = data.service_url
                proxy_obj = config.get_session_client(
                    self.service_type,
                    constructor=proxy_class,
                )
            return proxy_obj

        # Make an adapter to let discovery take over
        version_kwargs = {}
        supported_versions = sorted([int(f) for f in self.supported_versions])
        if version_string:
            version_kwargs['version'] = version_string
            if getattr(
                self.supported_versions[str(supported_versions[0])],
                'skip_discovery',
                False,
            ):
                # Requested service does not support version discovery
                # In this case it is more efficient to set the
                # endpoint_override to the current catalog endpoint value,
                # otherwise next request will try to perform discovery.

                temp_adapter = config.get_session_client(self.service_type)
                ep_override = temp_adapter.get_endpoint(skip_discovery=True)

                ep_key = '{service_type}_endpoint_override'.format(
                    service_type=self.service_type.replace('-', '_')
                )
                config.config[ep_key] = ep_override

                return config.get_session_client(
                    self.service_type,
                    allow_version_hack=True,
                    constructor=self.supported_versions[
                        str(supported_versions[0])
                    ],
                    version=version_string,
                )
        else:
            version_kwargs['min_version'] = str(supported_versions[0])
            version_kwargs['max_version'] = (
                f'{str(supported_versions[-1])}.latest'
            )

        temp_adapter = config.get_session_client(
            self.service_type, allow_version_hack=True, **version_kwargs
        )
        found_version = temp_adapter.get_api_major_version()
        if found_version is None:
            region_name = instance.config.get_region_name(self.service_type)
            if version_kwargs:
                raise exceptions.NotSupported(
                    f"The {self.service_type} service for "
                    f"{instance.name}:{region_name} exists but does not have "
                    f"any supported versions."
                )
            else:
                raise exceptions.NotSupported(
                    f"The {self.service_type} service for "
                    f"{instance.name}:{region_name} exists but no version "
                    f"was discoverable."
                )
        proxy_class = self.supported_versions.get(str(found_version[0]))
        if proxy_class:
            return config.get_session_client(
                self.service_type,
                allow_version_hack=True,
                constructor=proxy_class,
                **version_kwargs,
            )

        # No proxy_class
        # Maybe openstacksdk is being used for the passthrough
        # REST API proxy layer for an unknown service in the
        # service catalog that also doesn't have any useful
        # version discovery?
        warnings.warn(
            f"Service {self.service_type} has no discoverable version. "
            "The resulting Proxy object will only have direct "
            "passthrough REST capabilities.",
            category=os_warnings.UnsupportedServiceVersion,
        )
        return temp_adapter

    def __set__(self, instance, value):
        raise AttributeError('Service Descriptors cannot be set')

    def __delete__(self, instance):
        # NOTE(gtema) Some clouds are not very fast (or interested at all)
        # in bringing their changes upstream. If there are incompatible changes
        # downstream we need to allow overriding default implementation by
        # deleting service_type attribute of the connection and then
        # "add_service" with new implementation.
        # This is implemented explicitely not very comfortable to use
        # to show how bad it is not to contribute changes back
        for service_type in self.all_types:
            if service_type in instance._proxies:
                del instance._proxies[service_type]
