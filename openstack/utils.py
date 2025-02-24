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

import collections.abc
import hashlib
import io
import queue
import string
import threading
import time
import typing as ty

import keystoneauth1
from keystoneauth1 import adapter as ks_adapter
from keystoneauth1 import discover

from openstack import _log
from openstack import exceptions


def urljoin(*args: ty.Optional[str]) -> str:
    """A custom version of urljoin that simply joins strings into a path.

    The real urljoin takes into account web semantics like when joining a url
    like /path this should be joined to http://host/path as it is an anchored
    link. We generally won't care about that in client.
    """
    return '/'.join(str(a or '').strip('/') for a in args)


def iterate_timeout(
    timeout: ty.Optional[int],
    message: str,
    wait: ty.Union[int, float, None] = 2,
) -> ty.Generator[int, None, None]:
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for
    wait seconds, and if the timeout is reached, will raise an exception
    with <message>.

    :param timeout: Maximum number of seconds to wait for transition. Set to
        ``None`` to wait forever.
    :param message: The message to use for the exception if the timeout is
        reached.
    :param wait: Number of seconds to wait between checks. Set to ``None``
        to use the default interval.

    :returns: None
    :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
    :raises: :class:`~openstack.exceptions.SDKException` if ``wait`` is not a
        valid float, integer or None.
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
            f"Wait value must be an int or float value. {wait!r} given instead"
        )

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        log.debug('Waiting %s seconds', wait)
        time.sleep(wait)
    raise exceptions.ResourceTimeout(message)


class _AccessSaver:
    __slots__ = ('keys',)

    def __init__(self) -> None:
        self.keys: list[str] = []

    def __getitem__(self, key: str) -> None:
        self.keys.append(key)


def get_string_format_keys(
    fmt_string: str, old_style: bool = True
) -> list[str]:
    """Gets a list of required keys from a format string

    Required mostly for parsing base_path urls for required keys, which
    use the old style string formatting.
    """
    if old_style:
        a = _AccessSaver()
        fmt_string % a

        return a.keys
    else:
        keys = []
        for t in string.Formatter().parse(fmt_string):
            if t[1] is not None:
                keys.append(t[1])
        return keys


def supports_version(
    adapter: ks_adapter.Adapter,
    version: str,
    raise_exception: bool = False,
) -> bool:
    """Determine if the given adapter supports the given version.

    Checks the version asserted by the service and ensures this matches the
    provided version. ``version`` can be a major version or a major-minor
    version

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param version: String containing the desired version.
    :param raise_exception: Raise exception when requested version
        is not supported by the server.
    :returns: ``True`` if the service supports the version, else ``False``.
    :raises: :class:`~openstack.exceptions.SDKException` when
        ``raise_exception`` is ``True`` and requested version is not supported.
    """

    def _supports_version() -> bool:
        required = discover.normalize_version_number(version)
        major_version = adapter.get_api_major_version()

        if not major_version:
            return False

        if not discover.version_match(required, major_version):
            return False

        return True

    supported = _supports_version()

    if not supported and raise_exception:
        raise exceptions.SDKException(
            f'Required version {version} is not supported by the server'
        )

    return supported


def supports_microversion(
    adapter: ks_adapter.Adapter,
    microversion: ty.Union[
        str, int, float, ty.Iterable[ty.Union[str, int, float]]
    ],
    raise_exception: bool = False,
) -> bool:
    """Determine if the given adapter supports the given microversion.

    Checks the min and max microversion asserted by the service and ensures
    ``min <= microversion <= max``. If set, the current default microversion is
    taken into consideration to ensure ``microversion <= default``.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param microversion: String containing the desired microversion.
    :param raise_exception: Raise exception when requested microversion
        is not supported by the server or is higher than the current default
        microversion.
    :returns: True if the service supports the microversion, else False.
    :raises: :class:`~openstack.exceptions.SDKException` when
        ``raise_exception`` is ``True`` and requested microversion is not
        supported.
    """
    endpoint_data = adapter.get_endpoint_data()
    if endpoint_data is None:
        if raise_exception:
            raise exceptions.SDKException('Could not retrieve endpoint data')
        return False

    if (
        endpoint_data.min_microversion
        and endpoint_data.max_microversion
        and discover.version_between(
            endpoint_data.min_microversion,
            endpoint_data.max_microversion,
            microversion,
        )
    ):
        if adapter.default_microversion is not None:
            # If default_microversion is set - evaluate
            # whether it match the expectation
            candidate = discover.normalize_version_number(
                adapter.default_microversion
            )
            required = discover.normalize_version_number(microversion)
            supports = discover.version_match(required, candidate)
            if raise_exception and not supports:
                raise exceptions.SDKException(
                    f'Required microversion {microversion} is higher than '
                    f'currently selected {adapter.default_microversion}'
                )
            return supports

        return True

    if raise_exception:
        raise exceptions.SDKException(
            f'Required microversion {microversion} is not supported '
            f'by the server side'
        )

    return False


