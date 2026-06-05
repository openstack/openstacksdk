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

from keystoneauth1 import adapter

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
    #: The metadata associated with the server group. This is always empty and
    #: only used for preserving compatibility.
    metadata = resource.Body('metadata')
    #: The project ID who owns the server group.
    project_id = resource.Body('project_id')
    #: The rules field, which is a dict, can be applied to the policy.
    #: Currently, only the max_server_per_host rule is supported for the
    #: anti-affinity policy. The max_server_per_host rule allows specifying how
    #: many members of the anti-affinity group can reside on the same compute
    #: host. If not specified, only one member from the same anti-affinity
    #: group can reside on a given host.
    rules = resource.Body('rules', type=dict)
    #: The user ID who owns the server group
    user_id = resource.Body('user_id')

    @classmethod
    def _transform_create_request(
        cls,
        session: adapter.Adapter,
        request: resource._Request,
        *,
        microversion: str | None,
    ) -> resource._Request:
        assert isinstance(request.body, dict)  # narrow type
        # `policy` and `rules` were added with mv=2.64; `policies` was removed.
        body = request.body.get('server_group', {})
        if utils.supports_microversion(session, '2.64'):
            if body.get('policies'):
                if not body.get('policy') and isinstance(
                    body['policies'], list
                ):
                    body['policy'] = body['policies'][0]
                body.pop('policies', None)
        else:  # microversion < 2.64
            if body.get('rules'):
                raise exceptions.NotSupported(
                    "API version 2.64 is required to set rules, but "
                    "it is not available."
                )
            if body.get('policy'):
                if not body.get('policies'):
                    body['policies'] = [body['policy']]
                body.pop('policy', None)
        return request
