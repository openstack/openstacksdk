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

    # TODO(stephenfin): It would be nice to have a hookpoint to do this
    # microversion-based request manipulation, but we don't have anything like
    # that right now
    def create(self, session, prepend_key=True, base_path=None, **params):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
            should be prepended in a resource creation request. Default to
            True.
        :param str base_path: Base part of the URI for creating resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param dict params: Additional params to pass.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, 'create')

        session = self._get_session(session)
        microversion = self._get_microversion(session)
        requires_id = (
            self.create_requires_id
            if self.create_requires_id is not None
            else self.create_method == 'PUT'
        )

        if self.create_exclude_id_from_body:
            self._body._dirty.discard("id")

        # `policy` and `rules` are added with mv=2.64. In it also
        # `policies` are removed.
        if utils.supports_microversion(session, '2.64'):
            if self.policies:
                if not self.policy and isinstance(self.policies, list):
                    self.policy = self.policies[0]
                self._body.clean(only={'policies'})
            microversion = self._max_microversion
        else:  # microversion < 2.64
            if self.rules:
                msg = (
                    "API version 2.64 is required to set rules, but "
                    "it is not available."
                )
                raise exceptions.NotSupported(msg)

            if self.policy:
                if not self.policies:
                    self.policies = [self.policy]
                self._body.clean(only={'policy'})

        if self.create_method == 'POST':
            request = self._prepare_request(
                requires_id=requires_id,
                prepend_key=prepend_key,
                base_path=base_path,
            )
            response = session.post(
                request.url,
                json=request.body,
                headers=request.headers,
                microversion=microversion,
                params=params,
            )
        else:
            raise exceptions.ResourceFailure(
                f"Invalid create method: {self.create_method}"
            )

        has_body = (
            self.has_body
            if self.create_returns_body is None
            else self.create_returns_body
        )
        self.microversion = microversion
        self._translate_response(response, has_body=has_body)
        # direct comparision to False since we need to rule out None
        if self.has_body and self.create_returns_body is False:
            # fetch the body if it's required but not returned by create
            return self.fetch(session)
        return self
