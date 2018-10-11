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

from openstack import resource
from openstack import utils


class Cluster(resource.Resource):
    resource_key = 'cluster'
    resources_key = 'clusters'
    base_path = '/clusters'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'name', 'status', 'sort', 'global_project')

    # Properties
    #: The name of the cluster.
    name = resource.Body('name')
    #: The ID of the profile used by this cluster.
    profile_id = resource.Body('profile_id')
    #: The ID of the user who created this cluster, thus the owner of it.
    user_id = resource.Body('user')
    #: The ID of the project this cluster belongs to.
    project_id = resource.Body('project')
    #: The domain ID of the cluster owner.
    domain_id = resource.Body('domain')
    #: Timestamp of when the cluster was initialized.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    init_at = resource.Body('init_at')
    #: Timestamp of when the cluster was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.Body('created_at')
    #: Timestamp of when the cluster was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.Body('updated_at')
    #: Lower bound (inclusive) for the size of the cluster.
    min_size = resource.Body('min_size', type=int)
    #: Upper bound (inclusive) for the size of the cluster. A value of
    #: -1 indicates that there is no upper limit of cluster size.
    max_size = resource.Body('max_size', type=int)
    #: Desired capacity for the cluster. A cluster would be created at the
    #: scale specified by this value.
    desired_capacity = resource.Body('desired_capacity', type=int)
    #: Default timeout (in seconds) for cluster operations.
    timeout = resource.Body('timeout')
    #: A string representation of the cluster status.
    status = resource.Body('status')
    #: A string describing the reason why the cluster in current status.
    status_reason = resource.Body('status_reason')
    #: A dictionary configuration for cluster.
    config = resource.Body('config', type=dict)
    #: A collection of key-value pairs that are attached to the cluster.
    metadata = resource.Body('metadata', type=dict)
    #: A dictionary with some runtime data associated with the cluster.
    data = resource.Body('data', type=dict)
    #: A list IDs of nodes that are members of the cluster.
    node_ids = resource.Body('nodes')
    #: Name of the profile used by the cluster.
    profile_name = resource.Body('profile_name')
    #: Specify whether the cluster update should only pertain to the profile.
    is_profile_only = resource.Body('profile_only', type=bool)
    #: A dictionary with dependency information of the cluster
    dependents = resource.Body('dependents', type=dict)

    def action(self, session, body):
        url = utils.urljoin(self.base_path, self._get_id(self), 'actions')
        resp = session.post(url, json=body)
        return resp.json()

    def add_nodes(self, session, nodes):
        body = {
            'add_nodes': {
                'nodes': nodes,
            }
        }
        return self.action(session, body)

    def del_nodes(self, session, nodes, **params):
        data = {'nodes': nodes}
        data.update(params)
        body = {
            'del_nodes': data
        }
        return self.action(session, body)

    def replace_nodes(self, session, nodes):
        body = {
            'replace_nodes': {
                'nodes': nodes,
            }
        }
        return self.action(session, body)

    def scale_out(self, session, count=None):
        body = {
            'scale_out': {
                'count': count,
            }
        }
        return self.action(session, body)

    def scale_in(self, session, count=None):
        body = {
            'scale_in': {
                'count': count,
            }
        }
        return self.action(session, body)

    def resize(self, session, **params):
        body = {
            'resize': params
        }
        return self.action(session, body)

    def policy_attach(self, session, policy_id, **params):
        data = {'policy_id': policy_id}
        data.update(params)
        body = {
            'policy_attach': data
        }
        return self.action(session, body)

    def policy_detach(self, session, policy_id):
        body = {
            'policy_detach': {
                'policy_id': policy_id,
            }
        }
        return self.action(session, body)

    def policy_update(self, session, policy_id, **params):
        data = {'policy_id': policy_id}
        data.update(params)
        body = {
            'policy_update': data
        }
        return self.action(session, body)

    def check(self, session, **params):
        body = {
            'check': params
        }
        return self.action(session, body)

    def recover(self, session, **params):
        body = {
            'recover': params
        }
        return self.action(session, body)

    def op(self, session, operation, **params):
        """Perform an operation on the cluster.

        :param session: A session object used for sending request.
        :param operation: A string representing the operation to be performed.
        :param dict params: An optional dict providing the parameters for the
                            operation.
        :returns: A dictionary containing the action ID.
        """
        url = utils.urljoin(self.base_path, self.id, 'ops')
        resp = session.post(url,
                            json={operation: params})
        return resp.json()

    def force_delete(self, session):
        """Force delete a cluster."""
        body = {'force': True}
        url = utils.urljoin(self.base_path, self.id)
        resp = session.delete(url, json=body)
        self._translate_response(resp, has_body=False)
        return self