def require_microversion(adapter: ks_adapter.Adapter, required: str) -> None:
    """Require microversion.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param str microversion: String containing the desired microversion.
    :raises: :class:`~openstack.exceptions.SDKException` when requested
        microversion is not supported
    """
    supports_microversion(adapter, required, raise_exception=True)


def pick_microversion(
    session: ks_adapter.Adapter, required: str
) -> ty.Optional[str]:
    """Get a new microversion if it is higher than session's default.

    :param session: The session to use for making this request.
    :param required: Minimum version that is required for an action.
    :return: ``required`` as a string if the ``session``'s default is too low,
        otherwise the ``session``'s default. Returns ``None`` if both
        are ``None``.
    :raises: TypeError if ``required`` is invalid.
    :raises: :class:`~openstack.exceptions.SDKException` if requested
        microversion is not supported.
    """
    required_normalized = None
    if required is not None:
        required_normalized = discover.normalize_version_number(required)

    if session.default_microversion is not None:
        default = discover.normalize_version_number(
            session.default_microversion
        )

        if required_normalized is None:
            required_normalized = default
        else:
            required_normalized = (
                default
                if discover.version_match(required_normalized, default)
                else required_normalized
            )

    if required_normalized is None:
        return None

    if not supports_microversion(session, required_normalized):
        raise exceptions.SDKException(
            'Requested microversion is not supported by the server side '
            'or the default microversion is too low'
        )
    return discover.version_to_string(required_normalized)


