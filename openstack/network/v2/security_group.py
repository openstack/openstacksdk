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

from openstack.network import network_service
from openstack.network.v2 import security_group_rule as group_rules
from openstack import resource


class SecurityGroup(resource.Resource):
    resource_key = 'security_group'
    resources_key = 'security_groups'
    base_path = '/security-groups'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The security group description.
    description = resource.prop('description')
    #: The security group name.
    name = resource.prop('name')
    #: The ID of the project this security group is associated with.
    project_id = resource.prop('tenant_id')
    #: A list of
    #: :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
    #: objects. *Type: list*
    security_group_rules = resource.prop('security_group_rules')

    def __init__(self, attrs=None, loaded=False):
        super(SecurityGroup, self).__init__(attrs=attrs, loaded=loaded)
        # Convert any raw rules to SecurityGroupRule objects.
        if self.security_group_rules:
            rules = []
            for rule in self.security_group_rules:
                rules.append(group_rules.SecurityGroupRule.existing(**rule))
            self.security_group_rules = rules
