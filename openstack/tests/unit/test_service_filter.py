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

import six
import testtools

from openstack import exceptions
from openstack.identity import identity_service
from openstack import service_filter as filt


class TestServiceFilter(testtools.TestCase):
    def test_minimum(self):
        sot = filt.ServiceFilter()
        self.assertEqual("service_type=any,interface=public",
                         six.text_type(sot))

    def test_maximum(self):
        sot = filt.ServiceFilter(service_type='compute', interface='admin',
                                 region='b', service_name='c')
        exp = "service_type=compute,interface=admin,region=b,service_name=c"
        self.assertEqual(exp, six.text_type(sot))

    def test_interface(self):
        sot = filt.ServiceFilter(service_type='identity', interface='public')
        self.assertEqual("service_type=identity,interface=public",
                         six.text_type(sot))
        sot = filt.ServiceFilter(service_type='identity',
                                 interface='internal')
        self.assertEqual("service_type=identity,interface=internal",
                         six.text_type(sot))
        sot = filt.ServiceFilter(service_type='identity', interface='admin')
        self.assertEqual("service_type=identity,interface=admin",
                         six.text_type(sot))
        sot = filt.ServiceFilter(service_type='identity',
                                 interface='publicURL')
        self.assertEqual("service_type=identity,interface=public",
                         six.text_type(sot))
        sot = filt.ServiceFilter(service_type='identity',
                                 interface='internalURL')
        self.assertEqual("service_type=identity,interface=internal",
                         six.text_type(sot))
        sot = filt.ServiceFilter(service_type='identity',
                                 interface='adminURL')
        self.assertEqual("service_type=identity,interface=admin",
                         six.text_type(sot))
        self.assertRaises(exceptions.SDKException, filt.ServiceFilter,
                          service_type='identity', interface='b')
        sot = filt.ServiceFilter(service_type='identity', interface=None)
        self.assertEqual("service_type=identity", six.text_type(sot))

    def test_match_service_type(self):
        sot = filt.ServiceFilter(service_type='identity')
        self.assertTrue(sot.match_service_type('identity'))
        self.assertFalse(sot.match_service_type('compute'))

    def test_match_service_type_any(self):
        sot = filt.ServiceFilter()
        self.assertTrue(sot.match_service_type('identity'))
        self.assertTrue(sot.match_service_type('compute'))

    def test_match_service_name(self):
        sot = filt.ServiceFilter(service_type='identity')
        self.assertTrue(sot.match_service_name('keystone'))
        self.assertTrue(sot.match_service_name('ldap'))
        self.assertTrue(sot.match_service_name(None))
        sot = filt.ServiceFilter(service_type='identity',
                                 service_name='keystone')
        self.assertTrue(sot.match_service_name('keystone'))
        self.assertFalse(sot.match_service_name('ldap'))
        self.assertFalse(sot.match_service_name(None))

    def test_match_region(self):
        sot = filt.ServiceFilter(service_type='identity')
        self.assertTrue(sot.match_region('East'))
        self.assertTrue(sot.match_region('West'))
        self.assertTrue(sot.match_region(None))
        sot = filt.ServiceFilter(service_type='identity', region='East')
        self.assertTrue(sot.match_region('East'))
        self.assertFalse(sot.match_region('West'))
        self.assertFalse(sot.match_region(None))

    def test_match_interface(self):
        sot = filt.ServiceFilter(service_type='identity',
                                 interface='internal')
        self.assertFalse(sot.match_interface('admin'))
        self.assertTrue(sot.match_interface('internal'))
        self.assertFalse(sot.match_interface('public'))

    def test_join(self):
        a = filt.ServiceFilter(region='east')
        b = filt.ServiceFilter(service_type='identity')
        result = a.join(b)
        self.assertEqual("service_type=identity,interface=public,region=east",
                         six.text_type(result))
        self.assertEqual("service_type=any,interface=public,region=east",
                         six.text_type(a))
        self.assertEqual("service_type=identity,interface=public",
                         six.text_type(b))

    def test_join_interface(self):
        user_preference = filt.ServiceFilter(interface='public')
        service_default = filt.ServiceFilter(interface='admin')
        result = user_preference.join(service_default)
        self.assertEqual("public", result.interface)
        user_preference = filt.ServiceFilter(interface=None)
        service_default = filt.ServiceFilter(interface='admin')
        result = user_preference.join(service_default)
        self.assertEqual("admin", result.interface)

    def test_join_version(self):
        user_preference = filt.ServiceFilter(version='v2')
        service_default = filt.ServiceFilter()
        self.assertEqual('v2', user_preference.join(service_default).version)
        service_default = filt.ServiceFilter(
            version=filt.ServiceFilter.UNVERSIONED
        )
        self.assertEqual('', user_preference.join(service_default).version)

    def test_set_interface(self):
        sot = filt.ServiceFilter()
        sot.set_interface("PUBLICURL")
        self.assertEqual('public', sot.interface)
        sot.set_interface("INTERNALURL")
        self.assertEqual('internal', sot.interface)
        sot.set_interface("ADMINURL")
        self.assertEqual('admin', sot.interface)

    def test_get_module(self):
        sot = identity_service.IdentityService()
        self.assertEqual('openstack.identity.v3', sot.get_module())
        self.assertEqual('identity', sot.get_service_module())

    def test_get_version_path(self):
        sot = identity_service.IdentityService()
        self.assertEqual('v3', sot.get_version_path('v2'))
        sot = identity_service.IdentityService(version='v2')
        self.assertEqual('v2', sot.get_version_path('v3'))
        sot = identity_service.IdentityService(version='v2.1')
        self.assertEqual('v2.1', sot.get_version_path('v3'))
        sot = identity_service.IdentityService(version='')
        self.assertEqual('', sot.get_version_path('v3'))


class TestValidVersion(testtools.TestCase):
    def test_constructor(self):
        sot = filt.ValidVersion('v1.0', 'v1')
        self.assertEqual('v1.0', sot.module)
        self.assertEqual('v1', sot.path)
