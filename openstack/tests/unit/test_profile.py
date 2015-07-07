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
from openstack import profile
from openstack.tests.unit import base


class TestProfile(base.TestCase):
    def test_init(self):
        prof = profile.Profile()
        expected = [
            'clustering',
            'compute',
            'database',
            'identity',
            'image',
            'key-manager',
            'messaging',
            'metering',
            'metric',
            'network',
            'object-store',
            'orchestration',
            'volume',
        ]
        self.assertEqual(expected, prof.service_names)

    def test_set(self):
        prof = profile.Profile()
        self.assertEqual(None, prof.get_preference('compute'))
        prof.set_version('compute', 'v2')
        self.assertEqual('v2', prof.get_preference('compute').version)
        self.assertEqual(None, prof.get_preference('clustering'))
        prof.set_version('clustering', 'v1')
        self.assertEqual('v1', prof.get_preference('clustering').version)
        self.assertEqual(None, prof.get_preference('database'))
        prof.set_version('database', 'v3')
        self.assertEqual('v3', prof.get_preference('database').version)
        self.assertEqual(None, prof.get_preference('identity'))
        prof.set_version('identity', 'v4')
        self.assertEqual('v4', prof.get_preference('identity').version)
        self.assertEqual(None, prof.get_preference('image'))
        prof.set_version('image', 'v5')
        self.assertEqual('v5', prof.get_preference('image').version)
        self.assertEqual(None, prof.get_preference('metering'))
        prof.set_version('metering', 'v6')
        self.assertEqual('v6', prof.get_preference('metering').version)
        self.assertEqual(None, prof.get_preference('metric'))
        prof.set_version('metric', 'v9')
        self.assertEqual('v9', prof.get_preference('metric').version)
        self.assertEqual(None, prof.get_preference('network'))
        prof.set_version('network', 'v7')
        self.assertEqual('v7', prof.get_preference('network').version)
        self.assertEqual(None, prof.get_preference('object-store'))
        prof.set_version('object-store', 'v8')
        self.assertEqual('v8', prof.get_preference('object-store').version)
        self.assertEqual(None, prof.get_preference('orchestration'))
        prof.set_version('orchestration', 'v9')
        self.assertEqual('v9', prof.get_preference('orchestration').version)

    def test_set_version_bad_service(self):
        prof = profile.Profile()
        self.assertRaises(exceptions.SDKException, prof.set_version, 'bogus',
                          'v2')

    def test_set_all(self):
        prof = profile.Profile()
        prof.set_name(prof.ALL, 'fee')
        prof.set_region(prof.ALL, 'fie')
        prof.set_visibility(prof.ALL, 'public')
        for service in prof.service_names:
            self.assertEqual('fee', prof.get_preference(service).service_name)
            self.assertEqual('fie', prof.get_preference(service).region)
            self.assertEqual('public', prof.get_preference(service).visibility)
