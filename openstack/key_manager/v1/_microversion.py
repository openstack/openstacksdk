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

"""Work around Barbican's header-less version discovery document.

Barbican's unversioned discovery response (``GET <endpoint>`` with no
``OpenStack-API-Version`` header) is the legacy, pre-microversion document.
It intentionally omits ``min_version``/``max_version`` for backward
compatibility with clients that predate microversions -- see the discussion
on https://review.opendev.org/c/openstack/barbican/+/1009848. That server
change is not being pursued; clients must probe instead.

Because of that, ``Adapter.get_endpoint_data()`` (and therefore
``openstack.utils.supports_microversion()`` /
``openstack.utils.maximum_supported_microversion()``) can never report a
microversion range for key-manager: both fields stay ``None`` forever, even
against a server that fully supports microversions.

python-barbicanclient hit the exact same problem and works around it by
explicitly requesting a microversion on the discovery call itself, which
makes Barbican return the *microversion* document (which always carries the
range). See ``barbicanclient/v1/client.py:_get_min_max_version``. This
module does the same thing for openstacksdk, scoped to the key_manager
proxy so it doesn't need a keystoneauth or Barbican change.

TODO(alee): ``keystoneauth1.discover.get_version_data()`` already accepts a
``version_header`` kwarg for exactly this scenario, but
``keystoneauth1.discover.Discover`` (used internally by
``Adapter.get_endpoint_data()``) never passes one through. If that's ever
threaded through, this module can go away in favour of the normal
``openstack.utils`` helpers.
"""

from typing import cast

from keystoneauth1 import adapter as ks_adapter
from keystoneauth1 import discover
from keystoneauth1 import exceptions as ks_exceptions
from keystoneauth1 import session as ks_session

#: First microversion release. Any value works for the probe below; 1.1 is
#: used because it's the lowest microversion Barbican actually understands
#: (matching python-barbicanclient).
_PROBE_MICROVERSION = '1.1'

#: Name of the attribute used to cache the probed range on the adapter.
_CACHE_ATTR = '_key_manager_microversion_range'


def _probe_microversion_range(
    adapter: ks_adapter.Adapter,
) -> tuple[str | None, str | None]:
    """Probe the server once for its key-manager microversion range.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance (the
        key_manager ``Proxy``).
    :returns: ``(min_version, max_version)`` strings, or ``(None, None)``
        if the server doesn't support microversions at all.
    """
    endpoint = adapter.get_endpoint()
    if not endpoint:
        return None, None

    try:
        # Adapter.get() is call-compatible with the Session interface that
        # get_version_data() expects (it accepts the same headers /
        # authenticated kwargs and forwards them, just with endpoint
        # filters mixed in), it's simply typed more narrowly upstream.
        raw = discover.get_version_data(
            cast(ks_session.Session, adapter),
            endpoint,
            version_header=f'key-manager {_PROBE_MICROVERSION}',
        )
    except ks_exceptions.http.NotAcceptable:
        # The server rejected the header outright: too old to understand
        # OpenStack-API-Version at all.
        return None, None

    info = raw[0]
    if info.get('status', '').upper() == 'STABLE':
        # STABLE is only returned in two cases (see
        # barbicanclient/v1/client.py:_get_min_max_version):
        # 1. the server is old enough to ignore the header entirely, or
        # 2. the server understood the header and is confirming that 1.0
        #    is both the minimum and the maximum it supports.
        # Either way, the effective range is 1.0-1.0.
        return '1.0', '1.0'

    return info.get('min_version'), info.get('max_version')


def cached_microversion_range(
    adapter: ks_adapter.Adapter,
) -> tuple[str | None, str | None]:
    """Return the probed microversion range, probing at most once.

    The result is cached on ``adapter`` itself (the key_manager ``Proxy``
    instance, which lives for the lifetime of the owning ``Connection``), so
    repeated calls -- e.g. one per resource fetch -- only
    issue the extra discovery request the first time.
    """
    cached = getattr(adapter, _CACHE_ATTR, None)
    if cached is None:
        cached = _probe_microversion_range(adapter)
        setattr(adapter, _CACHE_ATTR, cached)
    return cast(tuple[str | None, str | None], cached)


def supports_microversion(adapter: ks_adapter.Adapter, required: str) -> bool:
    """Determine whether the server supports the given microversion.

    Equivalent to ``openstack.utils.supports_microversion()``, but sourced
    from :func:`cached_microversion_range` instead of
    ``adapter.get_endpoint_data()`` -- see the module docstring for why that
    doesn't work for key-manager.

    As with ``openstack.utils.supports_microversion()``, if the adapter has
    an explicit ``default_microversion`` set (e.g. a caller deliberately
    pinning the proxy to an older version), that takes precedence over what
    the server is capable of: a server that supports 1.3 still "does not
    support" 1.3 for this adapter if it has been pinned to 1.1.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param required: String containing the desired microversion.
    :returns: True if the service supports the microversion, else False.
    """
    min_version, max_version = cached_microversion_range(adapter)
    if not min_version or not max_version:
        return False
    if not discover.version_between(min_version, max_version, required):
        return False

    if adapter.default_microversion is not None:
        candidate = discover.normalize_version_number(
            adapter.default_microversion
        )
        required_n = discover.normalize_version_number(required)
        return discover.version_match(required_n, candidate)

    return True


def maximum_supported_microversion(
    adapter: ks_adapter.Adapter,
    client_maximum: str | None,
) -> str | None:
    """Maximum microversion supported by both client and server.

    Equivalent to ``openstack.utils.maximum_supported_microversion()``, but
    sourced from :func:`cached_microversion_range` instead of
    ``adapter.get_endpoint_data()``.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param client_maximum: Maximum microversion supported by the client.
        If ``None``, ``None`` is returned.
    :returns: the maximum supported microversion as string or ``None``.
    """
    if client_maximum is None:
        return None

    min_version, max_version = cached_microversion_range(adapter)
    if not max_version:
        return None

    client_max = discover.normalize_version_number(client_maximum)
    server_max = discover.normalize_version_number(max_version)

    if min_version:
        server_min = discover.normalize_version_number(min_version)
        if client_max < server_min:
            return None

    return discover.version_to_string(min(client_max, server_max))


def get_microversion(
    adapter: ks_adapter.Adapter,
    client_maximum: str | None,
) -> str | None:
    """Negotiate microversion for a key-manager resource.

    Same logic as :meth:`openstack.resource.Resource._get_microversion`, but
    uses the probed range instead of ``adapter.get_endpoint_data()``.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param client_maximum: Resource ``_max_microversion`` (or ``None``).
    :returns: Microversion as string or ``None``.
    """
    if adapter.default_microversion:
        return adapter.default_microversion
    return maximum_supported_microversion(adapter, client_maximum)
