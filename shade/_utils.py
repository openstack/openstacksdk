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

import time

from shade import exc


def _iterate_timeout(timeout, message):
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for 2
    seconds, and if the timeout is reached, will raise an exception
    with <message>.

    """

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        time.sleep(2)
    raise exc.OpenStackCloudTimeout(message)


def _filter_list(data, name_or_id, filters):
    """Filter a list by name/ID and arbitrary meta data.

    :param list data:
        The list of dictionary data to filter. It is expected that
        each dictionary contains an 'id', 'name' (or 'display_name')
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
            # cinder likes to be different and use display_name
            e_display_name = e.get('display_name', None)
            if str(name_or_id) in (e_id, e_name, e_display_name):
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
        The name or ID of the entity being filtered.
    :param dict filters:
        A dictionary of meta data to use for further filtering.
    """
    entities = func(name_or_id, filters)
    if not entities:
        return None
    if len(entities) > 1:
        raise exc.OpenStackCloudException(
            "Multiple matches found for %s" % name_or_id)
    return entities[0]


def normalize_nova_secgroups(groups):
    """Normalize the structure of nova security groups

    This makes security group dicts, as returned from nova, look like the
    security group dicts as returned from neutron. This does not make them
    look exactly the same, but it's pretty close.

    :param list groups: A list of security group dicts.

    :returns: A list of normalized dicts.
    """
    return [{'id': g['id'],
             'name': g['name'],
             'description': g['description'],
             'security_group_rules': [{
                 'id': r['id'],
                 'direction': 'ingress',
                 'ethertype': 'IPv4',
                 'port_range_min': r['from_port'],
                 'port_range_max': r['to_port'],
                 'protocol': r['ip_protocol'],
                 'remote_ip_prefix': r['ip_range'].get('cidr', None),
                 'security_group_id': r['parent_group_id'],
                 } for r in g['rules']]
             } for g in groups]
