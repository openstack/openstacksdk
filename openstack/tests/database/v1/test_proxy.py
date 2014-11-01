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

from openstack.database.v1 import _proxy
from openstack.tests import test_proxy_base


class TestDatabaseProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestDatabaseProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_database(self):
        self.verify_create('openstack.database.v1.database.Database.create',
                           self.proxy.create_database)
        self.verify_delete('openstack.database.v1.database.Database.delete',
                           self.proxy.delete_database)
        self.verify_find('openstack.database.v1.database.Database.find',
                         self.proxy.find_database)
        self.verify_list('openstack.database.v1.database.Database.list',
                         self.proxy.list_database)

    def test_flavor(self):
        self.verify_find('openstack.database.v1.flavor.Flavor.find',
                         self.proxy.find_flavor)
        self.verify_get('openstack.database.v1.flavor.Flavor.get',
                        self.proxy.get_flavor)
        self.verify_list('openstack.database.v1.flavor.Flavor.list',
                         self.proxy.list_flavor)

    def test_instance(self):
        self.verify_create('openstack.database.v1.instance.Instance.create',
                           self.proxy.create_instance)
        self.verify_delete('openstack.database.v1.instance.Instance.delete',
                           self.proxy.delete_instance)
        self.verify_find('openstack.database.v1.instance.Instance.find',
                         self.proxy.find_instance)
        self.verify_get('openstack.database.v1.instance.Instance.get',
                        self.proxy.get_instance)
        self.verify_list('openstack.database.v1.instance.Instance.list',
                         self.proxy.list_instance)
        self.verify_update('openstack.database.v1.instance.Instance.update',
                           self.proxy.update_instance)

    def test_user(self):
        self.verify_create('openstack.database.v1.user.User.create',
                           self.proxy.create_user)
        self.verify_delete('openstack.database.v1.user.User.delete',
                           self.proxy.delete_user)
        self.verify_find('openstack.database.v1.user.User.find',
                         self.proxy.find_user)
        self.verify_list('openstack.database.v1.user.User.list',
                         self.proxy.list_user)
