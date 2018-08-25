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


class AutoAllocatedTopology(resource.Resource):
    resource_name = 'auto_allocated_topology'
    resource_key = 'auto_allocated_topology'
    base_path = '/auto-allocated-topology'

    # Capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = False

    # NOTE: this resource doesn't support list or query

    # Properties
    #: Project ID
    #: If project is not specified the topology will be created
    #: for project user is authenticated against.
    #: Will return in error if resources have not been configured correctly
    #: To use this feature auto-allocated-topology, subnet_allocation,
    #: external-net and router extensions must be enabled and set up.
    project_id = resource.Body('tenant_id')


class ValidateTopology(AutoAllocatedTopology):
    base_path = '/auto-allocated-topology/%(project)s?fields=dry-run'

    #: Validate requirements before running (Does not return topology)
    #: Will return "Deployment error:" if the resources required have not
    #: been correctly set up.
    dry_run = resource.Body('dry_run')
    project = resource.URI('project')
