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
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_database_create_attrs(self):
        self.verify_create(
            self.proxy.create_database,
            database.Database,
            method_kwargs={"instance": "id"},
            expected_kwargs={"instance_id": "id"},
        )

    def test_database_delete(self):
        self.verify_delete(
            self.proxy.delete_database,
            database.Database,
            ignore_missing=False,
            method_kwargs={"instance": "test_id"},
            expected_kwargs={"instance_id": "test_id"},
        )

    def test_database_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_database,
            database.Database,
            ignore_missing=True,
            method_kwargs={"instance": "test_id"},
            expected_kwargs={"instance_id": "test_id"},
        )

    def test_database_find(self):
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_database,
            method_args=["db", "instance"],
            expected_args=[database.Database, "db"],
            expected_kwargs={
                "instance_id": "instance",
                "ignore_missing": True,
            },
        )

    def test_databases(self):
        self.verify_list(
            self.proxy.databases,
            database.Database,
            method_args=["id"],
            expected_args=[],
            expected_kwargs={"instance_id": "id"},
        )

    def test_database_get(self):
        self.verify_get(self.proxy.get_database, database.Database)

    def test_flavor_find(self):
        self.verify_find(self.proxy.find_flavor, flavor.Flavor)

    def test_flavor_get(self):
        self.verify_get(self.proxy.get_flavor, flavor.Flavor)

    def test_flavors(self):
        self.verify_list(self.proxy.flavors, flavor.Flavor)

    def test_instance_create_attrs(self):
        self.verify_create(self.proxy.create_instance, instance.Instance)

    def test_instance_delete(self):
        self.verify_delete(
            self.proxy.delete_instance, instance.Instance, False
        )

    def test_instance_delete_ignore(self):
        self.verify_delete(self.proxy.delete_instance, instance.Instance, True)

    def test_instance_find(self):
        self.verify_find(self.proxy.find_instance, instance.Instance)

    def test_instance_get(self):
        self.verify_get(self.proxy.get_instance, instance.Instance)

    def test_instances(self):
        self.verify_list(self.proxy.instances, instance.Instance)

    def test_instance_update(self):
        self.verify_update(self.proxy.update_instance, instance.Instance)

    def test_user_create_attrs(self):
        self.verify_create(
            self.proxy.create_user,
            user.User,
            method_kwargs={"instance": "id"},
            expected_kwargs={"instance_id": "id"},
        )

    def test_user_delete(self):
        self.verify_delete(
            self.proxy.delete_user,
            user.User,
            False,
            method_kwargs={"instance": "id"},
            expected_kwargs={"instance_id": "id"},
        )

    def test_user_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_user,
            user.User,
            True,
            method_kwargs={"instance": "id"},
            expected_kwargs={"instance_id": "id"},
        )

    def test_user_find(self):
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_user,
            method_args=["user", "instance"],
            expected_args=[user.User, "user"],
            expected_kwargs={
                "instance_id": "instance",
                "ignore_missing": True,
            },
        )

    def test_users(self):
        self.verify_list(
            self.proxy.users,
            user.User,
            method_args=["test_instance"],
            expected_args=[],
            expected_kwargs={"instance_id": "test_instance"},
        )

    def test_user_get(self):
        self.verify_get(self.proxy.get_user, user.User)
