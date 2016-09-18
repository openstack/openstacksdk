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


from openstack.identity import identity_service
from openstack import resource2 as resource


class Trust(resource.Resource):
    resource_key = 'trust'
    resources_key = 'trusts'
    base_path = '/OS-TRUST/trusts'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'trustor_user_id', 'trustee_user_id')

    # Properties
    #: A boolean indicating whether the trust can be issued by the trustee as
    #: a regulart trust. Default is ``False``.
    allow_redelegation = resource.Body('allow_redelegation', type=bool)
    #: If ``impersonation`` is set to ``False``, then the token's ``user``
    #: attribute will represent that of the trustee. *Type: bool*
    is_impersonation = resource.Body('impersonation', type=bool)
    #: Specifies the expiration time of the trust. A trust may be revoked
    #: ahead of expiration. If the value represents a time in the past,
    #: the trust is deactivated.
    expires_at = resource.Body('expires_at')
    #: If ``impersonation`` is set to true, then the ``user`` attribute
    #: of tokens that are generated based on the trust will represent
    #: that of the trustor rather than the trustee, thus allowing the trustee
    #: to impersonate the trustor.
    #: If ``impersonation`` is set to ``False``, then the token's ``user``
    #: attribute will represent that of the trustee. *Type: bool*
    is_impersonation = resource.Body('impersonation', type=bool)
    #: Links for the trust resource.
    links = resource.Body('links')
    #: ID of the project upon which the trustor is
    #: delegating authorization. *Type: string*
    project_id = resource.Body('project_id')
    #: A role links object that includes 'next', 'previous', and self links
    #: for roles.
    role_links = resource.Body('role_links')
    #: Specifies the subset of the trustor's roles on the ``project_id``
    #: to be granted to the trustee when the token in consumed. The
    #: trustor must already be granted these roles in the project referenced
    #: by the ``project_id`` attribute. *Type: list*
    roles = resource.Body('roles')
    #: Returned with redelegated trust provides information about the
    #: predecessor in the trust chain.
    redelegated_trust_id = resource.Body('redelegated_trust_id')
    #: Redelegation count
    redelegation_count = resource.Body('redelegation_count')
    #: How many times the trust can be used to obtain a token. The value is
    #: decreased each time a token is issued through the trust. Once it
    #: reaches zero, no further tokens will be isued through the trust.
    remaining_uses = resource.Body('remaining_uses')
    #: Represents the user ID who is capable of consuming the trust.
    #: *Type: string*
    trustee_user_id = resource.Body('trustee_user_id')
    #: Represents the user ID who created the trust, and who's authorization is
    #: being delegated. *Type: string*
    trustor_user_id = resource.Body('trustor_user_id')
