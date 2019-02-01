# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import exceptions
from openstack import resource

from openstack.clustering.v1 import action as _action


class AsyncResource(resource.Resource):

    def delete(self, session, error_message=None):
        """Delete the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :return: An :class:`~openstack.clustering.v1.action.Action`
                 instance. The ``fetch`` method will need to be used
                 to populate the `Action` with status information.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_commit` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.ResourceNotFound` if
                 the resource was not found.
        """
        response = self._raw_delete(session)
        return self._delete_response(response, error_message)

    def _delete_response(self, response, error_message=None):
        exceptions.raise_from_response(response, error_message=error_message)
        location = response.headers['Location']
        action_id = location.split('/')[-1]
        action = _action.Action.existing(
            id=action_id,
            connection=self._connection)
        return action
