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

from openstack import exceptions
from openstack import resource
from openstack import utils


class ServerGroup(resource.Resource):
    resource_key = 'server_group'
    resources_key = 'server_groups'
    base_path = '/os-server-groups'

    _query_mapping = resource.QueryParameters("all_projects")

    _max_microversion = '2.64'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    # Properties
    #: A name identifying the server group
    name = resource.Body('name')
    #: The list of policies supported by the server group (till 2.63)
    policies = resource.Body('policies')
    #: The policy field represents the name of the policy (from 2.64)
    policy = resource.Body('policy')
    #: The list of members in the server group
    member_ids = resource.Body('members')
    #: The metadata associated with the server group
    metadata = resource.Body('metadata')
    #: The project ID who owns the server group.
    project_id = resource.Body('project_id')
    #: The rules field, which is a dict, can be applied to the policy
    rules = resource.Body('rules', type=list, list_type=dict)
    #: The user ID who owns the server group
    user_id = resource.Body('user_id')

    def _get_microversion_for(self, session, action):
        """Get microversion to use for the given action.

        The base version uses :meth:`_get_microversion_for_list`.
        Subclasses can override this method if more complex logic is needed.

        :param session: :class`keystoneauth1.adapter.Adapter`
        :param action: One of "fetch", "commit", "create", "delete", "patch".
            Unused in the base implementation.
        :return: microversion as string or ``None``
        """
        if action not in ('fetch', 'commit', 'create', 'delete', 'patch'):
            raise ValueError('Invalid action: %s' % action)

        microversion = self._get_microversion_for_list(session)
        if action == 'create':
            # `policy` and `rules` are added with mv=2.64. In it also
            # `policies` are removed.
            if utils.supports_microversion(session, '2.64'):
                if self.policies:
                    if not self.policy and isinstance(self.policies, list):
                        self.policy = self.policies[0]
                    self._body.clean(only={'policies'})
                microversion = self._max_microversion
            else:
                if self.rules:
                    message = ("API version %s is required to set rules, but "
                               "it is not available.") % 2.64
                    raise exceptions.NotSupported(message)
                if self.policy:
                    if not self.policies:
                        self.policies = [self.policy]
                    self._body.clean(only={'policy'})

        return microversion
