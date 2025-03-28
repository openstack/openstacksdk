# Copyright (c) 2018 Red Hat, Inc.
#
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
# TODO(mordred) This is only here to ease the OSC transition

from openstack.config import cloud_region
from openstack import warnings as os_warnings

if ty.TYPE_CHECKING:
    from keystoneauth1 import discover
    from keystoneauth1 import plugin
    from keystoneauth1 import session as ks_session
    import prometheus_client

    from openstack.config import loader


class CloudConfig(cloud_region.CloudRegion):
    def __init__(
        self,
        name: str | None,
        region: str | None,
        config: dict[str, ty.Any] | None,
        force_ipv4: bool = False,
        auth_plugin: ty.Optional['plugin.BaseAuthPlugin'] = None,
        openstack_config: ty.Optional['loader.OpenStackConfig'] = None,
        session_constructor: type['ks_session.Session'] | None = None,
        app_name: str | None = None,
        app_version: str | None = None,
        session: ty.Optional['ks_session.Session'] = None,
        discovery_cache: dict[str, 'discover.Discover'] | None = None,
        extra_config: dict[str, ty.Any] | None = None,
        cache_expiration_time: int = 0,
        cache_expirations: dict[str, int] | None = None,
        cache_path: str | None = None,
        cache_class: str = 'dogpile.cache.null',
        cache_arguments: dict[str, ty.Any] | None = None,
        password_callback: cloud_region._PasswordCallback | None = None,
        statsd_host: str | None = None,
        statsd_port: str | None = None,
        statsd_prefix: str | None = None,
        # TODO(stephenfin): Add better types
        influxdb_config: dict[str, ty.Any] | None = None,
        collector_registry: ty.Optional[
            'prometheus_client.CollectorRegistry'
        ] = None,
        cache_auth: bool = False,
    ) -> None:
        warnings.warn(
            'The CloudConfig class has been deprecated in favour of '
            'CloudRegion. Please update your references.',
            os_warnings.RemovedInSDK60Warning,
        )

        self.region = region

        super().__init__(
            name,
            region,
            config,
            force_ipv4=force_ipv4,
            auth_plugin=auth_plugin,
            openstack_config=openstack_config,
            session_constructor=session_constructor,
            app_name=app_name,
            app_version=app_version,
            session=session,
            discovery_cache=discovery_cache,
            extra_config=extra_config,
            cache_expiration_time=cache_expiration_time,
            cache_expirations=cache_expirations,
            cache_path=cache_path,
            cache_class=cache_class,
            cache_arguments=cache_arguments,
            password_callback=password_callback,
            statsd_host=statsd_host,
            statsd_port=statsd_port,
            statsd_prefix=statsd_prefix,
            influxdb_config=influxdb_config,
            collector_registry=collector_registry,
            cache_auth=cache_auth,
        )
