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


class DeviceProfile(resource.Resource):
    resource_key = 'device_profile'
    resources_key = 'device_profiles'
    base_path = '/device_profiles'
    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    #: The timestamp when this device_profile was created.
    created_at = resource.Body('created_at')
    #: The groups of the device profile
    groups = resource.Body('groups')
    #: The name of the device profile
    name = resource.Body('name')
    #: The timestamp when this device_profile was updated.
    updated_at = resource.Body('updated_at')
    #: The uuid of the device profile
    uuid = resource.Body('uuid', alternate_id=True)

    # TODO(s_shogo): This implementation only treat [ DeviceProfile ], and
    # cannot treat multiple DeviceProfiles in list.
    def _prepare_request_body(self, patch, prepend_key):
        body = super(DeviceProfile, self)._prepare_request_body(
            patch, prepend_key)
        return [body]

    def create(self, session, base_path=None):
        # This overrides the default behavior of resource creation because
        # cyborg doesn't accept resource_key in its request.
        return super(DeviceProfile, self).create(
            session, prepend_key=False, base_path=base_path)
