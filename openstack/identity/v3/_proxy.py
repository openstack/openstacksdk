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

from openstack.identity.v3 import project


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def create_project(self, **data):
        return project.Project(data).create(self.session)

    def delete_project(self, **data):
        project.Project(data).delete(self.session)

    def find_project(self, name_or_id):
        return project.Project.find(self.session, name_or_id)

    def get_project(self, **data):
        return project.Project(data).get(self.session)

    def list_projects(self, **params):
        return project.Project.list(self.session, **params)

    def update_project(self, **data):
        return project.Project(**data).update(self.session)
