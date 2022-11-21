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


class MetadefResourceType(resource.Resource):
    resources_key = 'resource_types'
    base_path = '/metadefs/resource_types'

    # capabilities
    allow_list = True

    #: The name of metadata definition resource type
    name = resource.Body('name', alternate_id=True)
    #: The date and time when the resource type was created.
    created_at = resource.Body('created_at')
    #: The date and time when the resource type was updated.
    updated_at = resource.Body('updated_at')


class MetadefResourceTypeAssociation(resource.Resource):
    resources_key = 'resource_type_associations'
    base_path = '/metadefs/namespaces/%(namespace_name)s/resource_types'

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True

    #: The name of the namespace whose details you want to see.
    namespace_name = resource.URI('namespace_name')
    #: The name of metadata definition resource type
    name = resource.Body('name', alternate_id=True)
    #: The date and time when the resource type was created.
    created_at = resource.Body('created_at')
    #: The date and time when the resource type was updated.
    updated_at = resource.Body('updated_at')
    #: Prefix for any properties in the namespace that you want to apply
    #: to the resource type. If you specify a prefix, you must append
    #: a prefix separator, such as the colon (:) character.
    prefix = resource.Body('prefix')
    #: Some resource types allow more than one key and value pair
    #: for each instance.  For example, the Image service allows
    #: both user and image metadata on volumes. The properties_target parameter
    #: enables a namespace target to remove the ambiguity
    properties_target = resource.Body('properties_target')
