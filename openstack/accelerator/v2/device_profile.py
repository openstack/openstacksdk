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

from typing import Any, Self

from keystoneauth1 import adapter

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
    #: The description of the device profile
    description = resource.Body('description')
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
    def _prepare_request_body(
        self,
        *,
        prepend_key,
        resource_request_key=None,
    ):
        body = super()._prepare_request_body(
            prepend_key=prepend_key, resource_request_key=resource_request_key
        )
        return [body]

    def create(
        self,
        session: adapter.Adapter,
        prepend_key: bool = False,
        base_path: str | None = None,
        *,
        resource_request_key: str | None = None,
        resource_response_key: str | None = None,
        microversion: str | None = None,
        **params: Any,
    ) -> Self:
        # This overrides the default behavior of resource creation because
        # cyborg doesn't accept resource_key in its request.
        return super().create(
            session,
            prepend_key=prepend_key,
            base_path=base_path,
            resource_request_key=resource_request_key,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )
