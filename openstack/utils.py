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

import string
import time

import six

import keystoneauth1
from keystoneauth1 import discover

from openstack import _log
from openstack import exceptions


def urljoin(*args):
    """A custom version of urljoin that simply joins strings into a path.

    The real urljoin takes into account web semantics like when joining a url
    like /path this should be joined to http://host/path as it is an anchored
    link. We generally won't care about that in client.
    """
    return '/'.join(six.text_type(a or '').strip('/') for a in args)


def iterate_timeout(timeout, message, wait=2):
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for
    wait seconds, and if the timeout is reached, will raise an exception
    with <message>.

    """
    log = _log.setup_logging('openstack.iterate_timeout')

    try:
        # None as a wait winds up flowing well in the per-resource cache
        # flow. We could spread this logic around to all of the calling
        # points, but just having this treat None as "I don't have a value"
        # seems friendlier
        if wait is None:
            wait = 2
        elif wait == 0:
            # wait should be < timeout, unless timeout is None
            wait = 0.1 if timeout is None else min(0.1, timeout)
        wait = float(wait)
    except ValueError:
        raise exceptions.SDKException(
            "Wait value must be an int or float value. {wait} given"
            " instead".format(wait=wait))

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        log.debug('Waiting %s seconds', wait)
        time.sleep(wait)
    raise exceptions.ResourceTimeout(message)


def get_string_format_keys(fmt_string, old_style=True):
    """Gets a list of required keys from a format string

    Required mostly for parsing base_path urls for required keys, which
    use the old style string formatting.
    """
    if old_style:
        class AccessSaver(object):
            def __init__(self):
                self.keys = []

            def __getitem__(self, key):
                self.keys.append(key)

        a = AccessSaver()
        fmt_string % a

        return a.keys
    else:
        keys = []
        for t in string.Formatter().parse(fmt_string):
            if t[1] is not None:
                keys.append(t[1])
        return keys


def supports_microversion(adapter, microversion):
    """Determine if the given adapter supports the given microversion.

    Checks the min and max microversion asserted by the service and checks
    to make sure that ``min <= microversion <= max``.

    :param adapter:
        :class:`~keystoneauth1.adapter.Adapter` instance.
    :param str microversion:
        String containing the desired microversion.
    :returns: True if the service supports the microversion.
    :rtype: bool
    """

    endpoint_data = adapter.get_endpoint_data()
    if (endpoint_data.min_microversion
            and endpoint_data.max_microversion
            and discover.version_between(
                endpoint_data.min_microversion,
                endpoint_data.max_microversion,
                microversion)):
        return True
    return False


def pick_microversion(session, required):
    """Get a new microversion if it is higher than session's default.

    :param session: The session to use for making this request.
    :type session: :class:`~keystoneauth1.adapter.Adapter`
    :param required: Version that is required for an action.
    :type required: String or tuple or None.
    :return: ``required`` as a string if the ``session``'s default is too low,
        the ``session``'s default otherwise. Returns ``None`` of both
        are ``None``.
    :raises: TypeError if ``required`` is invalid.
    """
    if required is not None:
        required = discover.normalize_version_number(required)

    if session.default_microversion is not None:
        default = discover.normalize_version_number(
            session.default_microversion)

        if required is None:
            required = default
        else:
            required = (default if discover.version_match(required, default)
                        else required)

    if required is not None:
        return discover.version_to_string(required)


def maximum_supported_microversion(adapter, client_maximum):
    """Determinte the maximum microversion supported by both client and server.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param client_maximum: Maximum microversion supported by the client.
        If ``None``, ``None`` is returned.

    :returns: the maximum supported microversion as string or ``None``.
    """
    if client_maximum is None:
        return None

    # NOTE(dtantsur): if we cannot determine supported microversions, fall back
    # to the default one.
    try:
        endpoint_data = adapter.get_endpoint_data()
    except keystoneauth1.exceptions.discovery.DiscoveryFailure:
        endpoint_data = None

    if endpoint_data is None:
        log = _log.setup_logging('openstack')
        log.warning('Cannot determine endpoint data for service %s',
                    adapter.service_type or adapter.service_name)
        return None

    if not endpoint_data.max_microversion:
        return None

    client_max = discover.normalize_version_number(client_maximum)
    server_max = discover.normalize_version_number(
        endpoint_data.max_microversion)

    if endpoint_data.min_microversion:
        server_min = discover.normalize_version_number(
            endpoint_data.min_microversion)
        if client_max < server_min:
            # NOTE(dtantsur): we may want to raise in this case, but this keeps
            # the current behavior intact.
            return None

    result = min(client_max, server_max)
    return discover.version_to_string(result)
