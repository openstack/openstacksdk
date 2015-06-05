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
from openstack.database.v1 import database
from openstack.database.v1 import flavor
from openstack.database.v1 import instance
from openstack.database.v1 import user
from openstack.tests.unit import test_proxy_base


class TestDatabaseProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestDatabaseProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_database_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_database,
                            method_kwargs=kwargs,
                            expected_args=[database.Database],
                            expected_kwargs=kwargs)

    def test_database_delete(self):
        self.verify_delete2(database.Database, self.proxy.delete_database,
                            False)

    def test_database_delete_ignore(self):
        self.verify_delete2(database.Database, self.proxy.delete_database,
                            True)

    def test_database_find(self):
        self.verify_find('openstack.database.v1.database.Database.find',
                         self.proxy.find_database)

    def test_databases(self):
        self.verify_list2(self.proxy.databases,
                          expected_args=[database.Database],
                          expected_kwargs={})

    def test_database_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_database,
                         method_args=["resource_or_id"],
                         expected_args=[database.Database, "resource_or_id"])

    def test_flavor_find(self):
        self.verify_find('openstack.database.v1.flavor.Flavor.find',
                         self.proxy.find_flavor)

    def test_flavor_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_flavor,
                         method_args=["resource_or_id"],
                         expected_args=[flavor.Flavor, "resource_or_id"])

    def test_flavors(self):
        self.verify_list2(self.proxy.flavors,
                          expected_args=[flavor.Flavor],
                          expected_kwargs={})

    def test_instance_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_instance,
                            method_kwargs=kwargs,
                            expected_args=[instance.Instance],
                            expected_kwargs=kwargs)

    def test_instance_delete(self):
        self.verify_delete2(instance.Instance, self.proxy.delete_instance,
                            False)

    def test_instance_delete_ignore(self):
        self.verify_delete2(instance.Instance, self.proxy.delete_instance,
                            True)

    def test_instance_find(self):
        self.verify_find('openstack.database.v1.instance.Instance.find',
                         self.proxy.find_instance)

    def test_instance_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_instance,
                         method_args=["resource_or_id"],
                         expected_args=[instance.Instance, "resource_or_id"])

    def test_instances(self):
        self.verify_list2(self.proxy.instances,
                          expected_args=[instance.Instance],
                          expected_kwargs={})

    def test_instance_update(self):
        self.verify_update(self.proxy.update_instance, instance.Instance)

    def test_user_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_user,
                            method_kwargs=kwargs,
                            expected_args=[user.User],
                            expected_kwargs=kwargs)

    def test_user_delete(self):
        self.verify_delete2(user.User, self.proxy.delete_user, False)

    def test_user_delete_ignore(self):
        self.verify_delete2(user.User, self.proxy.delete_user, True)

    def test_user_find(self):
        self.verify_find('openstack.database.v1.user.User.find',
                         self.proxy.find_user)

    def test_users(self):
        self.verify_list2(self.proxy.users,
                          expected_args=[user.User],
                          expected_kwargs={})

    def test_user_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_user,
                         method_args=["resource_or_id"],
                         expected_args=[user.User, "resource_or_id"])
