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

from openstack.message import message_service
from openstack import resource


class Queue(resource.Resource):
    id_attribute = 'name'
    resources_key = 'queues'
    base_path = '/queues'
    service = message_service.MessageService()

    # capabilities
    allow_create = True
    allow_list = False
    allow_retrieve = False
    allow_delete = True

    @classmethod
    def create_by_id(cls, session, attrs, resource_id=None, path_args=None):
        url = cls._get_url(path_args, resource_id)
        headers = {'Accept': ''}
        session.put(url, endpoint_filter=cls.service, headers=headers)
        return {cls.id_attribute: resource_id}
