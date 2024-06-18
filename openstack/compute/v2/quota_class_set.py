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


class QuotaClassSet(resource.Resource):
    resource_key = 'quota_class_set'
    base_path = '/os-quota-class-sets'

    _max_microversion = '2.56'

    # capabilities
    allow_fetch = True
    allow_commit = True

    #: Properties
    #: The number of allowed server cores for each tenant.
    cores = resource.Body('cores', type=int)
    #: The number of allowed fixed IP addresses for each tenant. Must be
    #: equal to or greater than the number of allowed servers.
    fixed_ips = resource.Body('fixed_ips', type=int)
    #: The number of allowed floating IP addresses for each tenant.
    floating_ips = resource.Body('floating_ips', type=int)
    #: The number of allowed bytes of content for each injected file.
    injected_file_content_bytes = resource.Body(
        'injected_file_content_bytes', type=int
    )
    #: The number of allowed bytes for each injected file path.
    injected_file_path_bytes = resource.Body(
        'injected_file_path_bytes', type=int
    )
    #: The number of allowed injected files for each tenant.
    injected_files = resource.Body('injected_files', type=int)
    #: The number of allowed servers for each tenant.
    instances = resource.Body('instances', type=int)
    #: The number of allowed key pairs for each user.
    key_pairs = resource.Body('key_pairs', type=int)
    #: The number of allowed metadata items for each server.
    metadata_items = resource.Body('metadata_items', type=int)
    #: The number of private networks that can be created per project.
    networks = resource.Body('networks', type=int)
    #: The amount of allowed server RAM, in MiB, for each tenant.
    ram = resource.Body('ram', type=int)
    #: The number of allowed rules for each security group.
    security_group_rules = resource.Body('security_group_rules', type=int)
    #: The number of allowed security groups for each tenant.
    security_groups = resource.Body('security_groups', type=int)
    #: The number of allowed server groups for each tenant.
    server_groups = resource.Body('server_groups', type=int)
    #: The number of allowed members for each server group.
    server_group_members = resource.Body('server_group_members', type=int)
