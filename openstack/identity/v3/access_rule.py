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


class AccessRule(resource.Resource):
    resource_key = 'access_rule'
    resources_key = 'access_rules'
    base_path = '/users/%(user_id)s/access_rules'

    # capabilities
    allow_fetch = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The links for the access rule resource.
    links = resource.Body('links')
    #: Method that application credential is permitted to use.
    # *Type: string*
    method = resource.Body('method')
    #: Path that the application credential is permitted to access.
    # *Type: string*
    path = resource.Body('path')
    #: Service type identifier that application credential had access.
    # *Type: string*
    service = resource.Body('service')
    #: User ID using access rule. *Type: string*
    user_id = resource.URI('user_id')
