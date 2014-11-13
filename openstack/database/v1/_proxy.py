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

from openstack.database.v1 import database
from openstack.database.v1 import flavor
from openstack.database.v1 import instance
from openstack.database.v1 import user


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def create_database(self, **data):
        return database.Database(data).create(self.session)

    def delete_database(self, **data):
        database.Database(data).delete(self.session)

    def find_database(self, name_or_id):
        return database.Database.find(self.session, name_or_id)

    def list_database(self):
        return database.Database.list(self.session)

    def find_flavor(self, name_or_id):
        return flavor.Flavor.find(self.session, name_or_id)

    def get_flavor(self, **data):
        return flavor.Flavor(data).get(self.session)

    def list_flavor(self):
        return flavor.Flavor.list(self.session)

    def create_instance(self, **data):
        return instance.Instance(data).create(self.session)

    def delete_instance(self, **data):
        instance.Instance(data).delete(self.session)

    def find_instance(self, name_or_id):
        return instance.Instance.find(self.session, name_or_id)

    def get_instance(self, **data):
        return instance.Instance(data).get(self.session)

    def list_instance(self):
        return instance.Instance.list(self.session)

    def update_instance(self, **data):
        return instance.Instance(data).update(self.session)

    def create_user(self, **data):
        return user.User(data).create(self.session)

    def delete_user(self, **data):
        user.User(data).delete(self.session)

    def find_user(self, name_or_id):
        return user.User.find(self.session, name_or_id)

    def list_user(self):
        return user.User.list(self.session)
