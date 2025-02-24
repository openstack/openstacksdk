# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import fnmatch
import inspect
import ipaddress
import re
import socket
import uuid
import warnings

from decorator import decorator
import jmespath
import psutil

from openstack import _log
from openstack import exceptions
from openstack import warnings as os_warnings


def _dictify_resource(resource):
    if isinstance(resource, list):
        return [_dictify_resource(r) for r in resource]
    else:
        if hasattr(resource, 'toDict'):
            return resource.toDict()
        else:
            return resource


def _filter_list(data, name_or_id, filters):
    """Filter a list by name/ID and arbitrary meta data.

    :param list data: The list of dictionary data to filter. It is expected
        that each dictionary contains an 'id' and 'name' key if a value for
        name_or_id is given.
    :param string name_or_id: The name or ID of the entity being filtered. Can
        be a glob pattern, such as 'nb01*'.
    :param filters: A dictionary of meta data to use for further filtering.
        Elements of this dictionary may, themselves, be dictionaries. Example::

            {'last_name': 'Smith', 'other': {'gender': 'Female'}}

        OR

        A string containing a jmespath expression for further filtering.
        Invalid filters will be ignored.
    """
    # The logger is openstack.cloud.fmmatch to allow a user/operator to
    # configure logging not to communicate about fnmatch misses
    # (they shouldn't be too spammy, but one never knows)
    log = _log.setup_logging('openstack.fnmatch')
    if name_or_id:
        # name_or_id might already be unicode
        name_or_id = str(name_or_id)
        identifier_matches = []
        bad_pattern = False
        try:
            fn_reg = re.compile(fnmatch.translate(name_or_id))
        except re.error:
            # If the fnmatch re doesn't compile, then we don't care,
            # but log it in case the user DID pass a pattern but did
            # it poorly and wants to know what went wrong with their
            # search
            fn_reg = None
        for e in data:
            e_id = str(e.get('id', None))
            e_name = str(e.get('name', None))

            if (e_id and e_id == name_or_id) or (
                e_name and e_name == name_or_id
            ):
                identifier_matches.append(e)
            else:
                # Only try fnmatch if we don't match exactly
                if not fn_reg:
                    # If we don't have a pattern, skip this, but set the flag
                    # so that we log the bad pattern
                    bad_pattern = True
                    continue
                if (e_id and fn_reg.match(e_id)) or (
                    e_name and fn_reg.match(e_name)
                ):
                    identifier_matches.append(e)
        if not identifier_matches and bad_pattern:
            log.debug("Bad pattern passed to fnmatch", exc_info=True)
        data = identifier_matches

    if not filters:
        return data

    if isinstance(filters, str):
        warnings.warn(
            'Support for jmespath-style filters is deprecated and will be '
            'removed in a future release. Consider using dictionary-style '
            'filters instead.',
            os_warnings.RemovedInSDK60Warning,
        )
        return jmespath.search(filters, data)

    def _dict_filter(f, d):
        if not d:
            return False
        for key in f.keys():
            if key not in d:
                log.warning(
                    "Invalid filter: %s is not an attribute of %s.%s",
                    key,
                    e.__class__.__module__,
                    e.__class__.__qualname__,
                )
                # we intentionally skip this since the user was trying to
                # filter on _something_, but we don't know what that
                # _something_ was
                raise AttributeError(key)
            if isinstance(f[key], dict):
                if not _dict_filter(f[key], d.get(key, None)):
                    return False
            elif d.get(key, None) != f[key]:
                return False
        return True

    filtered = []
    for e in data:
        if _dict_filter(filters, e):
            filtered.append(e)
    return filtered


def _get_entity(cloud, resource, name_or_id, filters, **kwargs):
    """Return a single entity from the list returned by a given method.

    :param object cloud: The controller class (Example: the main OpenStackCloud
        object).
    :param string or callable resource: The string that identifies the resource
        to use to lookup the get_<>_by_id or search_<resource>s methods
        (Example: network) or a callable to invoke.
    :param string name_or_id: The name or ID of the entity being filtered or an
        object or dict. If this is an object/dict with an 'id' attr/key, we
        return it and bypass resource lookup.
    :param filters: A dictionary of meta data to use for further filtering.
        OR A string containing a jmespath expression for further filtering.
        Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
    """

    # Sometimes in the control flow of openstacksdk, we already have an object
    # fetched. Rather than then needing to pull the name or id out of that
    # object, pass it in here and rely on caching to prevent us from making
    # an additional call, it's simple enough to test to see if we got an
    # object and just short-circuit return it.

    if hasattr(name_or_id, 'id') or (
        isinstance(name_or_id, dict) and 'id' in name_or_id
    ):
        return name_or_id

    # If a uuid is passed short-circuit it calling the
    # get_<resource_name>_by_id method
    if getattr(cloud, 'use_direct_get', False) and _is_uuid_like(name_or_id):
        get_resource = getattr(cloud, f'get_{resource}_by_id', None)
        if get_resource:
            return get_resource(name_or_id)

    search = (
        resource
        if callable(resource)
        else getattr(cloud, f'search_{resource}s', None)
    )
    if search:
        entities = search(name_or_id, filters, **kwargs)
        if entities:
            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}"
                )
            return entities[0]
    return None


