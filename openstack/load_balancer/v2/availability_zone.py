#
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
    resource_key = 'availability_zone'
    resources_key = 'availability_zones'
    base_path = '/lbaas/availabilityzones'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'name',
        'description',
        'availability_zone_profile_id',
        is_enabled='enabled',
    )

    # Properties
    #: The name of the availability zone.
    name = resource.Body('name')
    #: The availability zone description.
    description = resource.Body('description')
    #: The associated availability zone profile ID
    availability_zone_profile_id = resource.Body(
        'availability_zone_profile_id'
    )
    #: Whether the availability zone is enabled for use or not.
    is_enabled = resource.Body('enabled')