def maximum_supported_microversion(
    adapter: ks_adapter.Adapter,
    client_maximum: ty.Optional[str],
) -> ty.Optional[str]:
    """Determine the maximum microversion supported by both client and server.

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
        log.warning(
            'Cannot determine endpoint data for service %s',
            adapter.service_type or adapter.service_name,
        )
        return None

    if not endpoint_data.max_microversion:
        return None

    client_max = discover.normalize_version_number(client_maximum)
    server_max = discover.normalize_version_number(
        endpoint_data.max_microversion
    )

    if endpoint_data.min_microversion:
        server_min = discover.normalize_version_number(
            endpoint_data.min_microversion
        )
        if client_max < server_min:
            # NOTE(dtantsur): we may want to raise in this case, but this keeps
            # the current behavior intact.
            return None

    result = min(client_max, server_max)
    return discover.version_to_string(result)


def _hashes_up_to_date(
    md5: ty.Optional[str],
    sha256: ty.Optional[str],
    md5_key: str,
    sha256_key: str,
) -> bool:
    """Compare md5 and sha256 hashes for being up to date

    md5 and sha256 are the current values.
    md5_key and sha256_key are the previous values.
    """
    up_to_date = False
    if md5 and md5_key == md5:
        up_to_date = True
    if sha256 and sha256_key == sha256:
        up_to_date = True
    if md5 and md5_key != md5:
        up_to_date = False
    if sha256 and sha256_key != sha256:
        up_to_date = False
    return up_to_date


def _calculate_data_hashes(
    data: ty.Union[io.BufferedReader, bytes],
) -> tuple[str, str]:
    _md5 = hashlib.md5(usedforsecurity=False)
    _sha256 = hashlib.sha256()

    if isinstance(data, io.BufferedIOBase):
        for chunk in iter(lambda: data.read(8192), b''):
            _md5.update(chunk)
            _sha256.update(chunk)
    elif isinstance(data, bytes):
        _md5.update(data)
        _sha256.update(data)
    else:
        raise TypeError(
            'unsupported type for data; expected IO stream or bytes; got '
            '{type(data)}'
        )

    return _md5.hexdigest(), _sha256.hexdigest()


def _get_file_hashes(filename: str) -> tuple[str, str]:
    _md5, _sha256 = (None, None)
    with open(filename, 'rb') as file_obj:
        _md5, _sha256 = _calculate_data_hashes(file_obj)

    return _md5, _sha256


class TinyDAG:
    """Tiny DAG

    Bases on the Kahn's algorithm, and enables parallel visiting of the nodes
    (parallel execution of the workflow items).
    """

    def __init__(self) -> None:
        self._reset()
        self._lock = threading.Lock()

    def _reset(self) -> None:
        self._graph: dict[str, set[str]] = {}
        self._wait_timeout = 120

    @property
    def graph(self) -> dict[str, set[str]]:
        """Get graph as adjacency dict"""
        return self._graph

    def add_node(self, node: str) -> None:
        self._graph.setdefault(node, set())

    def add_edge(self, u: str, v: str) -> None:
        self._graph[u].add(v)

    def walk(self, timeout: ty.Optional[int] = None) -> 'TinyDAG':
        """Start the walking from the beginning."""
        if timeout:
            self._wait_timeout = timeout
        return self

    def __iter__(self) -> 'TinyDAG':
        self._start_traverse()
        return self

    def __next__(self) -> str:
        # Start waiting if it is expected to get something
        # (counting down from graph length to 0).
        if self._it_cnt > 0:
            self._it_cnt -= 1
            try:
                res = self._queue.get(block=True, timeout=self._wait_timeout)
                return res

            except queue.Empty:
                raise exceptions.SDKException(
                    'Timeout waiting for cleanup task to complete'
                )
        else:
            raise StopIteration

    def node_done(self, node: str) -> None:
        """Mark node as "processed" and put following items into the queue"""
        self._done.add(node)

        for v in self._graph[node]:
            self._run_in_degree[v] -= 1
            if self._run_in_degree[v] == 0:
                self._queue.put(v)

    def _start_traverse(self) -> None:
        """Initialize graph traversing"""
        self._run_in_degree = self._get_in_degree()
        self._queue: queue.Queue[str] = queue.Queue()
        self._done: set[str] = set()
        self._it_cnt = len(self._graph)

        for k, v in self._run_in_degree.items():
            if v == 0:
                self._queue.put(k)

    def _get_in_degree(self) -> dict[str, int]:
        """Calculate the in_degree (count incoming) for nodes"""
        _in_degree: dict[str, int] = {u: 0 for u in self._graph.keys()}
        for u in self._graph:
            for v in self._graph[u]:
                _in_degree[v] += 1

        return _in_degree

    def topological_sort(self) -> list[str]:
        """Return the graph nodes in the topological order"""
        result = []
        for node in self:
            result.append(node)
            self.node_done(node)

        return result

    def size(self) -> int:
        return len(self._graph.keys())

    def is_complete(self) -> bool:
        return len(self._done) == self.size()


# Importing Munch is a relatively expensive operation (0.3s) while we do not
# really even need much of it. Before we can rework all places where we rely on
# it we can have a reduced version.
class Munch(dict[str, ty.Any]):
    """A slightly stripped version of munch.Munch class"""

    def __init__(self, *args: ty.Any, **kwargs: ty.Any):
        self.update(*args, **kwargs)

    # only called if k not found in normal places
    def __getattr__(self, k: str) -> ty.Any:
        """Gets key if it exists, otherwise throws AttributeError."""
        try:
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k: str, v: ty.Any) -> None:
        """Sets attribute k if it exists, otherwise sets key k. A KeyError
        raised by set-item (only likely if you subclass Munch) will
        propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except Exception:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k: str) -> None:
        """Deletes attribute k if it exists, otherwise deletes key k.

        A KeyError raised by deleting the key - such as when the key is missing
        - will propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def toDict(self) -> dict[str, ty.Any]:
        """Recursively converts a munch back into a dictionary."""
        return unmunchify(self)

    @property
    def __dict__(self) -> dict[str, ty.Any]:  # type: ignore[override]
        return self.toDict()

    def __repr__(self) -> str:
        """Invertible* string-form of a Munch."""
        return f'{self.__class__.__name__}({dict.__repr__(self)})'

    def __dir__(self) -> list[str]:
        return list(self.keys())

    def __getstate__(self) -> dict[str, ty.Any]:
        """Implement a serializable interface used for pickling.
        See https://docs.python.org/3.6/library/pickle.html.
        """
        return {k: v for k, v in self.items()}

    def __setstate__(self, state: dict[str, ty.Any]) -> None:
        """Implement a serializable interface used for pickling.
        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        self.update(state)

    # TODO(stephenfin): This needs to be stricter in the types that it will
    # accept. By limiting it to the primitive types (or subclasses of same) we
    # should cover everything we (sdk) care about and will be able to type the
    # results.
    @classmethod
    def fromDict(cls, d: dict[str, ty.Any]) -> 'Munch':
        """Recursively transforms a dictionary into a Munch via copy."""
        # Munchify x, using `seen` to track object cycles
        seen: dict[int, ty.Any] = dict()

        def munchify_cycles(obj: ty.Any) -> ty.Any:
            try:
                return seen[id(obj)]
            except KeyError:
                pass

            seen[id(obj)] = partial = pre_munchify(obj)
            return post_munchify(partial, obj)

        def pre_munchify(obj: ty.Any) -> ty.Any:
            if isinstance(obj, collections.abc.Mapping):
                return cls({})
            elif isinstance(obj, list):
                return type(obj)()
            elif isinstance(obj, tuple):
                type_factory = getattr(obj, "_make", type(obj))
                return type_factory(munchify_cycles(item) for item in obj)
            else:
                return obj

        def post_munchify(partial: ty.Any, obj: ty.Any) -> ty.Any:
            if isinstance(obj, collections.abc.Mapping):
                partial.update(
                    (k, munchify_cycles(obj[k])) for k in obj.keys()
                )
            elif isinstance(obj, list):
                partial.extend(munchify_cycles(item) for item in obj)
            elif isinstance(obj, tuple):
                for item_partial, item in zip(partial, obj):
                    post_munchify(item_partial, item)

            return partial

        return ty.cast('Munch', munchify_cycles(d))

    def copy(self) -> 'Munch':
        return self.fromDict(self)

    def update(self, *args: ty.Any, **kwargs: ty.Any) -> None:
        """
        Override built-in method to call custom __setitem__ method that may
        be defined in subclasses.
        """
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def get(self, k: str, d: ty.Any = None) -> ty.Any:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        if k not in self:
            return d
        return self[k]

    def setdefault(self, k: str, d: ty.Any = None) -> ty.Any:
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        if k not in self:
            self[k] = d
        return self[k]


