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

Functional tests for floating IP pool resource (managed by nova)
"""

from openstack.tests.functional import base


# When using nova-network, floating IP pools are created with nova-manage
# command.
# When using Neutron, floating IP pools in Nova are mapped from external
# network names. This only if the floating-ip-pools nova extension is
# available.
# For instance, for current implementation of hpcloud that's not true:
# nova floating-ip-pool-list returns 404.


class TestFloatingIPPool(base.BaseFunctionalTest):
    def test_list_floating_ip_pools(self):
        pools = self.user_cloud.list_floating_ip_pools()
        if not pools:
            self.assertFalse('no floating-ip pool available')

        for pool in pools:
            self.assertIn('name', pool)
