# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_floating_ip_pool
----------------------------------

Test floating IP pool resource (managed by nova)
"""

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.unit import base
from openstack.tests import fakes


class TestFloatingIPPool(base.TestCase):
    pools = [{'name': u'public'}]

    def test_list_floating_ip_pools(self):

        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/extensions'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json={'extensions': [{
                     u'alias': u'os-floating-ip-pools',
                     u'updated': u'2014-12-03T00:00:00Z',
                     u'name': u'FloatingIpPools',
                     u'links': [],
                     u'namespace':
                     u'http://docs.openstack.org/compute/ext/fake_xml',
                     u'description': u'Floating IPs support.'}]}),
            dict(method='GET',
                 uri='{endpoint}/os-floating-ip-pools'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json={"floating_ip_pools": [{"name": "public"}]})
        ])

        floating_ip_pools = self.cloud.list_floating_ip_pools()

        self.assertCountEqual(floating_ip_pools, self.pools)

        self.assert_calls()

    def test_list_floating_ip_pools_exception(self):

        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/extensions'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json={'extensions': [{
                     u'alias': u'os-floating-ip-pools',
                     u'updated': u'2014-12-03T00:00:00Z',
                     u'name': u'FloatingIpPools',
                     u'links': [],
                     u'namespace':
                     u'http://docs.openstack.org/compute/ext/fake_xml',
                     u'description': u'Floating IPs support.'}]}),
            dict(method='GET',
                 uri='{endpoint}/os-floating-ip-pools'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 status_code=404)])

        self.assertRaises(
            OpenStackCloudException, self.cloud.list_floating_ip_pools)

        self.assert_calls()
