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

import typing as ty

from keystoneauth1 import adapter
import typing_extensions as ty_ext

from openstack import resource


class Version(resource.Resource):
    resource_key = 'version'
    resources_key = 'versions'
    base_path = '/'

    # capabilities
    allow_list = True

    # Properties
    media_types = resource.Body('media-types')
    status = resource.Body('status')
    updated = resource.Body('updated')

    @classmethod
    def list(
        cls,
        session: adapter.Adapter,
        paginated: bool = True,
        base_path: str | None = None,
        allow_unknown_params: bool = False,
        *,
        microversion: str | None = None,
        headers: dict[str, str] | None = None,
        **params: ty.Any,
    ) -> ty.Generator[ty_ext.Self, None, None]:
        if base_path is None:
            base_path = cls.base_path

        resp = session.get(base_path, params=params)
        resp = resp.json()
        for data in resp[cls.resources_key]['values']:
            yield cls.existing(**data)
