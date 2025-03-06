# Copyright 2019 Rackspace, US Inc.
#
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


class Amphora(resource.Resource):
    resource_key = 'amphora'
    resources_key = 'amphorae'
    base_path = '/octavia/amphorae'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'id',
        'loadbalancer_id',
        'compute_id',
        'lb_network_ip',
        'vrrp_ip',
        'ha_ip',
        'vrrp_port_id',
        'ha_port_id',
        'cert_expiration',
        'cert_busy',
        'role',
        'status',
        'vrrp_interface',
        'vrrp_id',
        'vrrp_priority',
        'cached_zone',
        'created_at',
        'updated_at',
        'image_id',
        'compute_flavor',
    )

    # Properties
    #: The ID of the amphora.
    id = resource.Body('id')
    #: The ID of the load balancer.
    loadbalancer_id = resource.Body('loadbalancer_id')
    #: The ID of the amphora resource in the compute system.
    compute_id = resource.Body('compute_id')
    #: The management IP of the amphora.
    lb_network_ip = resource.Body('lb_network_ip')
    #: The address of the vrrp port on the amphora.
    vrrp_ip = resource.Body('vrrp_ip')
    #: The IP address of the Virtual IP (VIP).
    ha_ip = resource.Body('ha_ip')
    #: The vrrp port's ID in the networking system.
    vrrp_port_id = resource.Body('vrrp_port_id')
    #: The ID of the Virtual IP (VIP) port.
    ha_port_id = resource.Body('ha_port_id')
    #: The date the certificate for the amphora expires.
    cert_expiration = resource.Body('cert_expiration')
    #: Whether the certificate is in the process of being replaced.
    cert_busy = resource.Body('cert_busy')
    #: The role configured for the amphora. One of STANDALONE, MASTER, BACKUP.
    role = resource.Body('role')
    #: The status of the amphora. One of: BOOTING, ALLOCATED, READY,
    #: PENDING_CREATE, PENDING_DELETE, DELETED, ERROR.
    status = resource.Body('status')
    #: The bound interface name of the vrrp port on the amphora.
    vrrp_interface = resource.Body('vrrp_interface')
    #: The vrrp group's ID for the amphora.
    vrrp_id = resource.Body('vrrp_id')
    #: The priority of the amphora in the vrrp group.
    vrrp_priority = resource.Body('vrrp_priority')
    #: The availability zone of a compute instance, cached at create time.
    cached_zone = resource.Body('cached_zone')
    #: The UTC date and timestamp when the resource was created.
    created_at = resource.Body('created_at')
    #: The UTC date and timestamp when the resource was last updated.
    updated_at = resource.Body('updated_at')
    #: The ID of the glance image used for the amphora.
    image_id = resource.Body('image_id')
    #: The ID of the compute flavor used for the amphora.
    compute_flavor = resource.Body('compute_flavor')

    def configure(self, session):
        """Configure load balancer.

        Update the amphora agent configuration. This will push the new
        configuration to the amphora agent and will update the configuration
        options that are mutatable.

        :param session: The session to use for making this request.
        :returns: None
        """
        session = self._get_session(session)
        version = self._get_microversion(session)
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'config')

        response = session.put(
            request.url,
            headers=request.headers,
            microversion=version,
        )

        msg = f"Failed to configure load balancer {self.id}"
        exceptions.raise_from_response(response, error_message=msg)

    def failover(self, session):
        """Failover load balancer.

        :param session: The session to use for making this request.
        :returns: None
        """
        session = self._get_session(session)
        version = self._get_microversion(session)
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'failover')

        response = session.put(
            request.url,
            headers=request.headers,
            microversion=version,
        )

        msg = f"Failed to failover load balancer {self.id}"
        exceptions.raise_from_response(response, error_message=msg)


# TODO(stephenfin): Delete this: it's useless
class AmphoraConfig(resource.Resource):
    base_path = '/octavia/amphorae/%(amphora_id)s/config'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = True
    allow_delete = False
    allow_list = False
    allow_empty_commit = True

    requires_id = False

    # Properties
    #: The ID of the amphora.
    amphora_id = resource.URI('amphora_id')

    # The default _update code path also has no way to pass has_body into this
    # function, so overriding the method here.
    def commit(
        self, session, prepend_key=True, has_body=False, *args, **kwargs
    ):
        return super().commit(session, prepend_key, has_body, *args, *kwargs)


# TODO(stephenfin): Delete this: it's useless
class AmphoraFailover(resource.Resource):
    base_path = '/octavia/amphorae/%(amphora_id)s/failover'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = True
    allow_delete = False
    allow_list = False
    allow_empty_commit = True

    requires_id = False

    # Properties
    #: The ID of the amphora.
    amphora_id = resource.URI('amphora_id')

    # The default _update code path also has no way to pass has_body into this
    # function, so overriding the method here.
    def commit(
        self, session, prepend_key=True, has_body=False, *args, **kwargs
    ):
        return super().commit(session, prepend_key, has_body, *args, *kwargs)
