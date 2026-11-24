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

from keystoneauth1 import adapter

from openstack import exceptions
from openstack import resource
from openstack import utils


class StackSnapshot(resource.Resource):
    resource_key = 'snapshot'
    resources_key = 'snapshots'
    base_path = '/stacks/%(stack_name)s/%(stack_id)s/snapshots'

    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True
    allow_commit = False

    # Heat uses unwrapped bodies for creation, but wraps fetched snapshots.
    create_opts = resource.CreateOpts(request_key=None, response_key=None)

    #: The ID of the stack.
    stack_id = resource.URI('stack_id')
    #: The name of the stack.
    stack_name = resource.URI('stack_name')
    #: Creation time of the snapshot.
    created_at = resource.Body('creation_time')
    #: The status of the snapshot.
    status = resource.Body('status')
    #: The reason for the snapshot status.
    status_reason = resource.Body('status_reason')
    #: The data needed to restore the stack.
    data = resource.Body('data', type=dict)

    def restore(self, session: adapter.Adapter) -> None:
        """Restore the stack to this snapshot.

        :param session: The session to use for making this request.
        :returns: None. Restoration is asynchronous.
        :raises: :class:`~openstack.exceptions.HttpException` if the request
            fails.
        """
        session = self._get_session(session)
        request = self._prepare_request()
        response = session.post(utils.urljoin(request.url, 'restore'))
        exceptions.raise_from_response(response)
