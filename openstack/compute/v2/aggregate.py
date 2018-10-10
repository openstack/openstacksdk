# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from openstack import resource


class Aggregate(resource.Resource):
    resource_key = 'aggregate'
    resources_key = 'aggregates'
    base_path = '/os-aggregates'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Availability zone of aggregate
    availability_zone = resource.Body('availability_zone')
    #: Deleted?
    deleted = resource.Body('deleted')
    #: Name of aggregate
    name = resource.Body('name')
    #: Hosts
    hosts = resource.Body('hosts')
    #: Metadata
    metadata = resource.Body('metadata')
