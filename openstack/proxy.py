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

# This is needed due to https://github.com/eventlet/eventlet/issues/1026 which
# nova (and possibly others) expose
from __future__ import annotations

import collections.abc
import functools
import logging
import queue
import typing as ty
import urllib
from urllib.parse import urlparse
import warnings

try:
    import simplejson

    JSONDecodeError = simplejson.scanner.JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError  # type: ignore
import iso8601
import jmespath
from keystoneauth1 import adapter
from keystoneauth1 import session

from openstack import _log
from openstack import exceptions
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings

if ty.TYPE_CHECKING:
    import influxdb as influxdb_client
    from keystoneauth1 import plugin
    import prometheus_client
    import requests
    from statsd.client import base as statsd_client

    from openstack import connection


def normalize_metric_name(name: str) -> str:
    name = name.replace('.', '_')
    name = name.replace(':', '_')
    return name


class CleanupDependency(ty.TypedDict):
    before: list[str]
    after: list[str]


class Proxy(adapter.Adapter):
    """Represents a service."""

    retriable_status_codes: list[int] | None = None
    """HTTP status codes that should be retried by default.

    The number of retries is defined by the configuration in parameters called
    ``<service-type>_status_code_retries``.
    """

    _resource_registry: dict[str, type[resource.Resource]] = {}
    """Registry of the supported resourses.

    Dictionary of resource names (key) types (value).
    """

    _connection: connection.Connection

    def __init__(
        self,
        session: session.Session,
        *,
        service_type: str | None = None,
        service_name: str | None = None,
        interface: str | None = None,
        region_name: str | None = None,
        endpoint_override: str | None = None,
        version: str | None = None,
        auth: plugin.BaseAuthPlugin | None = None,
        user_agent: str | None = None,
        connect_retries: int | None = None,
        logger: logging.Logger | None = None,
        allow: dict[str, ty.Any] | None = None,
        additional_headers: collections.abc.MutableMapping[str, str]
        | None = None,
        client_name: str | None = None,
        client_version: str | None = None,
        allow_version_hack: bool | None = None,
        global_request_id: str | None = None,
        min_version: str | None = None,
        max_version: str | None = None,
        default_microversion: str | None = None,
        status_code_retries: int | None = None,
        retriable_status_codes: list[int] | None = None,
        raise_exc: bool | None = None,
        rate_limit: float | None = None,
        concurrency: int | None = None,
        connect_retry_delay: float | None = None,
        status_code_retry_delay: float | None = None,
        # everything from here on is SDK-specific
        statsd_client: statsd_client.StatsClient | None = None,
        statsd_prefix: str | None = None,
        prometheus_counter: prometheus_client.Counter | None = None,
        prometheus_histogram: prometheus_client.Histogram | None = None,
        influxdb_config: dict[str, ty.Any] | None = None,
        influxdb_client: influxdb_client.InfluxDBClient | None = None,
    ):
        # NOTE(dtantsur): keystoneauth defaults retriable_status_codes to None,
        # override it with a class-level value.
        if retriable_status_codes is None:
            retriable_status_codes = self.retriable_status_codes

        super().__init__(
            session=session,
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name,
            endpoint_override=endpoint_override,
            version=version,
            auth=auth,
            user_agent=user_agent,
            connect_retries=connect_retries,
            logger=logger,
            allow=allow,
            additional_headers=additional_headers,
            client_name=client_name,
            client_version=client_version,
            allow_version_hack=allow_version_hack,
            global_request_id=global_request_id,
            min_version=min_version,
            max_version=max_version,
            default_microversion=default_microversion,
            status_code_retries=status_code_retries,
            retriable_status_codes=retriable_status_codes,
            raise_exc=raise_exc,
            rate_limit=rate_limit,
            concurrency=concurrency,
            connect_retry_delay=connect_retry_delay,
            status_code_retry_delay=status_code_retry_delay,
        )

        self._statsd_client = statsd_client
        self._statsd_prefix = statsd_prefix
        self._prometheus_counter = prometheus_counter
        self._prometheus_histogram = prometheus_histogram
        self._influxdb_client = influxdb_client
        self._influxdb_config = influxdb_config
        if self.service_type:
            log_name = f'openstack.{self.service_type}'
        else:
            log_name = 'openstack'
        self.log = _log.setup_logging(log_name)

    def _get_cache_key_prefix(self, url: str) -> str:
        """Calculate cache prefix for the url"""
        if not self.service_type:
            # narrow type
            raise RuntimeError('expected service_type to be set')

        name_parts = self._extract_name(
            url, self.service_type, self.session.get_project_id()
        )

        return '.'.join([self.service_type] + name_parts)

    def _invalidate_cache(
        self,
        conn: connection.Connection,
        key_prefix: str,
    ) -> None:
        """Invalidate all cache entries starting with given prefix"""
        for k in set(conn._api_cache_keys):
            if k.startswith(key_prefix):
                conn._cache.delete(k)
                conn._api_cache_keys.remove(k)

    def request(
        self,
        url: str,
        method: str,
        error_message: str | None = None,
        raise_exc: bool = False,
        connect_retries: int = 1,
        global_request_id: str | None = None,
        *args: ty.Any,
        **kwargs: ty.Any,
    ) -> requests.Response:
        conn = self._get_connection()
        if not conn:
            # narrow type
            raise RuntimeError('no connection found')

        if not global_request_id:
            # Per-request setting should take precedence
            global_request_id = conn._global_request_id

        key = None
        key_prefix = self._get_cache_key_prefix(url)
        # The caller might want to force cache bypass.
        skip_cache = kwargs.pop('skip_cache', False)
        if conn.cache_enabled:
            # Construct cache key. It consists of:
            # service.name_parts.URL.str(kwargs)
            key = '.'.join([key_prefix, url, str(kwargs)])

            # Track cache key for invalidating possibility
            conn._api_cache_keys.add(key)

        try:
            if conn.cache_enabled and not skip_cache and method == 'GET':
                # Get the object expiration time from config
                # default to 0 to disable caching for this resource type
                expiration_time = int(
                    conn._cache_expirations.get(key_prefix, 0)
                )
                # Get from cache or execute and cache
                _response = conn._cache.get_or_create(
                    key=key,
                    creator=super().request,
                    creator_args=(
                        [url, method],
                        {
                            'connect_retries': connect_retries,
                            'raise_exc': raise_exc,
                            'global_request_id': global_request_id,
                            **kwargs,
                        },
                    ),
                    expiration_time=expiration_time,
                )
                response = ty.cast('requests.Response', _response)
            else:
                # invalidate cache if we send modification request or user
                # asked for cache bypass
                self._invalidate_cache(conn, key_prefix)
                # Pass through the API request bypassing cache
                response = super().request(
                    url,
                    method,
                    connect_retries=connect_retries,
                    raise_exc=raise_exc,
                    global_request_id=global_request_id,
                    **kwargs,
                )

            for h in response.history:
                self._report_stats(h)
            self._report_stats(response)
            return response
        except Exception as e:
            # If we want metrics to be generated we also need to generate some
            # in case of exceptions as well, so that timeouts and connection
            # problems (especially when called from ansible) are being
            # generated as well.
            self._report_stats(None, url, method, e)
            raise

    @functools.lru_cache(maxsize=256)
    def _extract_name(
        self,
        url: str,
        service_type: str | None = None,
        project_id: str | None = None,
    ) -> list[str]:
        """Produce a key name to use in logging/metrics from the URL path.

        We want to be able to logic/metric sane general things, so we pull
        the url apart to generate names. The function returns a list because
        there are two different ways in which the elements want to be combined
        below (one for logging, one for statsd)

        Some examples are likely useful::

          /servers -> ['servers']
          /servers/{id} -> ['server']
          /servers/{id}/os-security-groups -> ['server', 'os-security-groups']
          /v2.0/networks.json -> ['networks']
        """
        if service_type is not None:
            warnings.warn(
                "The 'service_type' parameter is unnecesary and will be "
                "removed in a future release.",
                os_warnings.RemovedInSDK60Warning,
            )

        url_path = urllib.parse.urlparse(url).path.strip()
        # Remove / from the beginning to keep the list indexes of interesting
        # things consistent
        if url_path.startswith('/'):
            url_path = url_path[1:]

        # Special case for neutron, which puts .json on the end of urls
        if url_path.endswith('.json'):
            url_path = url_path[: -len('.json')]

        # Split url into parts and exclude potential project_id in some urls
        url_parts = [
            x
            for x in url_path.split('/')
            if (
                x != project_id
                and (
                    not project_id
                    or (project_id and x != 'AUTH_' + project_id)
                )
            )
        ]
        if url_parts[-1] == 'detail':
            # Special case detail calls
            # GET /servers/detail
            # returns ['servers', 'detail']
            name_parts = url_parts[-2:]
        else:
            # Strip leading version piece so that
            # GET /v2.0/networks
            # returns ['networks']
            if (
                url_parts[0]
                and url_parts[0][0] == 'v'
                and url_parts[0][1]
                and url_parts[0][1].isdigit()
            ):
                url_parts = url_parts[1:]
            name_parts = self._extract_name_consume_url_parts(url_parts)

        # Keystone Token fetching is a special case, so we name it "tokens"
        # NOTE(gtema): there is no metric triggered for regular authorization
        # with openstack.connect(), since it bypassed SDK and goes directly to
        # keystoneauth1. If you need to measure performance of the token
        # fetching - trigger a separate call.
        if url_path.endswith('tokens'):
            name_parts = ['tokens']

        if not name_parts:
            name_parts = ['discovery']

        # Strip out anything that's empty or None
        return [part for part in name_parts if part]

    def _extract_name_consume_url_parts(
        self, url_parts: list[str]
    ) -> list[str]:
        """Pull out every other URL portion.

        For example, ``GET /servers/{id}/os-security-groups`` returns
        ``['server', 'os-security-groups']``.
        """
        name_parts = []
        for idx in range(0, len(url_parts)):
            if not idx % 2 and url_parts[idx]:
                # If we are on first segment and it end with 's' stip this 's'
                # to differentiate LIST and GET_BY_ID
                if (
                    len(url_parts) > idx + 1
                    and url_parts[idx][-1] == 's'
                    and url_parts[idx][-2:] != 'is'
                ):
                    name_parts.append(url_parts[idx][:-1])
                else:
                    name_parts.append(url_parts[idx])

        return name_parts

    def _report_stats(
        self,
        response: requests.Response | None,
        url: str | None = None,
        method: str | None = None,
        exc: BaseException | None = None,
    ) -> None:
        self._report_stats_statsd(response, url, method, exc)
        self._report_stats_prometheus(response, url, method, exc)
        self._report_stats_influxdb(response, url, method, exc)

    def _report_stats_statsd(
        self,
        response: requests.Response | None,
        url: str | None = None,
        method: str | None = None,
        exc: BaseException | None = None,
    ) -> None:
        if not self._statsd_prefix:
            return None

        if not self._statsd_client:
            return None

        try:
            if response is not None and not url:
                url = response.request.url
            if response is not None and not method:
                method = response.request.method

            # narrow types
            assert url is not None
            assert method is not None
            assert self.service_type is not None

            name_parts = [
                normalize_metric_name(f)
                for f in self._extract_name(
                    url, self.service_type, self.session.get_project_id()
                )
            ]
            key = '.'.join(
                [
                    self._statsd_prefix,
                    normalize_metric_name(self.service_type),
                    method,
                    '_'.join(name_parts),
                ]
            )
            with self._statsd_client.pipeline() as pipe:
                if response is not None:
                    duration = int(response.elapsed.total_seconds() * 1000)
                    metric_name = f'{key}.{str(response.status_code)}'
                    pipe.timing(metric_name, duration)
                    pipe.incr(metric_name)
                    if duration > 1000:
                        pipe.incr(f'{key}.over_1000')
                elif exc is not None:
                    pipe.incr(f'{key}.failed')
                pipe.incr(f'{key}.attempted')
        except Exception:
            # We do not want errors in metric reporting ever break client
            self.log.exception("Exception reporting metrics")

    def _report_stats_prometheus(
        self,
        response: requests.Response | None,
        url: str | None = None,
        method: str | None = None,
        exc: BaseException | None = None,
    ) -> None:
        if not self._prometheus_counter:
            return None

        if not self._prometheus_histogram:
            return None

        if response is not None and not url:
            url = response.request.url
        if response is not None and not method:
            method = response.request.method
        parsed_url = urlparse(url)
        endpoint = (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"  # type: ignore[str-bytes-safe]
        )
        if response is not None:
            labels = {
                'method': method,
                'endpoint': endpoint,
                'service_type': self.service_type,
                'status_code': response.status_code,
            }
            self._prometheus_counter.labels(**labels).inc()
            self._prometheus_histogram.labels(**labels).observe(
                response.elapsed.total_seconds() * 1000
            )

    def _report_stats_influxdb(
        self,
        response: requests.Response | None,
        url: str | None = None,
        method: str | None = None,
        exc: BaseException | None = None,
    ) -> None:
        if not self._influxdb_client:
            return None

        if not self._influxdb_config:
            return None

        # NOTE(gtema): status_code is saved both as tag and field to give
        # ability showing it as a value and not only as a legend.
        # However Influx is not ok with having same name in tags and fields,
        # therefore use different names.
        if response is not None and not url:
            url = response.request.url
        if response is not None and not method:
            method = response.request.method
        tags = {
            'method': method,
            'name': '_'.join(
                [
                    normalize_metric_name(f)
                    for f in self._extract_name(
                        url, self.service_type, self.session.get_project_id()
                    )
                ]
            ),
        }
        fields = {'attempted': 1}
        if response is not None:
            fields['duration'] = int(response.elapsed.total_seconds() * 1000)
            tags['status_code'] = str(response.status_code)
            # Note(gtema): emit also status_code as a value (counter)
            fields[str(response.status_code)] = 1
            fields[f'{method}.{response.status_code}'] = 1
            # Note(gtema): status_code field itself is also very helpful on the
            # graphs to show what was the code, instead of counting its
            # occurences
            fields['status_code_val'] = response.status_code
        elif exc:
            fields['failed'] = 1
        if 'additional_metric_tags' in self._influxdb_config:
            tags.update(self._influxdb_config['additional_metric_tags'])
        measurement = (
            self._influxdb_config.get('measurement', 'openstack_api')
            if self._influxdb_config
            else 'openstack_api'
        )
        # Note(gtema) append service name into the measurement name
        measurement = f'{measurement}.{self.service_type}'
        data = [{'measurement': measurement, 'tags': tags, 'fields': fields}]
        try:
            self._influxdb_client.write_points(data)
        except Exception:
            self.log.exception('Error writing statistics to InfluxDB')

    def _get_connection(self) -> connection.Connection | None:
        """Get the Connection object associated with this Proxy.

        When the Session is created, a reference to the Connection is attached
        to the ``_sdk_connection`` attribute. We also add a reference to it
        directly on ourselves. Use one of them.
        """
        return getattr(
            self, '_connection', getattr(self.session, '_sdk_connection', None)
        )

    def _get_resource(
        self,
        resource_type: type[resource.ResourceT],
        value: None | str | resource.ResourceT | utils.Munch,
        **attrs: ty.Any,
    ) -> resource.ResourceT:
        """Get a resource object to work on

        :param resource_type: The type of resource to operate on. This should
            be a subclass of :class:`~openstack.resource.Resource` with a
            ``from_id`` method.
        :param value: The ID of a resource or an object of ``resource_type``
            class if using an existing instance, or ``utils.Munch``,
            or None to create a new instance.
        :param attrs: A dict containing arguments for forming the request
            URL, if needed.
        """
        conn = self._get_connection()
        if value is None:
            # Create a bare resource
            res = resource_type.new(connection=conn, **attrs)
        elif isinstance(value, dict) and not isinstance(
            value, resource.Resource
        ):
            res = resource_type._from_munch(value, connection=conn)
            res._update(**attrs)
        elif not isinstance(value, resource_type):
            # Create from an ID
            res = resource_type.new(id=value, connection=conn, **attrs)
        else:
            # An existing resource instance
            if not isinstance(value, resource_type):
                raise ValueError(
                    f'Expected {resource_type.__name__} but received '
                    f'{value.__class__.__name__}'
                )
            res = value
            res._update(**attrs)

        return res

    def _get_uri_attribute(
        self,
        child: resource.Resource | str,
        parent: resource.Resource | str | None,
        name: str,
    ) -> str:
        """Get a value to be associated with a URI attribute

        `child` will not be None here as it's a required argument
        on the proxy method. `parent` is allowed to be None if `child`
        is an actual resource, but when an ID is given for the child
        one must also be provided for the parent. An example of this
        is that a parent is a Server and a child is a ServerInterface.
        """
        if parent is None:
            value = getattr(child, name)
            assert isinstance(value, str)  # narrow type
            return value

        return resource.Resource._get_id(parent)

    @ty.overload
    def _find(
        self,
        resource_type: type[resource.ResourceT],
        name_or_id: str,
        ignore_missing: ty.Literal[True] = True,
        **attrs: ty.Any,
    ) -> resource.ResourceT | None: ...

    @ty.overload
    def _find(
        self,
        resource_type: type[resource.ResourceT],
        name_or_id: str,
        ignore_missing: ty.Literal[False],
        **attrs: ty.Any,
    ) -> resource.ResourceT: ...

    # excuse the duplication here: it's mypy's fault
    # https://github.com/python/mypy/issues/14764
    @ty.overload
    def _find(
        self,
        resource_type: type[resource.ResourceT],
        name_or_id: str,
        ignore_missing: bool,
        **attrs: ty.Any,
    ) -> resource.ResourceT | None: ...

    def _find(
        self,
        resource_type: type[resource.ResourceT],
        name_or_id: str,
        ignore_missing: bool = True,
        **attrs: ty.Any,
    ) -> resource.ResourceT | None:
        """Find a resource

        :param resource_type: The type of resource to find. This should be a
            :class:`~openstack.resource.Resource` subclass.
        :param name_or_id: The name or ID of a resource to find.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.find`
            method, such as query parameters.

        :returns: An instance of ``resource_type`` or None
        """
        return resource_type.find(
            self, name_or_id, ignore_missing=ignore_missing, **attrs
        )

    def _delete(
        self,
        resource_type: type[resource.ResourceT],
        value: str | resource.ResourceT | None,
        ignore_missing: bool = True,
        **attrs: ty.Any,
    ) -> resource.ResourceT | None:
        """Delete a resource

        :param resource_type: The type of resource to delete. This should be a
            :class:`~openstack.resource.Resource` subclass.
        :param value: The resource to delete. This can be the ID of a resource,
            a :class:`~openstack.resource.Resource` subclass instance, or None
            for resources that don't have their own identifier or have
            identifiers with multiple parts. If None, you must pass these other
            identifiers as kwargs.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent resource.
        :param dict attrs: Attributes to be used to form the request URL such
            as the ID of a parent resource.
        :returns: The result of the ``delete``
        :raises: ``ValueError`` if ``value`` is a
            :class:`~openstack.resource.Resource` that doesn't match
            the ``resource_type``.
            :class:`~openstack.exceptions.NotFoundException` when
            ignore_missing if ``False`` and a nonexistent resource
            is attempted to be deleted.
        """
        res = self._get_resource(resource_type, value, **attrs)

        try:
            rv = res.delete(self)
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

        return rv

    def _update(
        self,
        resource_type: type[resource.ResourceT],
        value: str | resource.ResourceT | None,
        base_path: str | None = None,
        **attrs: ty.Any,
    ) -> resource.ResourceT:
        """Update a resource

        :param resource_type: The type of resource to update. This should be a
            :class:`~openstack.resource.Resource` subclass.
        :param value: The resource to update. This can be the ID of a resource,
            a :class:`~openstack.resource.Resource` subclass instance, or None
            for resources that don't have their own identifier or have
            identifiers with multiple parts. If None, you must pass these other
            identifiers as kwargs.
        :param str base_path: Base part of the URI for updating resources, if
            different from
            :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.update`
            method to be updated. These should correspond
            to either :class:`~openstack.resource.Body`
            or :class:`~openstack.resource.Header`
            values on this resource.

        :returns: The result of the ``update``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, **attrs)
        return res.commit(self, base_path=base_path)

    def _create(
        self,
        resource_type: type[resource.ResourceT],
        base_path: str | None = None,
        **attrs: ty.Any,
    ) -> resource.ResourceT:
        """Create a resource from attributes

        :param resource_type: The type of resource to create. This should be a
            :class:`~openstack.resource.Resource` subclass.
        :param base_path: Base part of the URI for creating resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.create`
            method to be created. These should correspond
            to either :class:`~openstack.resource.Body`
            or :class:`~openstack.resource.Header`
            values on this resource.

        :returns: The result of the ``create``
        :rtype: :class:`~openstack.resource.Resource`
        """
        # Check for attributes whose names conflict with the parameters
        # specified in the method.
        conflicting_attrs = attrs.get('__conflicting_attrs', {})
        if conflicting_attrs:
            for k, v in conflicting_attrs.items():
                attrs[k] = v
            attrs.pop('__conflicting_attrs')
        conn = self._get_connection()
        res = resource_type.new(connection=conn, **attrs)
        return res.create(self, base_path=base_path)

    def _bulk_create(
        self,
        resource_type: type[resource.ResourceT],
        data: list[dict[str, ty.Any]],
        base_path: str | None = None,
    ) -> ty.Generator[resource.ResourceT, None, None]:
        """Create a resource from attributes

        :param resource_type: The type of resource to create. This should be a
            :class:`~openstack.resource.Resource` subclass.
        :param data: List of attributes dicts to be passed onto the
            :meth:`~openstack.resource.Resource.create`
            method to be created. These should correspond
            to either :class:`~openstack.resource.Body`
            or :class:`~openstack.resource.Header`
            values on this resource.
        :param str base_path: Base part of the URI for creating resources, if
            different from
            :data:`~openstack.resource.Resource.base_path`.

        :returns: A generator of Resource objects.
        :rtype: :class:`~openstack.resource.Resource`
        """
        return resource_type.bulk_create(self, data, base_path=base_path)

    def _get(
        self,
        resource_type: type[resource.ResourceT],
        value: str | resource.ResourceT | None = None,
        requires_id: bool = True,
        base_path: str | None = None,
        skip_cache: bool = False,
        **attrs: ty.Any,
    ) -> resource.ResourceT:
        """Fetch a resource

        :param resource_type: The type of resource to get. This should be a
            :class:`~openstack.resource.Resource` subclass.
        :param value: The resource to get. This can be the ID of a resource,
            a :class:`~openstack.resource.Resource` subclass instance, or None
            for resources that don't have their own identifier or have
            identifiers with multiple parts. If None, you must pass these other
            identifiers as kwargs.
        :param requires_id: Whether the resource is identified by an ID or not.
        :param base_path: Base part of the URI for fetching resources, if
            different from
            :data:`~openstack.resource.Resource.base_path`.
        :param skip_cache: A boolean indicating whether optional API
            cache should be skipped for this invocation.
        :param attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.get`
            method. These should correspond
            to either :class:`~openstack.resource.Body`
            or :class:`~openstack.resource.Header`
            values on this resource.

        :returns: The result of the ``fetch``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, **attrs)

        return res.fetch(
            self,
            requires_id=requires_id,
            base_path=base_path,
            skip_cache=skip_cache,
            error_message=f"No {resource_type.__name__} found for {value}",
        )

    def _list(
        self,
        resource_type: type[resource.ResourceT],
        paginated: bool = True,
        base_path: str | None = None,
        jmespath_filters: str | None = None,
        **attrs: ty.Any,
    ) -> ty.Generator[resource.ResourceT, None, None]:
        """List a resource

        :param resource_type: The type of resource to list. This should
            be a :class:`~openstack.resource.Resource`
            subclass with a ``from_id`` method.
        :param bool paginated: When set to ``False``, expect all of the data
            to be returned in one response. When set to
            ``True``, the resource supports data being
            returned across multiple pages.
        :param str base_path: Base part of the URI for listing resources, if
            different from
            :data:`~openstack.resource.Resource.base_path`.
        :param str jmespath_filters: A string containing a jmespath expression
            for further filtering.

        :param dict attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.list` method. These should
            correspond to either :class:`~openstack.resource.URI` values
            or appear in :data:`~openstack.resource.Resource._query_mapping`.

        :returns: A generator of Resource objects.
        :raises: ``ValueError`` if ``value`` is a
            :class:`~openstack.resource.Resource` that doesn't match
            the ``resource_type``.
        """
        # Check for attributes whose names conflict with the parameters
        # specified in the method.
        conflicting_attrs = attrs.get('__conflicting_attrs', {})
        if conflicting_attrs:
            for k, v in conflicting_attrs.items():
                attrs[k] = v
            attrs.pop('__conflicting_attrs')

        data = resource_type.list(
            self, paginated=paginated, base_path=base_path, **attrs
        )

        if jmespath_filters and isinstance(jmespath_filters, str):
            warnings.warn(
                'Support for jmespath-style filters is deprecated and will be '
                'removed in a future release.',
                os_warnings.RemovedInSDK60Warning,
            )
            return jmespath.search(jmespath_filters, data)  # type: ignore[no-any-return]

        return data

    def _head(
        self,
        resource_type: type[resource.ResourceT],
        value: str | resource.ResourceT | None = None,
        base_path: str | None = None,
        **attrs: ty.Any,
    ) -> resource.ResourceT:
        """Retrieve a resource's header

        :param resource_type: The type of resource to retrieve.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value of a specific resource to retrieve headers
            for. Can be either the ID of a resource,
            a :class:`~openstack.resource.Resource` subclass,
            or ``None``.
        :param str base_path: Base part of the URI for heading resources, if
            different from
            :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.head` method.
            These should correspond to
            :class:`~openstack.resource.URI` values.

        :returns: The result of the ``head`` call
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, **attrs)
        return res.head(self, base_path=base_path)

    def _get_cleanup_dependencies(
        self,
    ) -> dict[str, CleanupDependency] | None:
        return None

    # TODO(stephenfin): Add type for filters. We expect the created_at or
    # updated_at keys
    def _service_cleanup(
        self,
        dry_run: bool = True,
        client_status_queue: queue.Queue[resource.Resource] | None = None,
        identified_resources: dict[str, resource.Resource] | None = None,
        filters: dict[str, ty.Any] | None = None,
        resource_evaluation_fn: ty.Callable[
            [
                resource.Resource,
                dict[str, ty.Any] | None,
                dict[str, resource.Resource] | None,
            ],
            bool,
        ]
        | None = None,
        skip_resources: list[str] | None = None,
    ) -> None:
        return None

    def _service_cleanup_del_res(
        self,
        del_fn: ty.Callable[[resource.Resource], None],
        obj: resource.Resource,
        dry_run: bool = True,
        client_status_queue: queue.Queue[resource.Resource] | None = None,
        identified_resources: dict[str, resource.Resource] | None = None,
        filters: dict[str, ty.Any] | None = None,
        resource_evaluation_fn: ty.Callable[
            [
                resource.Resource,
                dict[str, ty.Any] | None,
                dict[str, resource.Resource] | None,
            ],
            bool,
        ]
        | None = None,
    ) -> bool:
        need_delete = False
        try:
            if resource_evaluation_fn and callable(resource_evaluation_fn):
                # Ask a user-provided evaluation function if we need to delete
                # the resource
                need_del = resource_evaluation_fn(
                    obj, filters, identified_resources
                )
                if isinstance(need_del, bool):
                    # Just double check function returned bool
                    need_delete = need_del
            else:
                need_delete = (
                    self._service_cleanup_resource_filters_evaluation(
                        obj, filters=filters
                    )
                )

            if need_delete:
                if client_status_queue:
                    # Put into queue for client status info
                    client_status_queue.put(obj)
                if identified_resources is not None:
                    # Put into internal dict shared between threads so that
                    # other services might know which other resources were
                    # identified
                    identified_resources[obj.id] = obj
                if not dry_run:
                    del_fn(obj)
        except Exception as e:
            self.log.exception('Cannot delete resource %s: %s', obj, str(e))
        return need_delete

    def _service_cleanup_resource_filters_evaluation(
        self,
        obj: resource.Resource,
        filters: dict[str, ty.Any] | None = None,
    ) -> bool:
        part_cond = []
        if filters is not None and isinstance(filters, dict):
            for k, v in filters.items():
                try:
                    res_val = None
                    if k == 'created_at' and hasattr(obj, 'created_at'):
                        res_val = getattr(obj, 'created_at')
                    if k == 'updated_at' and hasattr(obj, 'updated_at'):
                        res_val = getattr(obj, 'updated_at')
                    if res_val:
                        res_date = iso8601.parse_date(res_val)
                        cmp_date = iso8601.parse_date(v)
                        if res_date and cmp_date and res_date <= cmp_date:
                            part_cond.append(True)
                        else:
                            part_cond.append(False)
                    else:
                        # There are filters set, but we can't get required
                        # attribute, so skip the resource
                        self.log.debug(
                            f'Requested cleanup attribute {k} is not '
                            'available on the resource'
                        )
                        part_cond.append(False)
                except Exception:
                    self.log.exception('Error during condition evaluation')
        if all(part_cond):
            return True
        else:
            return False

    def should_skip_resource_cleanup(
        self, resource: str, skip_resources: list[str] | None = None
    ) -> bool:
        if skip_resources is None:
            return False

        if self.service_type is None:
            # to keep mypy happy - this should never happen
            return False

        resource_name = f"{self.service_type.replace('-', '_')}.{resource}"

        if resource_name in skip_resources:
            self.log.debug(
                f"Skipping resource {resource_name} in project cleanup"
            )
            return True

        return False


# TODO(stephenfin): Remove this and all users. Use of this generally indicates
# a missing Resource type.
def _json_response(
    response: requests.Response,
    error_message: str | None = None,
) -> requests.Response | ty.Any:
    """Temporary method to use to bridge from ShadeAdapter to SDK calls."""
    exceptions.raise_from_response(response, error_message=error_message)

    if not response.content:
        # This doesn't have any content
        return response

    # Some REST calls do not return json content. Don't decode it.
    content_type = response.headers.get('Content-Type')
    if not content_type or 'application/json' not in content_type:
        return response

    try:
        return response.json()
    except JSONDecodeError:
        return response
