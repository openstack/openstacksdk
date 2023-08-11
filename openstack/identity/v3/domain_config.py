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


class DomainConfigLDAP(resource.Resource):
    #: The base distinguished name (DN) of LDAP.
    user_tree_dn = resource.Body('user_tree_dn')
    #: The LDAP URL.
    url = resource.Body('url')


class DomainConfigDriver(resource.Resource):
    #: The Identity backend driver.
    driver = resource.Body('driver')


class DomainConfig(resource.Resource):
    resource_key = 'config'
    base_path = '/domains/%(domain_id)s/config'
    requires_id = False
    create_requires_id = False
    commit_method = 'PATCH'
    create_method = 'PUT'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True

    #: The domain ID.
    domain_id = resource.URI('domain_id')
    #: An identity object.
    identity = resource.Body('identity', type=DomainConfigDriver)
    #: The config object.
    ldap = resource.Body('ldap', type=DomainConfigLDAP)
