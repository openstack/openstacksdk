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
        obj = project.Project(**data)
        obj.create(self.session)
        return obj

    def get_project(self, r_id):
        obj = project.Project({'id': r_id})
        obj.get(self.session)
        return obj

    def update_project(self, **data):
        obj = project.Project(**data)
        obj.update(self.session)

    def delete_project(self, r_id):
        obj = project.Project({'id': r_id})
        obj.delete(self.session)

    def list_projects(self, **params):
        return project.Project.list(self.session, **params)

    def find_project(self, name_or_id):
        return project.Project.find(self.session, name_or_id)
