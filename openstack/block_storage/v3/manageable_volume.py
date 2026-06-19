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


class ManageableVolume(resource.Resource):
    resource_key = 'manageable-volume'
    resources_key = 'manageable-volumes'
    base_path = '/manageable_volumes'

    # capabilities
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'host',
        'cluster',
        'marker',
        'limit',
        'offset',
        'sort',
    )

    # Properties
    #: The ID of this volume in Cinder, if already managed.
    cinder_id = resource.Body('cinder_id')
    #: Additional information about the volume.
    extra_info = resource.Body('extra_info')
    #: The reason the volume is not safe to manage, if applicable.
    reason_not_safe = resource.Body('reason_not_safe')
    #: A reference to identify the existing volume on the backend.
    reference = resource.Body('reference', type=dict)
    #: Whether it is safe to manage this volume.
    safe_to_manage = resource.Body('safe_to_manage', type=bool)
    #: The size of the volume in GiB.
    size = resource.Body('size', type=int)
