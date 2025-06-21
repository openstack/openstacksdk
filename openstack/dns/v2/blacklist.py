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


class Blacklist(_base.Resource):
    """DNS Blacklist Resource"""

    resources_key = 'blacklists'
    base_path = '/blacklists'

    # capabilities
    allow_list = True
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    commit_method = "PATCH"

    _query_mapping = resource.QueryParameters(
        'pattern',
    )

    #: Properties
    #: ID for the resource
    id = resource.Body('id')
    #: Pattern for this blacklist
    pattern = resource.Body('pattern')
    #: Description for this blacklist
    description = resource.Body("description")
    #: Timestampe when the blacklist created
    created_at = resource.Body("created_at")
    #: Timestampe when the blacklist last updated
    updated_at = resource.Body("updated_at")
    #: Links to the resource, and the other related resources.
    links = resource.Body("links")
