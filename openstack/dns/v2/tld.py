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


class TLD(_base.Resource):
    """DNS TLD Resource"""

    resources_key = "tlds"
    base_path = "/tlds"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    commit_method = "PATCH"

    _query_mapping = resource.QueryParameters(
        "name",
        "description",
        "limit",
        "marker",
    )

    #: TLD name
    name = resource.Body("name")
    #: TLD description
    description = resource.Body("description")
    #: Timestamp when the tld was created
    created_at = resource.Body("created_at")
    #: Timestamp when the tld was last updated
    updated_at = resource.Body("updated_at")
    #: Links contains a `self` pertaining to this tld or a `next` pertaining
    #: to next page
    links = resource.Body("links", type=dict)
