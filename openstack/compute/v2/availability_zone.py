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

from openstack.compute import compute_service
from openstack import resource


class AvailabilityZone(resource.Resource):
    resources_key = 'availabilityZoneInfo'
    base_path = '/os-availability-zone'

    service = compute_service.ComputeService()

    # capabilities
    allow_list = True

    # Properties
    #: name of availability zone
    name = resource.Body('zoneName')
    #: state of availability zone
    state = resource.Body('zoneState')
    #: hosts of availability zone
    hosts = resource.Body('hosts')


class AvailabilityZoneDetail(AvailabilityZone):
    base_path = '/os-availability-zone/detail'
