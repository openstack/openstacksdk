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


class ClusterTemplate(resource.Resource):
    resources_key = 'clustertemplates'
    base_path = '/clustertemplates'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True

    commit_method = 'PATCH'
    commit_jsonpatch = True

    #: The exposed port of COE API server.
    apiserver_port = resource.Body('apiserver_port', type=int)
    #: Display the attribute os_distro defined as appropriate metadata in image
    #: for the bay/cluster driver.
    cluster_distro = resource.Body('cluster_distro')
    #: Specify the Container Orchestration Engine to use. Supported COEs
    #: include kubernetes, swarm, mesos.
    coe = resource.Body('coe')
    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: The name of a driver to manage the storage for the images and the
    #: container’s writable layer.
    docker_storage_driver = resource.Body('docker_storage_driver')
    #: The size in GB for the local storage on each server for the Docker
    #: daemon to cache the images and host the containers.
    docker_volume_size = resource.Body('docker_volume_size', type=int)
    #: The DNS nameserver for the servers and containers in the bay/cluster to
    #: use.
    dns_nameserver = resource.Body('dns_nameserver')
    #: The name or network ID of a Neutron network to provide connectivity to
    #: the external internet for the bay/cluster.
    external_network_id = resource.Body('external_network_id')
    #: The name or network ID of a Neutron network to provide connectivity to
    #: the internal network for the bay/cluster.
    fixed_network = resource.Body('fixed_network')
    #: Fixed subnet that are using to allocate network address for nodes in
    #: bay/cluster.
    fixed_subnet = resource.Body('fixed_subnet')
    #: The nova flavor ID or name for booting the node servers.
    flavor_id = resource.Body('flavor_id')
    #: The IP address for a proxy to use when direct http access
    #: from the servers to sites on the external internet is blocked.
    #: This may happen in certain countries or enterprises, and the
    #: proxy allows the servers and containers to access these sites.
    #: The format is a URL including a port number. The default is
    #: None.
    http_proxy = resource.Body('http_proxy')
    #: The IP address for a proxy to use when direct https access from the
    #: servers to sites on the external internet is blocked.
    https_proxy = resource.Body('https_proxy')
    #: The name or UUID of the base image in Glance to boot the servers for the
    #: bay/cluster.
    image_id = resource.Body('image_id')
    #: The URL pointing to users’s own private insecure docker
    #: registry to deploy and run docker containers.
    insecure_registry = resource.Body('insecure_registry')
    #: Whether enable or not using the floating IP of cloud provider.
    is_floating_ip_enabled = resource.Body('floating_ip_enabled')
    #: Indicates whether the ClusterTemplate is hidden or not.
    is_hidden = resource.Body('hidden', type=bool)
    #: this option can be set to false to create a bay/cluster without the load
    #: balancer.
    is_master_lb_enabled = resource.Body('master_lb_enabled', type=bool)
    #: Specifying this parameter will disable TLS so that users can access the
    #: COE endpoints without a certificate.
    is_tls_disabled = resource.Body('tls_disabled', type=bool)
    #: Setting this flag makes the baymodel/cluster template public and
    #: accessible by other users.
    is_public = resource.Body('public', type=bool)
    #: This option provides an alternative registry based on the Registry V2
    is_registry_enabled = resource.Body('registry_enabled', type=bool)
    #: The name of the SSH keypair to configure in the bay/cluster servers for
    #: ssh access.
    keypair_id = resource.Body('keypair_id')
    #: Arbitrary labels. The accepted keys and valid values are defined in the
    #: bay/cluster drivers. They are used as a way to pass additional
    #: parameters that are specific to a bay/cluster driver.
    labels = resource.Body('labels', type=dict)
    #: The flavor of the master node for this baymodel/cluster template.
    master_flavor_id = resource.Body('master_flavor_id')
    #: The name of a network driver for providing the networks for the
    #: containers.
    network_driver = resource.Body('network_driver')
    #: When a proxy server is used, some sites should not go through the proxy
    #: and should be accessed normally.
    no_proxy = resource.Body('no_proxy')
    #: The servers in the bay/cluster can be vm or baremetal.
    server_type = resource.Body('server_type')
    #: The date and time when the resource was updated.
    updated_at = resource.Body('updated_at')
    #: The UUID of the cluster template.
    uuid = resource.Body('uuid', alternate_id=True)
    #: The name of a volume driver for managing the persistent storage for the
    #: containers.
    volume_driver = resource.Body('volume_driver')
