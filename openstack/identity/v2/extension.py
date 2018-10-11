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


class Extension(resource.Resource):
    resource_key = 'extension'
    resources_key = 'extensions'
    base_path = '/extensions'

    # capabilities
    allow_list = True
    allow_fetch = True

    # Properties
    #: A unique identifier, which will be used for accessing the extension
    #: through a dedicated url ``/extensions/*alias*``. The extension
    #: alias uniquely identifies an extension and is prefixed by a vendor
    #: identifier. *Type: string*
    alias = resource.Body('alias', alternate_id=True)
    #: A description of the extension. *Type: string*
    description = resource.Body('description')
    #: Links to the documentation in various format. *Type: string*
    links = resource.Body('links')
    #: The name of the extension. *Type: string*
    name = resource.Body('name')
    #: The second unique identifier of the extension after the alias.
    #: It is usually a URL which will be used. Example:
    #: "http://docs.openstack.org/identity/api/ext/s3tokens/v1.0"
    #: *Type: string*
    namespace = resource.Body('namespace')
    #: The last time the extension has been modified (update date).
    updated_at = resource.Body('updated')

    @classmethod
    def list(cls, session, paginated=False, **params):
        resp = session.get(cls.base_path,
                           params=params)
        resp = resp.json()
        for data in resp[cls.resources_key]['values']:
            yield cls.existing(**data)
