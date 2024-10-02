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


class ServiceStatus(_base.Resource):
    """Designate Service Statuses"""

    resources_key = 'service_statuses'
    base_path = '/service_statuses'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    #: Capabilities for the service
    capabilities = resource.Body('capabilities', type=dict)
    #: Timestamp when the resource was created
    created_at = resource.Body('created_at')
    #: Timestamp when the last heartbeat was received
    heartbeated_at = resource.Body('heartbeated_at')
    #: Hostname of the host with the service instance
    #: *Type: str*
    hostname = resource.Body('hostname')
    #: Links contains a `self` pertaining to this service status or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
    #: The name of the Designate service instance
    #: *Type: str*
    service_name = resource.Body('service_name')
    #: Statistics for the service
    stats = resource.Body('stats', type=dict)
    #: The status of the resource
    #: *Type: enum*
    status = resource.Body('status')
    #: Timestamp when the resource was last updated
    updated_at = resource.Body('updated_at')
