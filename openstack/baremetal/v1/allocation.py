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

from openstack.baremetal.v1 import _common
from openstack import exceptions
from openstack import resource
from openstack import utils


class Allocation(_common.ListMixin, resource.Resource):

    resources_key = 'allocations'
    base_path = '/allocations'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'node', 'resource_class', 'state',
        fields={'type': _common.fields_type},
    )

    # Allocation update is available since 1.57
    # Backfilling allocations is available since 1.58
    _max_microversion = '1.58'

    #: The candidate nodes for this allocation.
    candidate_nodes = resource.Body('candidate_nodes', type=list)
    #: Timestamp at which the allocation was created.
    created_at = resource.Body('created_at')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra', type=dict)
    #: The UUID for the allocation.
    id = resource.Body('uuid', alternate_id=True)
    #: The last error for the allocation.
    last_error = resource.Body("last_error")
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: The name of the allocation.
    name = resource.Body('name')
    #: The node UUID or name to create the allocation against,
    #: bypassing the normal allocation process.
    node = resource.Body('node')
    #: UUID of the node this allocation belongs to.
    node_id = resource.Body('node_uuid')
    #: The requested resource class.
    resource_class = resource.Body('resource_class')
    #: The state of the allocation.
    state = resource.Body('state')
    #: The requested traits.
    traits = resource.Body('traits', type=list)
    #: Timestamp at which the allocation was last updated.
    updated_at = resource.Body('updated_at')

    def wait(self, session, timeout=None, ignore_error=False):
        """Wait for the allocation to become active.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param timeout: How much (in seconds) to wait for the allocation.
            The value of ``None`` (the default) means no client-side timeout.
        :param ignore_error: If ``True``, this call will raise an exception
            if the allocation reaches the ``error`` state. Otherwise the error
            state is considered successful and the call returns.

        :return: This :class:`Allocation` instance.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if allocation
            fails and ``ignore_error`` is ``False``.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` on timeout.
        """
        if self.state == 'active':
            return self

        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for the allocation %s" % self.id):
            self.fetch(session)

            if self.state == 'error' and not ignore_error:
                raise exceptions.ResourceFailure(
                    "Allocation %(allocation)s failed: %(error)s" %
                    {'allocation': self.id, 'error': self.last_error})
            elif self.state != 'allocating':
                return self

            session.log.debug(
                'Still waiting for the allocation %(allocation)s '
                'to become active, the current state is %(state)s',
                {'allocation': self.id, 'state': self.state})
