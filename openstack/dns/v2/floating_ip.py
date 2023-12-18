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


class FloatingIP(_base.Resource):
    """DNS Floating IP Resource"""

    resources_key = 'floatingips'
    base_path = '/reverse/floatingips'

    # capabilities
    allow_fetch = True
    allow_commit = True
    allow_list = True
    commit_method = "PATCH"

    #: Properties
    #: current action in progress on the resource
    action = resource.Body('action')
    #: The floatingip address for this PTR record
    address = resource.Body('address')
    #: Description for this PTR record
    description = resource.Body('description')
    #: Domain name for this PTR record
    ptrdname = resource.Body('ptrdname')
    #: status of the resource
    status = resource.Body('status')
    #: Time to live for this PTR record
    ttl = resource.Body('ttl', type=int)
