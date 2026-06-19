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


class ManageableSnapshot(resource.Resource):
    resource_key = 'manageable-snapshot'
    resources_key = 'manageable-snapshots'
    base_path = '/manageable_snapshots'

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
    #: The ID of this snapshot in Cinder, if already managed.
    cinder_id = resource.Body('cinder_id')
    #: Additional information about the snapshot.
    extra_info = resource.Body('extra_info')
    #: The reason the snapshot is not safe to manage, if applicable.
    reason_not_safe = resource.Body('reason_not_safe')
    #: A reference to identify the existing snapshot on the backend.
    reference = resource.Body('reference', type=dict)
    #: Whether it is safe to manage this snapshot.
    safe_to_manage = resource.Body('safe_to_manage', type=bool)
    #: The size of the snapshot in GiB.
    size = resource.Body('size', type=int)
    #: A reference to the source volume of the snapshot.
    source_reference = resource.Body('source_reference', type=dict)
