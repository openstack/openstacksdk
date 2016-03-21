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
from openstack import resource


class Domain(resource.Resource):
    resource_key = 'domain'
    resources_key = 'domains'
    base_path = '/domains'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    #: The description of this domain. *Type: string*
    description = resource.prop('description')
    #: Setting this attribute to ``False`` prevents users from authorizing
    #: against this domain or any projects owned by this domain, and prevents
    #: users owned by this domain from authenticating or receiving any other
    #: authorization. Additionally, all pre-existing tokens applicable
    #: to the above entities are immediately invalidated.
    #: Re-enabling a domain does not re-enable pre-existing tokens.
    #: *Type: bool*
    is_enabled = resource.prop('enabled', type=bool)
    #: The globally unique name of this domain. *Type: string*
    name = resource.prop('name')
