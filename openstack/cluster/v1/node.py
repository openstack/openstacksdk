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

from openstack.cluster import cluster_service
from openstack import format
from openstack import resource
from openstack import utils


class Node(resource.Resource):
    resource_key = 'node'
    resources_key = 'nodes'
    base_path = '/nodes'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    patch_update = True

    # Properties
    #: The name of the node.
    name = resource.prop('name')
    #: The ID of the physical object that backs the node.
    physical_id = resource.prop('physical_id')
    #: The ID of the cluster in which this node is a member.
    #: A node is an orphan node if this field is empty.
    cluster_id = resource.prop('cluster_id')
    #: The ID of the profile used by this node.
    profile_id = resource.prop('profile_id')
    #: The ID of the project this node belongs to.
    project_id = resource.prop('project')
    #: The name of the profile used by this node.
    profile_name = resource.prop('profile_name')
    #: An integer that is unique inside the owning cluster.
    #: A value of -1 means this node is an orphan node.
    index = resource.prop('index', type=int)
    #: A string indicating the role the node plays in a cluster.
    role = resource.prop('role')
    #: The timestamp of the node object's initialization.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    init_at = resource.prop('init_at', type=format.ISO8601)
    #: The timestamp of the node's creation, i.e. the physical object
    #: represented by this node is also created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created_at', type=format.ISO8601)
    #: The timestamp the node was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_at', type=format.ISO8601)
    #: A string indicating the node's status.
    status = resource.prop('status')
    #: A string describing why the node entered its current status.
    status_reason = resource.prop('status_reason')
    #: A map containing key-value pairs attached to the node.
    metadata = resource.prop('tags', type=dict)
    #: A map containing some runtime data for this node.
    data = resource.prop('data', type=dict)
    #: A map containing the details of the physical object this node
    #: represents
    details = resource.prop('details', type=dict)

    def _action(self, session, body):
        """Procedure the invoke an action API.

        :param session: A session object used for sending request.
        :param body: The body of action to be sent.
        """
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json

    def check(self, session, **params):
        """An action procedure for the node to check its health status.

        :param session: A session object used for sending request.
        :returns: A dictionary containing the action ID.
        """
        body = {
            'check': params
        }
        return self._action(session, body)

    def recover(self, session, **params):
        """An action procedure for the node to recover.

        :param session: A session object used for sending request.
        :returns: A dictionary containing the action ID.
        """
        body = {
            'recover': params
        }
        return self._action(session, body)

    def delete(self, session):
        """Delete the remote resource associated with this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :returns: The instance of the Node which was deleted.
        :rtype: :class:`~openstack.cluster.v1.node.Node`.
        """
        url = self._get_url(self, self.id)
        resp = session.delete(url, endpoint_filter=self.service)
        self.location = resp.headers['location']
        return self
