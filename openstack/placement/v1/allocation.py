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


class Allocation(resource.Resource):
    """Allocations for a single consumer.

    Allocations are records representing resources that have been assigned and
    used by a consumer of those resources. The consumer is identified by its
    UUID, which serves as the resource ID in the URL
    (``/allocations/{consumer_uuid}``).

    An allocation maps resource providers to the resources consumed from them.
    Each entry in the ``allocations`` dict is keyed by resource provider UUID
    and contains a ``resources`` sub-dict mapping resource class names to
    quantities.
    """

    resource_key = None
    resources_key = None
    base_path = '/allocations'

    # Capabilities

    allow_fetch = True
    allow_commit = True
    allow_delete = True

    # The consumer_type field was introduced in 1.38
    _max_microversion = '1.38'

    _query_mapping = resource.QueryParameters(
        include_pagination_defaults=False,
    )

    # Properties

    #: A dictionary of resource allocations keyed by resource provider UUID.
    #: Each value is a dict with a ``resources`` key mapping resource class
    #: names to quantities, e.g.
    #: ``{"DISK_GB": 4, "VCPU": 2}``.
    #: Setting this to an empty dict removes all allocations for the consumer.
    allocations = resource.Body('allocations', type=dict)
    #: The generation of the consumer. Should be set to ``None`` when
    #: indicating that the caller expects the consumer does not yet exist.
    consumer_generation = resource.Body('consumer_generation')
    #: A string that consists of numbers, A-Z, and _ describing what kind of
    #: consumer is creating, or has created, allocations using a quantity of
    #: inventory. The string is determined by the client when writing
    #: allocations and it is up to the client to ensure correct choices amongst
    #: collaborating services. For example, the compute service may choose to
    #: type some consumers 'INSTANCE' and others 'MIGRATION'.
    consumer_type = resource.Body('consumer_type')
    #: The UUID of a project.
    project_id = resource.Body('project_id')
    #: The UUID of a user.
    user_id = resource.Body('user_id')