def munchify(x: dict[str, ty.Any], factory: type[Munch] = Munch) -> Munch:
    """Recursively transforms a dictionary into a Munch via copy."""
    return Munch.fromDict(x)


def unmunchify(x: Munch) -> dict[str, ty.Any]:
    """Recursively converts a Munch into a dictionary."""

    # Munchify x, using `seen` to track object cycles
    seen: dict[int, ty.Any] = dict()

    def unmunchify_cycles(obj: ty.Any) -> ty.Any:
        try:
            return seen[id(obj)]
        except KeyError:
            pass

        seen[id(obj)] = partial = pre_unmunchify(obj)
        return post_unmunchify(partial, obj)

    def pre_unmunchify(obj: ty.Any) -> ty.Any:
        if isinstance(obj, collections.abc.Mapping):
            return dict()
        elif isinstance(obj, list):
            return type(obj)()
        elif isinstance(obj, tuple):
            type_factory = getattr(obj, "_make", type(obj))
            return type_factory(unmunchify_cycles(item) for item in obj)
        else:
            return obj

    def post_unmunchify(partial: ty.Any, obj: ty.Any) -> ty.Any:
        if isinstance(obj, collections.abc.Mapping):
            partial.update((k, unmunchify_cycles(obj[k])) for k in obj.keys())
        elif isinstance(obj, list):
            partial.extend(unmunchify_cycles(v) for v in obj)
        elif isinstance(obj, tuple):
            for value_partial, value in zip(partial, obj):
                post_unmunchify(value_partial, value)

        return partial

    return ty.cast(dict[str, ty.Any], unmunchify_cycles(x))
