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

from openstack.dns.v2 import _base
from openstack import resource
# from openstack import exceptions
# from openstack import utils


class TSIGKey(_base.Resource):
    """DNS TSIGKEY Resource"""

    resources_key = 'tsigkeys'
    base_path = '/tsigkeys'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    commit_method = "PATCH"

    _query_mapping = resource.QueryParameters(
        'name',
        'algorithm',
        'scope',
        'limit',
        'marker',
    )

    #: Properties

    #: ID for the resource
    id = resource.Body('id')
    #: resource id for this tsigkey which can be either zone or pool id
    resource_id = resource.Body('resource_id')
    #: TSIGKey name
    name = resource.Body('name')
    #: scope for this tsigkey which can be either ZONE or POOL scope
    scope = resource.Body('scope')
    #: The actual key to be used
    secret = resource.Body('secret')
    #: The encryption algorithm for this tsigkey
    algorithm = resource.Body('algorithm')
    #: Timestamp when the tsigkey was created
    created_at = resource.Body('created_at')
    #: Timestamp when the tsigkey was last updated
    updated_at = resource.Body('updated_at')
    #: Links contains a 'self' pertaining to this tsigkey or a 'next' pertaining
    #: to next page
    links = resource.Body('links', type=dict)
