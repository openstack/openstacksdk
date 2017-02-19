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

    @classmethod
    def setUpClass(cls):
        super(TestServiceProfile, cls).setUpClass()
        service_profiles = cls.conn.network.create_service_profile(
            description=cls.SERVICE_PROFILE_DESCRIPTION,
            metainfo=cls.METAINFO,)
        assert isinstance(service_profiles, _service_profile.ServiceProfile)
        cls.assertIs(cls.SERVICE_PROFILE_DESCRIPTION,
                     service_profiles.description)
        cls.assertIs(cls.METAINFO, service_profiles.meta_info)

        cls.ID = service_profiles.id

    @classmethod
    def tearDownClass(cls):
        service_profiles = cls.conn.network.delete_service_profile(
            cls.ID,
            ignore_missing=True)
        cls.assertIs(None, service_profiles)

    def test_find(self):
        service_profiles = self.conn.network.find_service_profile(
            self.ID)
        self.assertEqual(self.METAINFO,
                         service_profiles.meta_info)

    def test_get(self):
        service_profiles = self.conn.network.get_service_profile(self.ID)
        self.assertEqual(self.METAINFO, service_profiles.meta_info)
        self.assertEqual(self.SERVICE_PROFILE_DESCRIPTION,
                         service_profiles.description)

    def test_update(self):
        service_profiles = self.conn.network.update_service_profile(
            self.ID,
            description=self.UPDATE_DESCRIPTION)
        self.assertEqual(self.UPDATE_DESCRIPTION, service_profiles.description)

    def test_list(self):
        metainfos = [f.meta_info for f in self.conn.network.service_profiles()]
        self.assertIn(self.METAINFO, metainfos)