def localhost_supports_ipv6():
    """Determine whether the local host supports IPv6

    We look for the all ip addresses configured to this node, and assume that
    if any of these is IPv6 address (but not loopback or link local), this host
    has IPv6 connectivity.
    """

    for ifname, if_addrs in psutil.net_if_addrs().items():
        for if_addr in if_addrs:
            if if_addr.family != socket.AF_INET6:
                continue
            addr = ipaddress.ip_address(if_addr.address)
            if not addr.is_link_local and not addr.is_loopback:
                return True
    return False


def valid_kwargs(*valid_args):
    # This decorator checks if argument passed as **kwargs to a function are
    # present in valid_args.
    #
    # Typically, valid_kwargs is used when we want to distinguish between
    # None and omitted arguments and we still want to validate the argument
    # list.
    #
    # Example usage:
    #
    # @valid_kwargs('opt_arg1', 'opt_arg2')
    # def my_func(self, mandatory_arg1, mandatory_arg2, **kwargs):
    #   ...
    #
    @decorator
    def func_wrapper(func, *args, **kwargs):
        argspec = inspect.getfullargspec(func)
        for k in kwargs:
            if k not in argspec.args[1:] and k not in valid_args:
                raise TypeError(
                    f"{inspect.stack()[1][3]}() got an unexpected keyword argument "
                    f"'{k}'"
                )
        return func(*args, **kwargs)

    return func_wrapper


@contextlib.contextmanager
def openstacksdk_exceptions(error_message=None):
    """Context manager for dealing with openstack exceptions.

    :param string error_message: String to use for the exception message
        content on non-SDKException exception.

        Useful for avoiding wrapping SDKException exceptions
        within themselves. Code called from within the context may throw such
        exceptions without having to catch and reraise them.

        Non-SDKException exceptions thrown within the context will
        be wrapped and the exception message will be appended to the given
        error message.
    """
    try:
        yield
    except exceptions.SDKException:
        raise
    except Exception as e:
        if error_message is None:
            error_message = str(e)
        raise exceptions.SDKException(error_message)


def safe_dict_min(key, data):
    """Safely find the minimum for a given key in a list of dict objects.

    This will find the minimum integer value for specific dictionary key
    across a list of dictionaries. The values for the given key MUST be
    integers, or string representations of an integer.

    The dictionary key does not have to be present in all (or any)
    of the elements/dicts within the data set.

    :param string key: The dictionary key to search for the minimum value.
    :param list data: List of dicts to use for the data set.

    :returns: None if the field was not found in any elements, or
        the minimum value for the field otherwise.
    """
    min_value = None
    for d in data:
        if (key in d) and (d[key] is not None):
            try:
                val = int(d[key])
            except ValueError:
                raise exceptions.SDKException(
                    "Search for minimum value failed. "
                    f"Value for {key} is not an integer: {d[key]}"
                )
            if (min_value is None) or (val < min_value):
                min_value = val
    return min_value


def safe_dict_max(key, data):
    """Safely find the maximum for a given key in a list of dict objects.

    This will find the maximum integer value for specific dictionary key
    across a list of dictionaries. The values for the given key MUST be
    integers, or string representations of an integer.

    The dictionary key does not have to be present in all (or any)
    of the elements/dicts within the data set.

    :param string key: The dictionary key to search for the maximum value.
    :param list data: List of dicts to use for the data set.

    :returns: None if the field was not found in any elements, or
        the maximum value for the field otherwise.
    """
    max_value = None
    for d in data:
        if (key in d) and (d[key] is not None):
            try:
                val = int(d[key])
            except ValueError:
                raise exceptions.SDKException(
                    "Search for maximum value failed. "
                    f"Value for {key} is not an integer: {d[key]}"
                )
            if (max_value is None) or (val > max_value):
                max_value = val
    return max_value


