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

from openstack.clustering.v1 import _async_resource
from openstack import resource
from openstack import utils


class Node(_async_resource.AsyncResource):
    resource_key = 'node'
    resources_key = 'nodes'
    base_path = '/nodes'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'show_details',
        'name',
        'sort',
        'global_project',
        'cluster_id',
        'status',
    )

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
    #: The domain ID of the node.
    domain_id = resource.Body('domain')
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
    #: Whether the node is tainted. *Type: bool*
    tainted = resource.Body('tainted', type=bool)

    def _action(self, session, body):
        """Procedure the invoke an action API.

        :param session: A session object used for sending request.
        :param body: The body of action to be sent.
        """
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, json=body)
        return resp.json()

    def check(self, session, **params):
        """An action procedure for the node to check its health status.

        :param session: A session object used for sending request.
        :returns: A dictionary containing the action ID.
        """
        body = {'check': params}
        return self._action(session, body)

    def recover(self, session, **params):
        """An action procedure for the node to recover.

        :param session: A session object used for sending request.
        :returns: A dictionary containing the action ID.
        """
        body = {'recover': params}
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
        resp = session.post(url, json={operation: params})
        return resp.json()

    def adopt(self, session, preview=False, **params):
        """Adopt a node for management.

        :param session: A session object used for sending request.
        :param preview: A boolean indicating whether the adoption is a
                        preview. A "preview" does not create the node object.
        :param dict params: A dict providing the details of a node to be
                            adopted.
        """
        if preview:
            path = 'adopt-preview'
            attrs = {
                'identity': params.get('identity'),
                'overrides': params.get('overrides'),
                'type': params.get('type'),
                'snapshot': params.get('snapshot'),
            }
        else:
            path = 'adopt'
            attrs = params

        url = utils.urljoin(self.base_path, path)
        resp = session.post(url, json=attrs)
        if preview:
            return resp.json()

        self._translate_response(resp)
        return self

    def force_delete(self, session):
        """Force delete a node."""
        body = {'force': True}
        url = utils.urljoin(self.base_path, self.id)
        response = session.delete(url, json=body)
        return self._delete_response(response)


class NodeDetail(Node):
    base_path = '/nodes/%(node_id)s?show_details=True'

    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = False

    node_id = resource.URI('node_id')
