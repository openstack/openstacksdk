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


class ApplicationCredential(resource.Resource):
    resource_key = 'application_credential'
    resources_key = 'application_credentials'
    base_path = '/users/%(user_id)s/application_credentials'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: User ID using application credential. *Type: string*
    user_id = resource.URI('user_id')
    #: User object using application credential. *Type: string*
    user = resource.Body('user')
    #: The links for the application credential resource.
    links = resource.Body('links')
    #: name of the user. *Type: string*
    name = resource.Body('name')
    #: secret that application credential will be created with, if any.
    # *Type: string*
    secret = resource.Body('secret')
    #: description of application credential's purpose. *Type: string*
    description = resource.Body('description')
    #: expire time of application credential. *Type: string*
    expires_at = resource.Body('expires_at')
    #: roles of the user. *Type: list*
    roles = resource.Body('roles')
    #: restricts the application credential. *Type: boolean*
    unrestricted = resource.Body('unrestricted', type=bool)
    #: ID of project. *Type: string*
    project_id = resource.Body('project_id')
    #: access rules for application credential. *Type: list*
    access_rules = resource.Body('access_rules')
