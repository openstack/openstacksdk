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


class ShareExportLocation(resource.Resource):
    resource_key = "export_location"
    resources_key = "export_locations"
    base_path = "/shares/%(share_id)s/export_locations"

    # capabilities
    allow_list = True
    allow_fetch = True
    allow_create = False
    allow_commit = False
    allow_delete = False
    allow_head = False

    _max_microversion = '2.47'

    #: Properties
    # The share ID, part of the URI for export locations
    share_id = resource.URI("share_id", type=str)
    #: The path of the export location.
    path = resource.Body("path", type=str)
    #: Indicate if export location is preferred.
    is_preferred = resource.Body("preferred", type=bool)
    #: The share instance ID of the export location.
    share_instance_id = resource.Body("share_instance_id", type=str)
    #: Indicate if export location is admin only.
    is_admin = resource.Body("is_admin_only", type=bool)
    #: Indicate when the export location is created at
    created_at = resource.Body("created_at", type=str)
    #: Indicate when the export location is updated at
    updated_at = resource.Body("updated_at", type=str)
