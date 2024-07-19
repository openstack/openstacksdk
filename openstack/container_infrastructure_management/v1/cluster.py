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

from openstack import exceptions
from openstack import resource
from openstack import utils


class Cluster(resource.Resource):
    resources_key = 'clusters'
    base_path = '/clusters'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True

    commit_method = 'PATCH'
    commit_jsonpatch = True

    #: The endpoint URL of COE API exposed to end-users.
    api_address = resource.Body('api_address')
    #: The UUID of the cluster template.
    cluster_template_id = resource.Body('cluster_template_id')
    #: Version info of chosen COE in bay/cluster for helping client in picking
    #: the right version of client.
    coe_version = resource.Body('coe_version')
    #: The timeout for cluster creation in minutes. The value expected is a
    #: positive integer. If the timeout is reached during cluster creation
    #: process, the operation will be aborted and the cluster status will be
    #: set to CREATE_FAILED. Defaults to 60.
    create_timeout = resource.Body('create_timeout', type=int)
    #: The date and time when the resource was created. The date and time stamp
    #: format is ISO 8601::
    #:
    #:     CCYY-MM-DDThh:mm:ss±hh:mm
    #:
    #: For example, `2015-08-27T09:49:58-05:00`. The ±hh:mm value, if included,
    #: is the time zone as an offset from UTC.
    created_at = resource.Body('created_at')
    #: The custom discovery url for node discovery. This is used by the COE to
    #: discover the servers that have been created to host the containers. The
    #: actual discovery mechanism varies with the COE. In some cases, the
    #: service fills in the server info in the discovery service. In other
    #: cases,if the discovery_url is not specified, the service will use the
    #: public discovery service at https://discovery.etcd.io. In this case, the
    #: service will generate a unique url here for each bay and store the info
    #: for the servers.
    discovery_url = resource.Body('discovery_url')
    #: The name or ID of the network to provide connectivity to the internal
    #: network for the bay/cluster.
    fixed_network = resource.Body('fixed_network')
    #: The fixed subnet to use when allocating network addresses for nodes in
    #: bay/cluster.
    fixed_subnet = resource.Body('fixed_subnet')
    #: The flavor name or ID to use when booting the node servers. Defaults to
    #: m1.small.
    flavor_id = resource.Body('flavor_id')
    #: Whether to enable using the floating IP of cloud provider. Some cloud
    #: providers use floating IPs while some use public IPs. When set to true,
    #: floating IPs will be used. If this value is not provided, the value of
    #: ``floating_ip_enabled`` provided in the template will be used.
    is_floating_ip_enabled = resource.Body('floating_ip_enabled', type=bool)
    #: Whether to enable the master load balancer. Since multiple masters may
    #: exist in a bay/cluster, a Neutron load balancer is created to provide
    #: the API endpoint for the bay/cluster and to direct requests to the
    #: masters. In some cases, such as when the LBaaS service is not available,
    #: this option can be set to false to create a bay/cluster without the load
    #: balancer. In this case, one of the masters will serve as the API
    #: endpoint. The default is true, i.e. to create the load balancer for the
    #: bay.
    is_master_lb_enabled = resource.Body('master_lb_enabled', type=bool)
    #: The name of the SSH keypair to configure in the bay/cluster servers for
    #: SSH access. Users will need the key to be able to ssh to the servers in
    #: the bay/cluster. The login name is specific to the bay/cluster driver.
    #: For example, with fedora-atomic image the default login name is fedora.
    keypair = resource.Body('keypair')
    #: Arbitrary labels. The accepted keys and valid values are defined in the
    #: bay/cluster drivers. They are used as a way to pass additional
    #: parameters that are specific to a bay/cluster driver.
    labels = resource.Body('labels', type=dict)
    #: A list of floating IPs of all master nodes.
    master_addresses = resource.Body('master_addresses', type=list)
    #: The number of servers that will serve as master for the bay/cluster. Set
    #: to more than 1 master to enable High Availability. If the option
    #: master-lb-enabled is specified in the baymodel/cluster template, the
    #: master servers will be placed in a load balancer pool. Defaults to 1.
    master_count = resource.Body('master_count', type=int)
    #: The flavor of the master node for this baymodel/cluster template.
    master_flavor_id = resource.Body('master_flavor_id')
    #: Name of the resource.
    name = resource.Body('name')
    #: The number of servers that will serve as node in the bay/cluster.
    #: Defaults to 1.
    node_count = resource.Body('node_count', type=int)
    #: A list of floating IPs of all servers that serve as nodes.
    node_addresses = resource.Body('node_addresses', type=list)
    #: The reference UUID of orchestration stack from Heat orchestration
    #: service.
    stack_id = resource.Body('stack_id')
    #: The current state of the bay/cluster.
    status = resource.Body('status')
    #: The reason of bay/cluster current status.
    status_reason = resource.Body('reason')
    #: The date and time when the resource was updated. The date and time stamp
    #: format is ISO 8601::
    #:
    #:     CCYY-MM-DDThh:mm:ss±hh:mm
    #:
    #: For example, `2015-08-27T09:49:58-05:00`. The ±hh:mm value, if included,
    #: is the time zone as an offset from UTC. If the updated_at date and time
    #: stamp is not set, its value is null.
    updated_at = resource.Body('updated_at')
    #: The UUID of the cluster.
    uuid = resource.Body('uuid', alternate_id=True)

    def resize(self, session, *, node_count, nodes_to_remove=None):
        """Resize the cluster.

        :param node_count: The number of servers that will serve as node in the
            bay/cluster. The default is 1.
        :param nodes_to_remove: The server ID list will be removed if
            downsizing the cluster.
        :returns: The UUID of the resized cluster.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
            the resource was not found.
        """
        url = utils.urljoin(Cluster.base_path, self.id, 'actions', 'resize')
        headers = {'Accept': ''}
        body = {
            'node_count': node_count,
            'nodes_to_remove': nodes_to_remove,
        }
        response = session.post(url, json=body, headers=headers)
        exceptions.raise_from_response(response)
        return response['uuid']

    def upgrade(self, session, *, cluster_template, max_batch_size=None):
        """Upgrade the cluster.

        :param cluster_template: The UUID of the cluster template.
        :param max_batch_size: The max batch size each time when doing upgrade.
            The default is 1
        :returns: The UUID of the updated cluster.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
            the resource was not found.
        """
        url = utils.urljoin(Cluster.base_path, self.id, 'actions', 'upgrade')
        headers = {'Accept': ''}
        body = {
            'cluster_template': cluster_template,
            'max_batch_size': max_batch_size,
        }
        response = session.post(url, json=body, headers=headers)
        exceptions.raise_from_response(response)
        return response['uuid']
