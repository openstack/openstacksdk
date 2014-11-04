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

from openstack import exceptions
from openstack.tests import base
from openstack import user_preference


class TestUserPreference(base.TestCase):
    def test_init(self):
        pref = user_preference.UserPreference()
        expected = [
            'compute',
            'database',
            'identity',
            'image',
            'keystore',
            'metering',
            'network',
            'object-store',
            'orchestration',
        ]
        self.assertEqual(expected, pref.service_names)

    def test_set(self):
        pref = user_preference.UserPreference()
        self.assertEqual(None, pref.get_preference('compute'))
        pref.set_version('compute', 'v2')
        self.assertEqual('v2', pref.get_preference('compute').version)
        self.assertEqual(None, pref.get_preference('database'))
        pref.set_version('database', 'v3')
        self.assertEqual('v3', pref.get_preference('database').version)
        self.assertEqual(None, pref.get_preference('identity'))
        pref.set_version('identity', 'v4')
        self.assertEqual('v4', pref.get_preference('identity').version)
        self.assertEqual(None, pref.get_preference('image'))
        pref.set_version('image', 'v5')
        self.assertEqual('v5', pref.get_preference('image').version)
        self.assertEqual(None, pref.get_preference('metering'))
        pref.set_version('metering', 'v6')
        self.assertEqual('v6', pref.get_preference('metering').version)
        self.assertEqual(None, pref.get_preference('network'))
        pref.set_version('network', 'v7')
        self.assertEqual('v7', pref.get_preference('network').version)
        self.assertEqual(None, pref.get_preference('object-store'))
        pref.set_version('object-store', 'v8')
        self.assertEqual('v8', pref.get_preference('object-store').version)
        self.assertEqual(None, pref.get_preference('orchestration'))
        pref.set_version('orchestration', 'v9')
        self.assertEqual('v9', pref.get_preference('orchestration').version)

    def test_set_version_bad_service(self):
        pref = user_preference.UserPreference()
        self.assertRaises(exceptions.SDKException, pref.set_version, 'bogus',
                          'v2')

    def test_set_all(self):
        pref = user_preference.UserPreference()
        pref.set_name(pref.ALL, 'fee')
        pref.set_region(pref.ALL, 'fie')
        pref.set_version(pref.ALL, 'foe')
        pref.set_visibility(pref.ALL, 'public')
        for service in pref.service_names:
            self.assertEqual('fee', pref.get_preference(service).service_name)
            self.assertEqual('fie', pref.get_preference(service).region)
            self.assertEqual('foe', pref.get_preference(service).version)
            self.assertEqual('public', pref.get_preference(service).visibility)