def parse_range(value):
    """Parse a numerical range string.

    Breakdown a range expression into its operater and numerical parts.
    This expression must be a string. Valid values must be an integer string,
    optionally preceeded by one of the following operators::

        - "<"  : Less than
        - ">"  : Greater than
        - "<=" : Less than or equal to
        - ">=" : Greater than or equal to

    Some examples of valid values and function return values::

        - "1024"  : returns (None, 1024)
        - "<5"    : returns ("<", 5)
        - ">=100" : returns (">=", 100)

    :param string value: The range expression to be parsed.

    :returns: A tuple with the operator string (or None if no operator
        was given) and the integer value. None is returned if parsing failed.
    """
    if value is None:
        return None

    range_exp = re.match(r'(<|>|<=|>=){0,1}(\d+)$', value)
    if range_exp is None:
        return None

    op = range_exp.group(1)
    num = int(range_exp.group(2))
    return (op, num)


def range_filter(data, key, range_exp):
    """Filter a list by a single range expression.

    :param list data: List of dictionaries to be searched.
    :param string key: Key name to search within the data set.
    :param string range_exp: The expression describing the range of values.

    :returns: A list subset of the original data set.
    :raises: :class:`~openstack.exceptions.SDKException` on invalid range
        expressions.
    """
    filtered = []
    range_exp = str(range_exp).upper()

    if range_exp == "MIN":
        key_min = safe_dict_min(key, data)
        if key_min is None:
            return []
        for d in data:
            if int(d[key]) == key_min:
                filtered.append(d)
        return filtered
    elif range_exp == "MAX":
        key_max = safe_dict_max(key, data)
        if key_max is None:
            return []
        for d in data:
            if int(d[key]) == key_max:
                filtered.append(d)
        return filtered

    # Not looking for a min or max, so a range or exact value must
    # have been supplied.
    val_range = parse_range(range_exp)

    # If parsing the range fails, it must be a bad value.
    if val_range is None:
        raise exceptions.SDKException(f"Invalid range value: {range_exp}")

    op = val_range[0]
    if op:
        # Range matching
        for d in data:
            d_val = int(d[key])
            if op == '<':
                if d_val < val_range[1]:
                    filtered.append(d)
            elif op == '>':
                if d_val > val_range[1]:
                    filtered.append(d)
            elif op == '<=':
                if d_val <= val_range[1]:
                    filtered.append(d)
            elif op == '>=':
                if d_val >= val_range[1]:
                    filtered.append(d)
        return filtered
    else:
        # Exact number match
        for d in data:
            if int(d[key]) == val_range[1]:
                filtered.append(d)
        return filtered


def generate_patches_from_kwargs(operation, **kwargs):
    """Given a set of parameters, returns a list with the
    valid patch values.

    :param string operation: The operation to perform.
    :param list kwargs: Dict of parameters.

    :returns: A list with the right patch values.
    """
    patches = []
    for k, v in kwargs.items():
        patch = {'op': operation, 'value': v, 'path': f'/{k}'}
        patches.append(patch)
    return sorted(patches)


class FileSegment:
    """File-like object to pass to requests."""

    def __init__(self, filename, offset, length):
        self.filename = filename
        self.offset = offset
        self.length = length
        self.pos = 0
        self._file = open(filename, 'rb')
        self.seek(0)

    def tell(self):
        return self._file.tell() - self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self._file.seek(self.offset + offset, whence)
        elif whence == 1:
            self._file.seek(offset, whence)
        elif whence == 2:
            self._file.seek(self.offset + self.length - offset, 0)

    def read(self, size=-1):
        remaining = self.length - self.pos
        if remaining <= 0:
            return b''

        to_read = remaining if size < 0 else min(size, remaining)
        chunk = self._file.read(to_read)
        self.pos += len(chunk)

        return chunk

    def reset(self):
        self._file.seek(self.offset, 0)


def _format_uuid_string(string):
    return (
        string.replace('urn:', '')
        .replace('uuid:', '')
        .strip('{}')
        .replace('-', '')
        .lower()
    )


def _is_uuid_like(val):
    """Returns validation of a value as a UUID.

    :param val: Value to verify
    :type val: string
    :returns: bool

    .. versionchanged:: 1.1.1
       Support non-lowercase UUIDs.
    """
    try:
        return str(uuid.UUID(val)).replace('-', '') == _format_uuid_string(val)
    except (TypeError, ValueError, AttributeError):
        return False
