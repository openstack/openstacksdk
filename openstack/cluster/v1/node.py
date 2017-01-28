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
from openstack import resource2 as resource
from openstack import utils


class Node(resource.Resource):
    resource_key = 'node'
    resources_key = 'nodes'
    base_path = '/nodes'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    patch_update = True

    _query_mapping = resource.QueryParameters(
        'show_details', 'name', 'sort', 'global_project', 'cluster_id',
        'status')

    # Properties
    #: The name of the node.
    name = resource.Body('name')
    #: The ID of the physical object that backs the node.
    physical_id = resource.Body('physical_id')
    #: The ID of the cluster in which this node is a member.
    #: A node is an orphan node if this field is empty.
    cluster_id = resource.Body('cluster_id')
    #: The ID of the profile used by this node.
    profile_id = resource.Body('profile_id')
    #: The ID of the user who created this node.
    user_id = resource.Body('user')
    #: The ID of the project this node belongs to.
    project_id = resource.Body('project')
    #: The name of the profile used by this node.
    profile_name = resource.Body('profile_name')
    #: An integer that is unique inside the owning cluster.
    #: A value of -1 means this node is an orphan node.
    index = resource.Body('index', type=int)
    #: A string indicating the role the node plays in a cluster.
    role = resource.Body('role')
    #: The timestamp of the node object's initialization.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    init_at = resource.Body('init_at')
    #: The timestamp of the node's creation, i.e. the physical object
    #: represented by this node is also created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.Body('created_at')
    #: The timestamp the node was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.Body('updated_at')
    #: A string indicating the node's status.
    status = resource.Body('status')
    #: A string describing why the node entered its current status.
    status_reason = resource.Body('status_reason')
    #: A map containing key-value pairs attached to the node.
    metadata = resource.Body('metadata', type=dict)
    #: A map containing some runtime data for this node.
    data = resource.Body('data', type=dict)
    #: A map containing the details of the physical object this node
    #: represents
    details = resource.Body('details', type=dict)
    #: A map containing the dependency of nodes
    dependents = resource.Body('dependents', type=dict)

    def _action(self, session, body):
        """Procedure the invoke an action API.

        :param session: A session object used for sending request.
        :param body: The body of action to be sent.
        """
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

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

    def op(self, session, operation, **params):
        """Perform an operation on the specified node.

        :param session: A session object used for sending request.
        :param operation: A string representing the operation to be performed.
        :param dict params: An optional dict providing the parameters for the
                            operation.
        :returns: A dictionary containing the action ID.
        """
        url = utils.urljoin(self.base_path, self.id, 'ops')
        resp = session.post(url, endpoint_filter=self.service,
                            json={operation: params})
        return resp.json()


class NodeDetail(Node):
    base_path = '/nodes/%(node_id)s?show_details=True'

    allow_create = False
    allow_get = True
    allow_update = False
    allow_delete = False
    allow_list = False

    node_id = resource.URI('node_id')
