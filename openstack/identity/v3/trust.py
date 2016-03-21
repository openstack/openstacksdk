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


from openstack import format
from openstack.identity import identity_service
from openstack import resource


class Trust(resource.Resource):
    resource_key = 'trust'
    resources_key = 'trusts'
    base_path = '/OS-TRUST/trusts'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True
    allow_retrieve = True

    # Properties
    #: ID of the project upon which the trustor is
    #: delegating authorization. *Type: string*
    project_id = resource.prop('project_id')
    #: Specifies the expiration time of the trust. A trust may be revoked
    #: ahead of expiration. If the value represents a time in the past,
    #: the trust is deactivated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    expires_at = resource.prop('expires_at', type=format.ISO8601)
    #: ID of the trust object. *Type: string*
    id = resource.prop('id')
    #: If ``impersonation`` is set to true, then the ``user`` attribute
    #: of tokens that are generated based on the trust will represent
    #: that of the trustor rather than the trustee, thus allowing the trustee
    #: to impersonate the trustor.
    #: If ``impersonation`` is set to ``False``, then the token's ``user``
    #: attribute will represent that of the trustee. *Type: bool*
    is_impersonation = resource.prop('impersonation', type=bool)
    #: Represents the user ID who is capable of consuming the trust.
    #: *Type: string*
    trustee_user_id = resource.prop('trustee_user_id')
    #: Represents the user ID who created the trust, and who's authorization is
    #: being delegated. *Type: string*
    trustor_user_id = resource.prop('trustor_user_id')
    #: Specifies the subset of the trustor's roles on the ``project_id``
    #: to be granted to the trustee when the token in consumed. The
    #: trustor must already be granted these roles in the project referenced
    #: by the ``project_id`` attribute. *Type: list*
    roles = resource.prop('roles')
    #: Redelegation count
    redelegation_count = resource.prop('redelegation_count')
