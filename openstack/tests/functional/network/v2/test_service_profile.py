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

from openstack.network.v2 import service_profile as _service_profile
from openstack.tests.functional import base


class TestServiceProfile(base.BaseFunctionalTest):
    SERVICE_PROFILE_DESCRIPTION = "DESCRIPTION"
    UPDATE_DESCRIPTION = "UPDATED-DESCRIPTION"
    METAINFO = "FlAVOR_PROFILE_METAINFO"
    ID = None

    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension("flavors"):
            self.skipTest("Neutron flavor extension is required for this test")

        if self.operator_cloud:
            service_profiles = (
                self.operator_cloud.network.create_service_profile(
                    description=self.SERVICE_PROFILE_DESCRIPTION,
                    metainfo=self.METAINFO,
                )
            )
            assert isinstance(
                service_profiles, _service_profile.ServiceProfile
            )
            self.assertEqual(
                self.SERVICE_PROFILE_DESCRIPTION, service_profiles.description
            )
            self.assertEqual(self.METAINFO, service_profiles.meta_info)

            self.ID = service_profiles.id

    def tearDown(self):
        if self.ID:
            service_profiles = (
                self.operator_cloud.network.delete_service_profile(
                    self.ID, ignore_missing=True
                )
            )
            self.assertIsNone(service_profiles)
        super().tearDown()

    def test_find(self):
        self.user_cloud.network.find_service_profile(
            name_or_id="not_existing", ignore_missing=True
        )
        if self.operator_cloud and self.ID:
            service_profiles = (
                self.operator_cloud.network.find_service_profile(self.ID)
            )
            self.assertEqual(self.METAINFO, service_profiles.meta_info)

    def test_get(self):
        if not self.ID:
            self.skipTest("ServiceProfile was not created")
        service_profiles = self.operator_cloud.network.get_service_profile(
            self.ID
        )
        self.assertEqual(self.METAINFO, service_profiles.meta_info)
        self.assertEqual(
            self.SERVICE_PROFILE_DESCRIPTION, service_profiles.description
        )

    def test_update(self):
        if not self.ID:
            self.skipTest("ServiceProfile was not created")
        service_profiles = self.operator_cloud.network.update_service_profile(
            self.ID, description=self.UPDATE_DESCRIPTION
        )
        self.assertEqual(self.UPDATE_DESCRIPTION, service_profiles.description)

    def test_list(self):
        # Test in user scope
        self.user_cloud.network.service_profiles()
        # Test as operator
        if self.operator_cloud:
            metainfos = [
                f.meta_info
                for f in self.operator_cloud.network.service_profiles()
            ]
            if self.ID:
                self.assertIn(self.METAINFO, metainfos)
