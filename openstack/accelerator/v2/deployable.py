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

from collections.abc import Sequence
from typing import Any
from typing_extensions import Self

from keystoneauth1 import adapter

from openstack import resource


class Deployable(resource.Resource):
    resource_key = 'deployable'
    resources_key = 'deployables'
    base_path = '/deployables'
    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_patch = True
    #: The timestamp when this deployable was created.
    created_at = resource.Body('created_at')
    #: The device_id of the deployable.
    device_id = resource.Body('device_id')
    #: The UUID of the deployable.
    id = resource.Body('uuid', alternate_id=True)
    #: The name of the deployable.
    name = resource.Body('name')
    #: The num_accelerator of the deployable.
    num_accelerators = resource.Body('num_accelerators')
    #: The parent_id of the deployable.
    parent_id = resource.Body('parent_id')
    #: The root_id of the deployable.
    root_id = resource.Body('root_id')
    #: The timestamp when this deployable was updated.
    updated_at = resource.Body('updated_at')

    def patch(
        self,
        session: adapter.Adapter,
        patch: Sequence[dict[str, Any]] | None = None,
        prepend_key: bool = True,
        has_body: bool = True,
        retry_on_conflict: bool | None = None,
        base_path: str | None = '/deployables/%(id)s/program',
        *,
        microversion: str | None = None,
    ) -> Self:
        return super().patch(
            session,
            patch=patch,
            prepend_key=prepend_key,
            has_body=has_body,
            retry_on_conflict=retry_on_conflict,
            base_path=base_path,
            microversion=microversion,
        )
