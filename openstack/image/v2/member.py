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


class Member(resource.Resource):
    resources_key = 'members'
    base_path = '/images/%(image_id)s/members'
    service = image_service.ImageService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # See https://bugs.launchpad.net/glance/+bug/1526991 for member/member_id
    # 'member' is documented incorrectly as being deprecated but it's the
    # only thing that works. 'member_id' is not accepted.

    #: The ID of the image member. An image member is a tenant
    #: with whom the image is shared.
    member_id = resource.Body('member', alternate_id=True)
    #: The date and time when the member was created.
    created_at = resource.Body('created_at')
    #: Image ID stored through the image API. Typically a UUID.
    image_id = resource.URI('image_id')
    #: The status of the image.
    status = resource.Body('status')
    #: The URL for schema of the member.
    schema = resource.Body('schema')
    #: The date and time when the member was updated.
    updated_at = resource.Body('updated_at')
