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

import queue
import string
import threading
import time

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
    return '/'.join(str(a or '').strip('/') for a in args)


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
        class AccessSaver:
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


def supports_microversion(adapter, microversion, raise_exception=False):
    """Determine if the given adapter supports the given microversion.

    Checks the min and max microversion asserted by the service and checks to
    make sure that ``min <= microversion <= max``. Current default microversion
    is taken into consideration if set and verifies that ``microversion <=
    default``.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param str microversion: String containing the desired microversion.
    :param bool raise_exception: Raise exception when requested microversion
        is not supported be the server side or is higher than the current
        default microversion.
    :returns: True if the service supports the microversion.
    :rtype: bool
    :raises: :class:`~openstack.exceptions.SDKException` when requested
        microversion is not supported.
    """

    endpoint_data = adapter.get_endpoint_data()
    if (endpoint_data.min_microversion
            and endpoint_data.max_microversion
            and discover.version_between(
                endpoint_data.min_microversion,
                endpoint_data.max_microversion,
                microversion)):
        if adapter.default_microversion is not None:
            # If default_microversion is set - evaluate
            # whether it match the expectation
            candidate = discover.normalize_version_number(
                adapter.default_microversion)
            required = discover.normalize_version_number(microversion)
            supports = discover.version_match(required, candidate)
            if raise_exception and not supports:
                raise exceptions.SDKException(
                    'Required microversion {ver} is higher than currently '
                    'selected {curr}'.format(
                        ver=microversion,
                        curr=adapter.default_microversion)
                )
            return supports
        return True
    if raise_exception:
        raise exceptions.SDKException(
            'Required microversion {ver} is not supported '
            'by the server side'.format(ver=microversion)
        )
    return False


def require_microversion(adapter, required):
    """Require microversion.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param str microversion: String containing the desired microversion.
    :raises: :class:`~openstack.exceptions.SDKException` when requested
        microversion is not supported
    """
    supports_microversion(adapter, required, raise_exception=True)


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
        if not supports_microversion(session, required):
            raise exceptions.SDKException(
                'Requested microversion is not supported by the server side '
                'or the default microversion is too low')
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


class TinyDAG:
    """Tiny DAG

    Bases on the Kahn's algorithm, and enables parallel visiting of the nodes
    (parallel execution of the workflow items).
    """

    def __init__(self, data=None):
        self._reset()
        self._lock = threading.Lock()
        if data and isinstance(data, dict):
            self.from_dict(data)

    def _reset(self):
        self._graph = dict()
        self._wait_timeout = 120

    @property
    def graph(self):
        """Get graph as adjacency dict
        """
        return self._graph

    def add_node(self, node):
        self._graph.setdefault(node, set())

    def add_edge(self, u, v):
        self._graph[u].add(v)

    def from_dict(self, data):
        self._reset()
        for k, v in data.items():
            self.add_node(k)
            for dep in v:
                self.add_edge(k, dep)

    def walk(self, timeout=None):
        """Start the walking from the beginning.
        """
        if timeout:
            self._wait_timeout = timeout
        return self

    def __iter__(self):
        self._start_traverse()
        return self

    def __next__(self):
        # Start waiting if it is expected to get something
        # (counting down from graph length to 0).
        if (self._it_cnt > 0):
            self._it_cnt -= 1
            try:
                res = self._queue.get(
                    block=True,
                    timeout=self._wait_timeout)
                return res

            except queue.Empty:
                raise exceptions.SDKException('Timeout waiting for '
                                              'cleanup task to complete')
        else:
            raise StopIteration

    def node_done(self, node):
        """Mark node as "processed" and put following items into the queue"""
        self._done.add(node)

        for v in self._graph[node]:
            self._run_in_degree[v] -= 1
            if self._run_in_degree[v] == 0:
                self._queue.put(v)

    def _start_traverse(self):
        """Initialize graph traversing"""
        self._run_in_degree = self._get_in_degree()
        self._queue = queue.Queue()
        self._done = set()
        self._it_cnt = len(self._graph)

        for k, v in self._run_in_degree.items():
            if v == 0:
                self._queue.put(k)

    def _get_in_degree(self):
        """Calculate the in_degree (count incoming) for nodes"""
        _in_degree = dict()
        _in_degree = {u: 0 for u in self._graph.keys()}
        for u in self._graph:
            for v in self._graph[u]:
                _in_degree[v] += 1

        return _in_degree

    def topological_sort(self):
        """Return the graph nodes in the topological order"""
        result = []
        for node in self:
            result.append(node)
            self.node_done(node)

        return result

    def size(self):
        return len(self._graph.keys())

    def is_complete(self):
        return len(self._done) == self.size()
