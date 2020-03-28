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


class AvailabilityZoneProfile(resource.Resource):
    resource_key = 'availability_zone_profile'
    resources_key = 'availability_zone_profiles'
    base_path = '/lbaas/availabilityzoneprofiles'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'id', 'name', 'provider_name', 'availability_zone_data'
    )

    # Properties
    #: The ID of the availability zone profile.
    id = resource.Body('id')
    #: The name of the availability zone profile.
    name = resource.Body('name')
    #: The provider this availability zone profile is for.
    provider_name = resource.Body('provider_name')
    #: The JSON string containing the availability zone metadata.
    availability_zone_data = resource.Body('availability_zone_data')
