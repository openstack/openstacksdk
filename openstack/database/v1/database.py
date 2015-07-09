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

from openstack.database import database_service
from openstack import resource


class Database(resource.Resource):
    id_attribute = 'name'
    resource_key = 'database'
    resources_key = 'databases'
    base_path = '/instances/%(instance_id)s/databases'
    service = database_service.DatabaseService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Set of symbols and encodings. The default character set is ``utf8``.
    character_set = resource.prop('character_set')
    #: Set of rules for comparing characters in a character set.
    #: The default value for collate is ``utf8_general_ci``.
    collate = resource.prop('collate')
    #: The ID of the instance
    instance_id = resource.prop('instance_id')
    #: The name of the database
    name = resource.prop('name')
