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
import inspect
import netifaces
import time

from decorator import decorator
from neutronclient.common import exceptions as neutron_exc

from shade import _log
from shade import exc
from shade import meta


log = _log.setup_logging(__name__)


_decorated_methods = []


def _iterate_timeout(timeout, message, wait=2):
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for
    wait seconds, and if the timeout is reached, will raise an exception
    with <message>.

    """

    try:
        wait = float(wait)
    except ValueError:
        raise exc.OpenStackCloudException(
            "Wait value must be an int or float value. {wait} given"
            " instead".format(wait=wait))

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        log.debug('Waiting {wait} seconds'.format(wait=wait))
        time.sleep(wait)
    raise exc.OpenStackCloudTimeout(message)


def _filter_list(data, name_or_id, filters):
    """Filter a list by name/ID and arbitrary meta data.

    :param list data:
        The list of dictionary data to filter. It is expected that
        each dictionary contains an 'id' and 'name'
        key if a value for name_or_id is given.
    :param string name_or_id:
        The name or ID of the entity being filtered.
    :param dict filters:
        A dictionary of meta data to use for further filtering. Elements
        of this dictionary may, themselves, be dictionaries. Example::

            {
              'last_name': 'Smith',
              'other': {
                  'gender': 'Female'
              }
            }
    """
    if name_or_id:
        identifier_matches = []
        for e in data:
            e_id = str(e.get('id', None))
            e_name = e.get('name', None)
            if str(name_or_id) in (e_id, e_name):
                identifier_matches.append(e)
        data = identifier_matches

    if not filters:
        return data

    def _dict_filter(f, d):
        if not d:
            return False
        for key in f.keys():
            if isinstance(f[key], dict):
                if not _dict_filter(f[key], d.get(key, None)):
                    return False
            elif d.get(key, None) != f[key]:
                return False
        return True

    filtered = []
    for e in data:
        filtered.append(e)
        for key in filters.keys():
            if isinstance(filters[key], dict):
                if not _dict_filter(filters[key], e.get(key, None)):
                    filtered.pop()
                    break
            elif e.get(key, None) != filters[key]:
                filtered.pop()
                break
    return filtered


def _get_entity(func, name_or_id, filters):
    """Return a single entity from the list returned by a given method.

    :param callable func:
        A function that takes `name_or_id` and `filters` as parameters
        and returns a list of entities to filter.
    :param string name_or_id:
        The name or ID of the entity being filtered or a dict
    :param dict filters:
        A dictionary of meta data to use for further filtering.
    """
    # Sometimes in the control flow of shade, we already have an object
    # fetched. Rather than then needing to pull the name or id out of that
    # object, pass it in here and rely on caching to prevent us from making
    # an additional call, it's simple enough to test to see if we got an
    # object and just short-circuit return it.
    if hasattr(name_or_id, 'id'):
        return name_or_id
    entities = func(name_or_id, filters)
    if not entities:
        return None
    if len(entities) > 1:
        raise exc.OpenStackCloudException(
            "Multiple matches found for %s" % name_or_id)
    return entities[0]


def normalize_servers(servers, cloud_name, region_name):
    # Here instead of _utils because we need access to region and cloud
    # name from the cloud object
    ret = []
    for server in servers:
        ret.append(normalize_server(server, cloud_name, region_name))
    return ret


def normalize_server(server, cloud_name, region_name):
    server.pop('links', None)
    server['flavor'].pop('links', None)
    # OpenStack can return image as a string when you've booted
    # from volume
    if str(server['image']) != server['image']:
        server['image'].pop('links', None)

    server['region'] = region_name
    server['cloud'] = cloud_name

    az = server.get('OS-EXT-AZ:availability_zone', None)
    if az:
        server['az'] = az

    # Ensure volumes is always in the server dict, even if empty
    server['volumes'] = []

    return server


def normalize_keystone_services(services):
    """Normalize the structure of keystone services

    In keystone v2, there is a field called "service_type". In v3, it's
    "type". Just make the returned dict have both.

    :param list services: A list of keystone service dicts

    :returns: A list of normalized dicts.
    """
    ret = []
    for service in services:
        service_type = service.get('type', service.get('service_type'))
        new_service = {
            'id': service['id'],
            'name': service['name'],
            'description': service.get('description', None),
            'type': service_type,
            'service_type': service_type,
        }
        ret.append(new_service)
    return meta.obj_list_to_dict(ret)


def normalize_nova_secgroups(groups):
    """Normalize the structure of nova security groups

    This makes security group dicts, as returned from nova, look like the
    security group dicts as returned from neutron. This does not make them
    look exactly the same, but it's pretty close.

    :param list groups: A list of security group dicts.

    :returns: A list of normalized dicts.
    """
    ret = [{'id': g['id'],
            'name': g['name'],
            'description': g['description'],
            'security_group_rules': normalize_nova_secgroup_rules(g['rules'])
            } for g in groups]
    return meta.obj_list_to_dict(ret)


def normalize_nova_secgroup_rules(rules):
    """Normalize the structure of nova security group rules

    Note that nova uses -1 for non-specific port values, but neutron
    represents these with None.

    :param list rules: A list of security group rule dicts.

    :returns: A list of normalized dicts.
    """
    ret = [{'id': r['id'],
            'direction': 'ingress',
            'ethertype': 'IPv4',
            'port_range_min':
                None if r['from_port'] == -1 else r['from_port'],
            'port_range_max':
                None if r['to_port'] == -1 else r['to_port'],
            'protocol': r['ip_protocol'],
            'remote_ip_prefix': r['ip_range'].get('cidr', None),
            'security_group_id': r['parent_group_id']
            } for r in rules]
    return meta.obj_list_to_dict(ret)


def normalize_nova_floating_ips(ips):
    """Normalize the structure of Neutron floating IPs

    Unfortunately, not all the Neutron floating_ip attributes are available
    with Nova and not all Nova floating_ip attributes are available with
    Neutron.
    This function extract attributes that are common to Nova and Neutron
    floating IP resource.
    If the whole structure is needed inside shade, shade provides private
    methods that returns "original" objects (e.g. _nova_allocate_floating_ip)

    :param list ips: A list of Nova floating IPs.

    :returns:
        A list of normalized dicts with the following attributes::

        [
          {
            "id": "this-is-a-floating-ip-id",
            "fixed_ip_address": "192.0.2.10",
            "floating_ip_address": "198.51.100.10",
            "network": "this-is-a-net-or-pool-id",
            "attached": True,
            "status": "ACTIVE"
          }, ...
        ]

    """
    ret = [dict(
        id=ip['id'],
        fixed_ip_address=ip.get('fixed_ip'),
        floating_ip_address=ip['ip'],
        network=ip['pool'],
        attached=(ip.get('instance_id') is not None and
                  ip.get('instance_id') != ''),
        status='ACTIVE'  # In neutrons terms, Nova floating IPs are always
                         # ACTIVE
    ) for ip in ips]
    return meta.obj_list_to_dict(ret)


def normalize_neutron_floating_ips(ips):
    """Normalize the structure of Neutron floating IPs

    Unfortunately, not all the Neutron floating_ip attributes are available
    with Nova and not all Nova floating_ip attributes are available with
    Neutron.
    This function extract attributes that are common to Nova and Neutron
    floating IP resource.
    If the whole structure is needed inside shade, shade provides private
    methods that returns "original" objects (e.g.
    _neutron_allocate_floating_ip)

    :param list ips: A list of Neutron floating IPs.

    :returns:
        A list of normalized dicts with the following attributes::

        [
          {
            "id": "this-is-a-floating-ip-id",
            "fixed_ip_address": "192.0.2.10",
            "floating_ip_address": "198.51.100.10",
            "network": "this-is-a-net-or-pool-id",
            "attached": True,
            "status": "ACTIVE"
          }, ...
        ]

    """
    ret = [dict(
        id=ip['id'],
        fixed_ip_address=ip.get('fixed_ip_address'),
        floating_ip_address=ip['floating_ip_address'],
        network=ip['floating_network_id'],
        attached=(ip.get('port_id') is not None and
                  ip.get('port_id') != ''),
        status=ip['status']
    ) for ip in ips]
    return meta.obj_list_to_dict(ret)


def localhost_supports_ipv6():
    """Determine whether the local host supports IPv6

    We look for a default route that supports the IPv6 address family,
    and assume that if it is present, this host has globally routable
    IPv6 connectivity.
    """

    return netifaces.AF_INET6 in netifaces.gateways()['default']


def normalize_users(users):
    ret = [
        dict(
            id=user.get('id'),
            email=user.get('email'),
            name=user.get('name'),
            username=user.get('username'),
            default_project_id=user.get('default_project_id',
                                        user.get('tenantId')),
            domain_id=user.get('domain_id'),
            enabled=user.get('enabled'),
        ) for user in users
    ]
    return meta.obj_list_to_dict(ret)


def normalize_volumes(volumes):
    ret = []
    for vol in volumes:
        new_vol = vol.copy()
        name = vol.get('name', vol.get('display_name'))
        description = vol.get('description', vol.get('display_description'))
        new_vol['name'] = name
        new_vol['display_name'] = name
        new_vol['description'] = description
        new_vol['display_description'] = description
        # For some reason, cinder uses strings for bools for these fields
        for field in ('bootable', 'multiattach'):
            if field in new_vol and new_vol[field] is not None:
                if new_vol[field].lower() == 'true':
                    new_vol[field] = True
                elif new_vol[field].lower() == 'false':
                    new_vol[field] = False
        ret.append(new_vol)
    return meta.obj_list_to_dict(ret)


def normalize_domains(domains):
    ret = [
        dict(
            id=domain.get('id'),
            name=domain.get('name'),
            description=domain.get('description'),
            enabled=domain.get('enabled'),
        ) for domain in domains
    ]
    return meta.obj_list_to_dict(ret)


def normalize_groups(domains):
    """Normalize Identity groups."""
    ret = [
        dict(
            id=domain.get('id'),
            name=domain.get('name'),
            description=domain.get('description'),
            domain_id=domain.get('domain_id'),
        ) for domain in domains
    ]
    return meta.obj_list_to_dict(ret)


def normalize_role_assignments(assignments):
    """Put role_assignments into a form that works with search/get interface.

    Role assignments have the structure::

        [
            {
                "role": {
                    "id": "--role-id--"
                },
                "scope": {
                    "domain": {
                        "id": "--domain-id--"
                    }
                },
                "user": {
                    "id": "--user-id--"
                }
            },
        ]

    Which is hard to work with in the rest of our interface. Map this to be::

        [
            {
                "id": "--role-id--",
                "domain": "--domain-id--",
                "user": "--user-id--",
            }
        ]

    Scope can be "domain" or "project" and "user" can also be "group".

    :param list assignments: A list of dictionaries of role assignments.

    :returns: A list of flattened/normalized role assignment dicts.
    """
    new_assignments = []
    for assignment in assignments:
        new_val = {'id': assignment['role']['id']}
        for scope in ('project', 'domain'):
            if scope in assignment['scope']:
                new_val[scope] = assignment['scope'][scope]['id']
        for assignee in ('user', 'group'):
            if assignee in assignment:
                new_val[assignee] = assignment[assignee]['id']
        new_assignments.append(new_val)
    return new_assignments


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
        argspec = inspect.getargspec(func)
        for k in kwargs:
            if k not in argspec.args[1:] and k not in valid_args:
                raise TypeError(
                    "{f}() got an unexpected keyword argument "
                    "'{arg}'".format(f=inspect.stack()[1][3], arg=k))
        return func(*args, **kwargs)
    return func_wrapper


def cache_on_arguments(*cache_on_args, **cache_on_kwargs):
    def _inner_cache_on_arguments(func):
        def _cache_decorator(obj, *args, **kwargs):
            the_method = obj._cache.cache_on_arguments(
                *cache_on_args, **cache_on_kwargs)(
                    func.__get__(obj, type(obj)))
            return the_method(*args, **kwargs)

        def invalidate(obj, *args, **kwargs):
            return obj._cache.cache_on_arguments()(func).invalidate(
                *args, **kwargs)

        _cache_decorator.invalidate = invalidate
        _cache_decorator.func = func
        _decorated_methods.append(func.__name__)

        return _cache_decorator
    return _inner_cache_on_arguments


@contextlib.contextmanager
def neutron_exceptions(error_message):
    try:
        yield
    except neutron_exc.NotFound as e:
        raise exc.OpenStackCloudResourceNotFound(
            "{msg}: {exc}".format(msg=error_message, exc=str(e)))
    except neutron_exc.NeutronClientException as e:
        if e.status_code == 404:
            raise exc.OpenStackCloudURINotFound(
                "{msg}: {exc}".format(msg=error_message, exc=str(e)))
        else:
            raise exc.OpenStackCloudException(
                "{msg}: {exc}".format(msg=error_message, exc=str(e)))
    except Exception as e:
        raise exc.OpenStackCloudException(
            "{msg}: {exc}".format(msg=error_message, exc=str(e)))


@contextlib.contextmanager
def shade_exceptions(error_message=None):
    """Context manager for dealing with shade exceptions.

    :param string error_message: String to use for the exception message
        content on non-OpenStackCloudExceptions.

    Useful for avoiding wrapping shade OpenStackCloudException exceptions
    within themselves. Code called from within the context may throw such
    exceptions without having to catch and reraise them.

    Non-OpenStackCloudException exceptions thrown within the context will
    be wrapped and the exception message will be appended to the given error
    message.
    """
    try:
        yield
    except exc.OpenStackCloudException:
        raise
    except Exception as e:
        if error_message is None:
            error_message = str(e)
        raise exc.OpenStackCloudException(error_message)
