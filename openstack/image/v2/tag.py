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

from openstack.image import image_service
from openstack import resource


class Tag(resource.Resource):
    id_attribute = 'tag'
    resources_key = 'tags'
    base_path = '/images/%(image_id)s/tags'
    service = image_service.ImageService()

    # capabilities
    allow_create = True
    allow_delete = True

    # Properties
    image_id = resource.prop('image_id')

    def create(self, session):
        """Create a remote resource from this instance."""
        # Service expects a naked PUT. Omit properties.
        self.create_by_id(session, None, self.id, path_args=self)
        self._reset_dirty()
        return self