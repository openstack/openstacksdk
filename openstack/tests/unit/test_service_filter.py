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

import testtools

from openstack.identity import identity_service
from openstack import service_filter


class TestValidVersion(testtools.TestCase):
    def test_constructor(self):
        sot = service_filter.ValidVersion('v1.0', 'v1')
        self.assertEqual('v1.0', sot.module)
        self.assertEqual('v1', sot.path)


class TestServiceFilter(testtools.TestCase):
    def test_init(self):
        sot = service_filter.ServiceFilter(
            'ServiceType', region='REGION1', service_name='ServiceName',
            version='1', api_version='1.23', requires_project_id=True)
        self.assertEqual('servicetype', sot.service_type)
        self.assertEqual('REGION1', sot.region)
        self.assertEqual('ServiceName', sot.service_name)
        self.assertEqual('1', sot.version)
        self.assertEqual('1.23', sot.api_version)
        self.assertTrue(sot.requires_project_id)

    def test_get_module(self):
        sot = identity_service.IdentityService()
        self.assertEqual('openstack.identity.v3', sot.get_module())
        self.assertEqual('identity', sot.get_service_module())
