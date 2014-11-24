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

from openstack.identity.v2 import role
from openstack.identity.v2 import tenant
from openstack.identity.v2 import user


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def create_role(self, **data):
        return role.Role(data).create(self.session)

    def delete_role(self, **data):
        role.Role(data).delete(self.session)

    def find_role(self, name_or_id):
        return role.Role.find(self.session, name_or_id)

    def get_role(self, **data):
        return role.Role(data).get(self.session)

    def list_roles(self):
        return role.Role.list(self.session)

    def update_role(self, **data):
        return role.Role(data).update(self.session)

    def create_tenant(self, **data):
        return tenant.Tenant(data).create(self.session)

    def delete_tenant(self, **data):
        tenant.Tenant(data).delete(self.session)

    def find_tenant(self, name_or_id):
        return tenant.Tenant.find(self.session, name_or_id)

    def get_tenant(self, **data):
        return tenant.Tenant(data).get(self.session)

    def list_tenants(self):
        return tenant.Tenant.list(self.session)

    def update_tenant(self, **data):
        return tenant.Tenant(data).update(self.session)

    def create_user(self, **data):
        return user.User(data).create(self.session)

    def delete_user(self, **data):
        user.User(data).delete(self.session)

    def find_user(self, name_or_id):
        return user.User.find(self.session, name_or_id)

    def get_user(self, **data):
        return user.User(data).get(self.session)

    def list_users(self):
        return user.User.list(self.session)

    def update_user(self, **data):
        return user.User(data).update(self.session)
