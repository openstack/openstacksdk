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

from openstack import resource


class Import(resource.Resource):
    base_path = '/info/import'

    # capabilities
    allow_fetch = True

    #: import methods
    import_methods = resource.Body('import-methods', type=dict)


class Store(resource.Resource):
    resources_key = 'stores'
    base_path = '/info/stores'

    # capabilities
    allow_list = True

    #: Description of the store
    description = resource.Body('description')
    #: default
    is_default = resource.Body('default', type=bool)
