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

from openstack.cloud import _utils
from openstack.cloud import exc
from openstack import exceptions
from openstack.network.v2._proxy import Proxy
from openstack import proxy
from openstack import utils


class SecurityGroupCloudMixin:
    network: Proxy

    def __init__(self):
        self.secgroup_source = self.config.config['secgroup_source']

    def search_security_groups(self, name_or_id=None, filters=None):
        # `filters` could be a dict or a jmespath (str)
        groups = self.list_security_groups(
            filters=filters if isinstance(filters, dict) else None
        )
        return _utils._filter_list(groups, name_or_id, filters)

    def list_security_groups(self, filters=None):
        """List all available security groups.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of security group
            ``openstack.network.v2.security_group.SecurityGroup``.

        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if not filters:
            filters = {}

        data = []
        # Handle neutron security groups
        if self._use_neutron_secgroups():
            # pass filters dict to the list to filter as much as possible on
            # the server side
            return list(self.network.security_groups(**filters))

        # Handle nova security groups
        else:
            data = proxy._json_response(
                self.compute.get('/os-security-groups', params=filters)
            )
        return self._normalize_secgroups(
            self._get_and_munchify('security_groups', data)
        )

    def get_security_group(self, name_or_id, filters=None):
        """Get a security group by name or ID.

        :param name_or_id: Name or ID of the security group.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                    'last_name': 'Smith',
                    'other': {
                        'gender': 'Female'
                    }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A security group
            ``openstack.network.v2.security_group.SecurityGroup``
            or None if no matching security group is found.

        """
        return _utils._get_entity(self, 'security_group', name_or_id, filters)

    def get_security_group_by_id(self, id):
        """Get a security group by ID

        :param id: ID of the security group.
        :returns: A security group
            ``openstack.network.v2.security_group.SecurityGroup``.
        """
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )
        error_message = f"Error getting security group with ID {id}"
        if self._use_neutron_secgroups():
            return self.network.get_security_group(id)
        else:
            data = proxy._json_response(
                self.compute.get(f'/os-security-groups/{id}'),
                error_message=error_message,
            )
        return self._normalize_secgroup(
            self._get_and_munchify('security_group', data)
        )

    def create_security_group(
        self, name, description, project_id=None, stateful=None
    ):
        """Create a new security group

        :param string name: A name for the security group.
        :param string description: Describes the security group.
        :param string project_id:
            Specify the project ID this security group will be created
            on (admin-only).
        :param string stateful: Whether the security group is stateful or not.

        :returns: A ``openstack.network.v2.security_group.SecurityGroup``
            representing the new security group.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
            not supported on this cloud.
        """

        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        data = []
        security_group_json = {'name': name, 'description': description}
        if stateful is not None:
            security_group_json['stateful'] = stateful
        if project_id is not None:
            security_group_json['tenant_id'] = project_id
        if self._use_neutron_secgroups():
            return self.network.create_security_group(**security_group_json)
        else:
            data = proxy._json_response(
                self.compute.post(
                    '/os-security-groups',
                    json={'security_group': security_group_json},
                )
            )
        return self._normalize_secgroup(
            self._get_and_munchify('security_group', data)
        )

    def delete_security_group(self, name_or_id):
        """Delete a security group

        :param string name_or_id: The name or unique ID of the security group.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
            not supported on this cloud.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        # TODO(mordred): Let's come back and stop doing a GET before we do
        #                the delete.
        secgroup = self.get_security_group(name_or_id)
        if secgroup is None:
            self.log.debug(
                'Security group %s not found for deleting', name_or_id
            )
            return False

        if self._use_neutron_secgroups():
            self.network.delete_security_group(
                secgroup['id'], ignore_missing=False
            )
            return True

        else:
            proxy._json_response(
                self.compute.delete(
                    '/os-security-groups/{id}'.format(id=secgroup['id'])
                )
            )
            return True

    @_utils.valid_kwargs('name', 'description', 'stateful')
    def update_security_group(self, name_or_id, **kwargs):
        """Update a security group

        :param string name_or_id: Name or ID of the security group to update.
        :param string name: New name for the security group.
        :param string description: New description for the security group.

        :returns: A ``openstack.network.v2.security_group.SecurityGroup``
            describing the updated security group.

        :raises: OpenStackCloudException on operation error.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        group = self.get_security_group(name_or_id)

        if group is None:
            raise exc.OpenStackCloudException(
                "Security group %s not found." % name_or_id
            )

        if self._use_neutron_secgroups():
            return self.network.update_security_group(group['id'], **kwargs)
        else:
            for key in ('name', 'description'):
                kwargs.setdefault(key, group[key])
            data = proxy._json_response(
                self.compute.put(
                    '/os-security-groups/{id}'.format(id=group['id']),
                    json={'security_group': kwargs},
                )
            )
        return self._normalize_secgroup(
            self._get_and_munchify('security_group', data)
        )

    def create_security_group_rule(
        self,
        secgroup_name_or_id,
        port_range_min=None,
        port_range_max=None,
        protocol=None,
        remote_ip_prefix=None,
        remote_group_id=None,
        remote_address_group_id=None,
        direction='ingress',
        ethertype='IPv4',
        project_id=None,
        description=None,
    ):
        """Create a new security group rule

        :param string secgroup_name_or_id:
            The security group name or ID to associate with this security
            group rule. If a non-unique group name is given, an exception
            is raised.
        :param int port_range_min:
            The minimum port number in the range that is matched by the
            security group rule. If the protocol is TCP or UDP, this value
            must be less than or equal to the port_range_max attribute value.
            If nova is used by the cloud provider for security groups, then
            a value of None will be transformed to -1.
        :param int port_range_max:
            The maximum port number in the range that is matched by the
            security group rule. The port_range_min attribute constrains the
            port_range_max attribute. If nova is used by the cloud provider
            for security groups, then a value of None will be transformed
            to -1.
        :param string protocol:
            The protocol that is matched by the security group rule. Valid
            values are None, tcp, udp, and icmp.
        :param string remote_ip_prefix:
            The remote IP prefix to be associated with this security group
            rule. This attribute matches the specified IP prefix as the
            source IP address of the IP packet.
        :param string remote_group_id:
            The remote group ID to be associated with this security group
            rule.
        :param string remote_address_group_id:
            The remote address group ID to be associated with this security
            group rule.
        :param string direction:
            Ingress or egress: The direction in which the security group
            rule is applied. For a compute instance, an ingress security
            group rule is applied to incoming (ingress) traffic for that
            instance. An egress rule is applied to traffic leaving the
            instance.
        :param string ethertype:
            Must be IPv4 or IPv6, and addresses represented in CIDR must
            match the ingress or egress rules.
        :param string project_id:
            Specify the project ID this security group will be created
            on (admin-only).
        :param string description:
            Description of the rule, max 255 characters.
        :returns: A ``openstack.network.v2.security_group.SecurityGroup``
            representing the new security group rule.

        :raises: OpenStackCloudException on operation error.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        secgroup = self.get_security_group(secgroup_name_or_id)
        if not secgroup:
            raise exc.OpenStackCloudException(
                "Security group %s not found." % secgroup_name_or_id
            )

        if self._use_neutron_secgroups():
            # NOTE: Nova accepts -1 port numbers, but Neutron accepts None
            # as the equivalent value.
            rule_def = {
                'security_group_id': secgroup['id'],
                'port_range_min': None
                if port_range_min == -1
                else port_range_min,
                'port_range_max': None
                if port_range_max == -1
                else port_range_max,
                'protocol': protocol,
                'remote_ip_prefix': remote_ip_prefix,
                'remote_group_id': remote_group_id,
                'remote_address_group_id': remote_address_group_id,
                'direction': direction,
                'ethertype': ethertype,
            }
            if project_id is not None:
                rule_def['tenant_id'] = project_id
            if description is not None:
                rule_def["description"] = description
            return self.network.create_security_group_rule(**rule_def)
        else:
            # NOTE: Neutron accepts None for protocol. Nova does not.
            if protocol is None:
                raise exc.OpenStackCloudException('Protocol must be specified')

            if direction == 'egress':
                self.log.debug(
                    'Rule creation failed: Nova does not support egress rules'
                )
                raise exc.OpenStackCloudException(
                    'No support for egress rules'
                )

            # NOTE: Neutron accepts None for ports, but Nova requires -1
            # as the equivalent value for ICMP.
            #
            # For TCP/UDP, if both are None, Neutron allows this and Nova
            # represents this as all ports (1-65535). Nova does not accept
            # None values, so to hide this difference, we will automatically
            # convert to the full port range. If only a single port value is
            # specified, it will error as normal.
            if protocol == 'icmp':
                if port_range_min is None:
                    port_range_min = -1
                if port_range_max is None:
                    port_range_max = -1
            elif protocol in ['tcp', 'udp']:
                if port_range_min is None and port_range_max is None:
                    port_range_min = 1
                    port_range_max = 65535

            security_group_rule_dict = dict(
                security_group_rule=dict(
                    parent_group_id=secgroup['id'],
                    ip_protocol=protocol,
                    from_port=port_range_min,
                    to_port=port_range_max,
                    cidr=remote_ip_prefix,
                    group_id=remote_group_id,
                )
            )
            if project_id is not None:
                security_group_rule_dict['security_group_rule'][
                    'tenant_id'
                ] = project_id
            data = proxy._json_response(
                self.compute.post(
                    '/os-security-group-rules', json=security_group_rule_dict
                )
            )
        return self._normalize_secgroup_rule(
            self._get_and_munchify('security_group_rule', data)
        )

    def delete_security_group_rule(self, rule_id):
        """Delete a security group rule

        :param string rule_id: The unique ID of the security group rule.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
            not supported on this cloud.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if self._use_neutron_secgroups():
            self.network.delete_security_group_rule(
                rule_id, ignore_missing=False
            )
            return True

        else:
            try:
                exceptions.raise_from_response(
                    self.compute.delete(
                        '/os-security-group-rules/{id}'.format(id=rule_id)
                    )
                )
            except exc.OpenStackCloudResourceNotFound:
                return False

            return True

    def _has_secgroups(self):
        if not self.secgroup_source:
            return False
        else:
            return self.secgroup_source.lower() in ('nova', 'neutron')

    def _use_neutron_secgroups(self):
        return (
            self.has_service('network') and self.secgroup_source == 'neutron'
        )

    def _normalize_secgroups(self, groups):
        """Normalize the structure of security groups

        This makes security group dicts, as returned from nova, look like the
        security group dicts as returned from neutron. This does not make them
        look exactly the same, but it's pretty close.

        :param list groups: A list of security group dicts.

        :returns: A list of normalized dicts.
        """
        ret = []
        for group in groups:
            ret.append(self._normalize_secgroup(group))
        return ret

    # TODO(stephenfin): Remove this once we get rid of support for nova
    # secgroups
    def _normalize_secgroup(self, group):
        ret = utils.Munch()
        # Copy incoming group because of shared dicts in unittests
        group = group.copy()

        # Discard noise
        self._remove_novaclient_artifacts(group)

        rules = self._normalize_secgroup_rules(
            group.pop('security_group_rules', group.pop('rules', []))
        )
        project_id = group.pop('tenant_id', '')
        project_id = group.pop('project_id', project_id)

        ret['location'] = self._get_current_location(project_id=project_id)
        ret['id'] = group.pop('id')
        ret['name'] = group.pop('name')
        ret['security_group_rules'] = rules
        ret['description'] = group.pop('description')
        ret['properties'] = group

        if self._use_neutron_secgroups():
            ret['stateful'] = group.pop('stateful', True)

        # Backwards compat with Neutron
        if not self.strict_mode:
            ret['tenant_id'] = project_id
            ret['project_id'] = project_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)

        return ret

    # TODO(stephenfin): Remove this once we get rid of support for nova
    # secgroups
    def _normalize_secgroup_rules(self, rules):
        """Normalize the structure of nova security group rules

        Note that nova uses -1 for non-specific port values, but neutron
        represents these with None.

        :param list rules: A list of security group rule dicts.

        :returns: A list of normalized dicts.
        """
        ret = []
        for rule in rules:
            ret.append(self._normalize_secgroup_rule(rule))
        return ret

    # TODO(stephenfin): Remove this once we get rid of support for nova
    # secgroups
    def _normalize_secgroup_rule(self, rule):
        ret = utils.Munch()
        # Copy incoming rule because of shared dicts in unittests
        rule = rule.copy()

        ret['id'] = rule.pop('id')
        ret['direction'] = rule.pop('direction', 'ingress')
        ret['ethertype'] = rule.pop('ethertype', 'IPv4')
        port_range_min = rule.get(
            'port_range_min', rule.pop('from_port', None)
        )
        if port_range_min == -1:
            port_range_min = None
        if port_range_min is not None:
            port_range_min = int(port_range_min)
        ret['port_range_min'] = port_range_min
        port_range_max = rule.pop('port_range_max', rule.pop('to_port', None))
        if port_range_max == -1:
            port_range_max = None
        if port_range_min is not None:
            port_range_min = int(port_range_min)
        ret['port_range_max'] = port_range_max
        ret['protocol'] = rule.pop('protocol', rule.pop('ip_protocol', None))
        ret['remote_ip_prefix'] = rule.pop(
            'remote_ip_prefix', rule.pop('ip_range', {}).get('cidr', None)
        )
        ret['security_group_id'] = rule.pop(
            'security_group_id', rule.pop('parent_group_id', None)
        )
        ret['remote_group_id'] = rule.pop('remote_group_id', None)
        project_id = rule.pop('tenant_id', '')
        project_id = rule.pop('project_id', project_id)
        ret['location'] = self._get_current_location(project_id=project_id)
        ret['properties'] = rule

        # Backwards compat with Neutron
        if not self.strict_mode:
            ret['tenant_id'] = project_id
            ret['project_id'] = project_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)
        return ret

    def _remove_novaclient_artifacts(self, item):
        # Remove novaclient artifacts
        item.pop('links', None)
        item.pop('NAME_ATTR', None)
        item.pop('HUMAN_ID', None)
        item.pop('human_id', None)
        item.pop('request_ids', None)
        item.pop('x_openstack_request_ids', None)
