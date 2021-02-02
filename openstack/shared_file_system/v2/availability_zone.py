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

from openstack import resource


class AvailabilityZone(resource.Resource):
    resource_key = "availability_zone"
    resources_key = "availability_zones"
    base_path = "/availability-zones"

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    #: Properties
    #: The ID of the availability zone
    id = resource.Body("id", type=str)
    #: The name of the availability zone.
    name = resource.Body("name", type=str)
    #: Date and time the availability zone was created at.
    created_at = resource.Body("created_at", type=str)
    #: Date and time the availability zone was last updated at.
    updated_at = resource.Body("updated_at", type=str)
