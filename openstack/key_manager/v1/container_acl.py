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


class ContainerACL(resource.Resource):
    base_path = '/containers/%(container_id)s/acl'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = False

    # A container ACL is a singleton sub-resource living at a fixed path
    # (/containers/<container_id>/acl); it is never addressed by an id of
    # its own. Barbican creates/replaces the ACL with a PUT and partially
    # updates it with a PATCH.
    create_opts = resource.CreateOpts(method='PUT', requires_id=False)
    commit_method = 'PATCH'
    requires_id = False

    # Properties
    #: The ID of the container this ACL belongs to
    container_id = resource.URI('container_id')
    #: A URI for this container ACL
    acl_ref = resource.Body('acl_ref', type=str)
    #: Read operation settings, e.g.
    #: ``{'users': [str], 'project-access': bool}``.
    read = resource.Body('read', type=dict)
    #: The timestamp when this ACL was created (ISO 8601 format)
    created_at = resource.Body('created', type=str)
    #: The timestamp when this ACL was last updated (ISO 8601 format)
    updated_at = resource.Body('updated', type=str)
