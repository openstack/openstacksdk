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

from openstack.identity.v3 import credential
from openstack.identity.v3 import domain
from openstack.identity.v3 import endpoint
from openstack.identity.v3 import group
from openstack.identity.v3 import policy
from openstack.identity.v3 import project
from openstack.identity.v3 import service
from openstack.identity.v3 import user


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def create_credential(self, **data):
        return credential.Credential(data).create(self.session)

    def delete_credential(self, **data):
        credential.Credential(data).delete(self.session)

    def find_credential(self, name_or_id):
        return credential.Credential.find(self.session, name_or_id)

    def get_credential(self, **data):
        return credential.Credential(data).get(self.session)

    def list_credentials(self):
        return credential.Credential.list(self.session)

    def update_credential(self, **data):
        return credential.Credential(data).update(self.session)

    def create_domain(self, **data):
        return domain.Domain(data).create(self.session)

    def delete_domain(self, **data):
        domain.Domain(data).delete(self.session)

    def find_domain(self, name_or_id):
        return domain.Domain.find(self.session, name_or_id)

    def get_domain(self, **data):
        return domain.Domain(data).get(self.session)

    def list_domains(self):
        return domain.Domain.list(self.session)

    def update_domain(self, **data):
        return domain.Domain(data).update(self.session)

    def create_endpoint(self, **data):
        return endpoint.Endpoint(data).create(self.session)

    def delete_endpoint(self, **data):
        endpoint.Endpoint(data).delete(self.session)

    def find_endpoint(self, name_or_id):
        return endpoint.Endpoint.find(self.session, name_or_id)

    def get_endpoint(self, **data):
        return endpoint.Endpoint(data).get(self.session)

    def list_endpoints(self):
        return endpoint.Endpoint.list(self.session)

    def update_endpoint(self, **data):
        return endpoint.Endpoint(data).update(self.session)

    def create_group(self, **data):
        return group.Group(data).create(self.session)

    def delete_group(self, **data):
        group.Group(data).delete(self.session)

    def find_group(self, name_or_id):
        return group.Group.find(self.session, name_or_id)

    def get_group(self, **data):
        return group.Group(data).get(self.session)

    def list_groups(self):
        return group.Group.list(self.session)

    def update_group(self, **data):
        return group.Group(data).update(self.session)

    def create_policy(self, **data):
        return policy.Policy(data).create(self.session)

    def delete_policy(self, **data):
        policy.Policy(data).delete(self.session)

    def find_policy(self, name_or_id):
        return policy.Policy.find(self.session, name_or_id)

    def get_policy(self, **data):
        return policy.Policy(data).get(self.session)

    def list_policys(self):
        return policy.Policy.list(self.session)

    def update_policy(self, **data):
        return policy.Policy(data).update(self.session)

    def create_project(self, **data):
        return project.Project(data).create(self.session)

    def delete_project(self, **data):
        project.Project(data).delete(self.session)

    def find_project(self, name_or_id):
        return project.Project.find(self.session, name_or_id)

    def get_project(self, **data):
        return project.Project(data).get(self.session)

    def list_projects(self):
        return project.Project.list(self.session)

    def update_project(self, **data):
        return project.Project(data).update(self.session)

    def create_service(self, **data):
        return service.Service(data).create(self.session)

    def delete_service(self, **data):
        service.Service(data).delete(self.session)

    def find_service(self, name_or_id):
        return service.Service.find(self.session, name_or_id)

    def get_service(self, **data):
        return service.Service(data).get(self.session)

    def list_services(self):
        return service.Service.list(self.session)

    def update_service(self, **data):
        return service.Service(data).update(self.session)

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
