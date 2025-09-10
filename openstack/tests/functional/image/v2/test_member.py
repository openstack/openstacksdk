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

from openstack import exceptions as sdk_exc
from openstack.image.v2 import image as _image
from openstack.image.v2 import member as _member
from openstack.tests.functional.image.v2 import base


TEST_IMAGE_NAME = 'Test Image for Sharing'
MEMBER_STATUS_PENDING = 'pending'
MEMBER_STATUS_ACCEPTED = 'accepted'


class TestImageMember(base.BaseImageTest):
    def setUp(self):
        super().setUp()

        # NOTE(jbeen): 1-byte dummy image data for sharing tests; not bootable.
        self.image = self.operator_cloud.image.create_image(
            name=TEST_IMAGE_NAME,
            disk_format='raw',
            container_format='bare',
            visibility='shared',
            data=b'0',
        )
        self.assertIsInstance(self.image, _image.Image)
        self.assertEqual(TEST_IMAGE_NAME, self.image.name)

        self.member_id = self.user_cloud.session.get_project_id()
        self.assertIsNotNone(self.member_id)

    def tearDown(self):
        self.operator_cloud.image.delete_image(self.image)
        self.operator_cloud.image.wait_for_delete(self.image)

        super().tearDown()

    def test_image_members(self):
        # add member
        member = self.operator_cloud.image.add_member(
            image=self.image, member=self.member_id
        )
        self.assertIsInstance(member, _member.Member)
        self.assertEqual(self.member_id, member.member_id)
        self.assertEqual(MEMBER_STATUS_PENDING, member.status)

        # get member
        member = self.operator_cloud.image.get_member(
            image=self.image, member=self.member_id
        )
        self.assertIsInstance(member, _member.Member)
        self.assertEqual(self.member_id, member.member_id)

        # list members
        members = list(self.operator_cloud.image.members(image=self.image))
        self.assertIn(self.member_id, {m.id for m in members})

        # update member
        member = self.user_cloud.image.update_member(
            image=self.image,
            member=self.member_id,
            status=MEMBER_STATUS_ACCEPTED,
        )
        self.assertIsInstance(member, _member.Member)
        self.assertEqual(self.member_id, member.member_id)
        self.assertEqual(MEMBER_STATUS_ACCEPTED, member.status)

        # remove member
        self.operator_cloud.image.remove_member(
            image=self.image, member=self.member_id
        )
        self.assertRaises(
            sdk_exc.NotFoundException,
            self.operator_cloud.image.get_member,
            image=self.image,
            member=self.member_id,
        )
