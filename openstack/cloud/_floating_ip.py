# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import ipaddress
# import jsonpatch
import threading
import time
import types  # noqa

from openstack.cloud import exc
from openstack.cloud import meta
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import exceptions
from openstack import proxy
from openstack import utils

_CONFIG_DOC_URL = (
    "https://docs.openstack.org/openstacksdk/latest/"
    "user/config/configuration.html")


class FloatingIPCloudMixin(_normalize.Normalizer):

    def __init__(self):
        self.private = self.config.config.get('private', False)

        self._floating_ip_source = self.config.config.get(
            'floating_ip_source')
        if self._floating_ip_source:
            if self._floating_ip_source.lower() == 'none':
                self._floating_ip_source = None
            else:
                self._floating_ip_source = self._floating_ip_source.lower()

        self._floating_ips = None
        self._floating_ips_time = 0
        self._floating_ips_lock = threading.Lock()

        self._floating_network_by_router = None
        self._floating_network_by_router_run = False
        self._floating_network_by_router_lock = threading.Lock()

    def search_floating_ip_pools(self, name=None, filters=None):
        pools = self.list_floating_ip_pools()
        return _utils._filter_list(pools, name, filters)

    # With Neutron, there are some cases in which full server side filtering is
    # not possible (e.g. nested attributes or list of objects) so we also need
    # to use the client-side filtering
    # The same goes for all neutron-related search/get methods!
    def search_floating_ips(self, id=None, filters=None):
        # `filters` could be a jmespath expression which Neutron server doesn't
        # understand, obviously.
        if self._use_neutron_floating() and isinstance(filters, dict):
            filter_keys = ['router_id', 'status', 'tenant_id', 'project_id',
                           'revision_number', 'description',
                           'floating_network_id', 'fixed_ip_address',
                           'floating_ip_address', 'port_id', 'sort_dir',
                           'sort_key', 'tags', 'tags-any', 'not-tags',
                           'not-tags-any', 'fields']
            neutron_filters = {k: v for k, v in filters.items()
                               if k in filter_keys}
            kwargs = {'filters': neutron_filters}
        else:
            kwargs = {}
        floating_ips = self.list_floating_ips(**kwargs)
        return _utils._filter_list(floating_ips, id, filters)

    def _neutron_list_floating_ips(self, filters=None):
        if not filters:
            filters = {}
        data = self.network.get('/floatingips.json', params=filters)
        return self._get_and_munchify('floatingips', data)

    def _nova_list_floating_ips(self):
        try:
            data = proxy._json_response(
                self.compute.get('/os-floating-ips'))
        except exc.OpenStackCloudURINotFound:
            return []
        return self._get_and_munchify('floating_ips', data)

    def get_floating_ip(self, id, filters=None):
        """Get a floating IP by ID

        :param id: ID of the floating IP.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A floating IP ``munch.Munch`` or None if no matching floating
                  IP is found.

        """
        return _utils._get_entity(self, 'floating_ip', id, filters)

    def _list_floating_ips(self, filters=None):
        if self._use_neutron_floating():
            try:
                return self._normalize_floating_ips(
                    self._neutron_list_floating_ips(filters))
            except exc.OpenStackCloudURINotFound as e:
                # Nova-network don't support server-side floating ips
                # filtering, so it's safer to return and empty list than
                # to fallback to Nova which may return more results that
                # expected.
                if filters:
                    self.log.error(
                        "Neutron returned NotFound for floating IPs, which"
                        " means this cloud doesn't have neutron floating ips."
                        " shade can't fallback to trying Nova since nova"
                        " doesn't support server-side filtering when listing"
                        " floating ips and filters were given. If you do not"
                        " think shade should be attempting to list floating"
                        " ips on neutron, it is possible to control the"
                        " behavior by setting floating_ip_source to 'nova' or"
                        " None for cloud: %(cloud)s. If you are not already"
                        " using clouds.yaml to configure settings for your"
                        " cloud(s), and you want to configure this setting,"
                        " you will need a clouds.yaml file. For more"
                        " information, please see %(doc_url)s", {
                            'cloud': self.name,
                            'doc_url': _CONFIG_DOC_URL,
                        }
                    )
                    # We can't fallback to nova because we push-down filters.
                    # We got a 404 which means neutron doesn't exist. If the
                    # user
                    return []
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova
        else:
            if filters:
                raise ValueError(
                    "Nova-network don't support server-side floating ips "
                    "filtering. Use the search_floatting_ips method instead"
                )

        floating_ips = self._nova_list_floating_ips()
        return self._normalize_floating_ips(floating_ips)

    def list_floating_ip_pools(self):
        """List all available floating IP pools.

        NOTE: This function supports the nova-net view of the world. nova-net
        has been deprecated, so it's highly recommended to switch to using
        neutron. `get_external_ipv4_floating_networks` is what you should
        almost certainly be using.

        :returns: A list of floating IP pool ``munch.Munch``.

        """
        if not self._has_nova_extension('os-floating-ip-pools'):
            raise exc.OpenStackCloudUnavailableExtension(
                'Floating IP pools extension is not available on target cloud')

        data = proxy._json_response(
            self.compute.get('os-floating-ip-pools'),
            error_message="Error fetching floating IP pool list")
        pools = self._get_and_munchify('floating_ip_pools', data)
        return [{'name': p['name']} for p in pools]

    def list_floating_ips(self, filters=None):
        """List all available floating IPs.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of floating IP ``munch.Munch``.

        """
        # If pushdown filters are specified and we do not have batched caching
        # enabled, bypass local caching and push down the filters.
        if filters and self._FLOAT_AGE == 0:
            return self._list_floating_ips(filters)

        if (time.time() - self._floating_ips_time) >= self._FLOAT_AGE:
            # Since we're using cached data anyway, we don't need to
            # have more than one thread actually submit the list
            # floating ips task.  Let the first one submit it while holding
            # a lock, and the non-blocking acquire method will cause
            # subsequent threads to just skip this and use the old
            # data until it succeeds.
            # Initially when we never got data, block to retrieve some data.
            first_run = self._floating_ips is None
            if self._floating_ips_lock.acquire(first_run):
                try:
                    if not (first_run and self._floating_ips is not None):
                        self._floating_ips = self._list_floating_ips()
                        self._floating_ips_time = time.time()
                finally:
                    self._floating_ips_lock.release()
        # Wrap the return with filter_list so that if filters were passed
        # but we were batching/caching and thus always fetching the whole
        # list from the cloud, we still return a filtered list.
        return _utils._filter_list(self._floating_ips, None, filters)

    def get_floating_ip_by_id(self, id):
        """ Get a floating ip by ID

        :param id: ID of the floating ip.
        :returns: A floating ip ``munch.Munch``.
        """
        error_message = "Error getting floating ip with ID {id}".format(id=id)

        if self._use_neutron_floating():
            data = proxy._json_response(
                self.network.get('/floatingips/{id}'.format(id=id)),
                error_message=error_message)
            return self._normalize_floating_ip(
                self._get_and_munchify('floatingip', data))
        else:
            data = proxy._json_response(
                self.compute.get('/os-floating-ips/{id}'.format(id=id)),
                error_message=error_message)
            return self._normalize_floating_ip(
                self._get_and_munchify('floating_ip', data))

    def _neutron_available_floating_ips(
            self, network=None, project_id=None, server=None):
        """Get a floating IP from a network.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param network: A single network name or ID, or a list of them.
        :param server: (server) Server the Floating IP is for

        :returns: a list of floating IP addresses.

        :raises: ``OpenStackCloudResourceNotFound``, if an external network
                 that meets the specified criteria cannot be found.
        """
        if project_id is None:
            # Make sure we are only listing floatingIPs allocated the current
            # tenant. This is the default behaviour of Nova
            project_id = self.current_project_id

        if network:
            if isinstance(network, str):
                network = [network]

            # Use given list to get first matching external network
            floating_network_id = None
            for net in network:
                for ext_net in self.get_external_ipv4_floating_networks():
                    if net in (ext_net['name'], ext_net['id']):
                        floating_network_id = ext_net['id']
                        break
                if floating_network_id:
                    break

            if floating_network_id is None:
                raise exc.OpenStackCloudResourceNotFound(
                    "unable to find external network {net}".format(
                        net=network)
                )
        else:
            floating_network_id = self._get_floating_network_id()

        filters = {
            'port': None,
            'network': floating_network_id,
            'location': {'project': {'id': project_id}},
        }

        floating_ips = self._list_floating_ips()
        available_ips = _utils._filter_list(
            floating_ips, name_or_id=None, filters=filters)
        if available_ips:
            return available_ips

        # No available IP found or we didn't try
        # allocate a new Floating IP
        f_ip = self._neutron_create_floating_ip(
            network_id=floating_network_id, server=server)

        return [f_ip]

    def _nova_available_floating_ips(self, pool=None):
        """Get available floating IPs from a floating IP pool.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param pool: Nova floating IP pool name.

        :returns: a list of floating IP addresses.

        :raises: ``OpenStackCloudResourceNotFound``, if a floating IP pool
                 is not specified and cannot be found.
        """

        with _utils.shade_exceptions(
                "Unable to create floating IP in pool {pool}".format(
                    pool=pool)):
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise exc.OpenStackCloudResourceNotFound(
                        "unable to find a floating ip pool")
                pool = pools[0]['name']

            filters = {
                'instance_id': None,
                'pool': pool
            }

            floating_ips = self._nova_list_floating_ips()
            available_ips = _utils._filter_list(
                floating_ips, name_or_id=None, filters=filters)
            if available_ips:
                return available_ips

            # No available IP found or we did not try.
            # Allocate a new Floating IP
            f_ip = self._nova_create_floating_ip(pool=pool)

            return [f_ip]

    def _find_floating_network_by_router(self):
        """Find the network providing floating ips by looking at routers."""

        if self._floating_network_by_router_lock.acquire(
                not self._floating_network_by_router_run):
            if self._floating_network_by_router_run:
                self._floating_network_by_router_lock.release()
                return self._floating_network_by_router
            try:
                for router in self.list_routers():
                    if router['admin_state_up']:
                        network_id = router.get(
                            'external_gateway_info', {}).get('network_id')
                        if network_id:
                            self._floating_network_by_router = network_id
            finally:
                self._floating_network_by_router_run = True
                self._floating_network_by_router_lock.release()
        return self._floating_network_by_router

    def available_floating_ip(self, network=None, server=None):
        """Get a floating IP from a network or a pool.

        Return the first available floating IP or allocate a new one.

        :param network: Name or ID of the network.
        :param server: Server the IP is for if known

        :returns: a (normalized) structure with a floating IP address
                  description.
        """
        if self._use_neutron_floating():
            try:
                f_ips = self._normalize_floating_ips(
                    self._neutron_available_floating_ips(
                        network=network, server=server))
                return f_ips[0]
            except exc.OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova

        f_ips = self._normalize_floating_ips(
            self._nova_available_floating_ips(pool=network)
        )
        return f_ips[0]

    def _get_floating_network_id(self):
        # Get first existing external IPv4 network
        networks = self.get_external_ipv4_floating_networks()
        if networks:
            floating_network_id = networks[0]['id']
        else:
            floating_network = self._find_floating_network_by_router()
            if floating_network:
                floating_network_id = floating_network
            else:
                raise exc.OpenStackCloudResourceNotFound(
                    "unable to find an external network")
        return floating_network_id

    def create_floating_ip(self, network=None, server=None,
                           fixed_address=None, nat_destination=None,
                           port=None, wait=False, timeout=60):
        """Allocate a new floating IP from a network or a pool.

        :param network: Name or ID of the network
                        that the floating IP should come from.
        :param server: (optional) Server dict for the server to create
                       the IP for and to which it should be attached.
        :param fixed_address: (optional) Fixed IP to attach the floating
                              ip to.
        :param nat_destination: (optional) Name or ID of the network
                                that the fixed IP to attach the floating
                                IP to should be on.
        :param port: (optional) The port ID that the floating IP should be
                                attached to. Specifying a port conflicts
                                with specifying a server, fixed_address or
                                nat_destination.
        :param wait: (optional) Whether to wait for the IP to be active.
                     Defaults to False. Only applies if a server is
                     provided.
        :param timeout: (optional) How long to wait for the IP to be active.
                        Defaults to 60. Only applies if a server is
                        provided.

        :returns: a floating IP address

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self._use_neutron_floating():
            try:
                return self._neutron_create_floating_ip(
                    network_name_or_id=network, server=server,
                    fixed_address=fixed_address,
                    nat_destination=nat_destination,
                    port=port,
                    wait=wait, timeout=timeout)
            except exc.OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova

        if port:
            raise exc.OpenStackCloudException(
                "This cloud uses nova-network which does not support"
                " arbitrary floating-ip/port mappings. Please nudge"
                " your cloud provider to upgrade the networking stack"
                " to neutron, or alternately provide the server,"
                " fixed_address and nat_destination arguments as appropriate")
        # Else, we are using Nova network
        f_ips = self._normalize_floating_ips(
            [self._nova_create_floating_ip(pool=network)])
        return f_ips[0]

    def _submit_create_fip(self, kwargs):
        # Split into a method to aid in test mocking
        data = self.network.post(
            "/floatingips.json", json={"floatingip": kwargs})
        return self._normalize_floating_ip(
            self._get_and_munchify('floatingip', data))

    def _neutron_create_floating_ip(
            self, network_name_or_id=None, server=None,
            fixed_address=None, nat_destination=None,
            port=None,
            wait=False, timeout=60, network_id=None):

        if not network_id:
            if network_name_or_id:
                network = self.get_network(network_name_or_id)
                if not network:
                    raise exc.OpenStackCloudResourceNotFound(
                        "unable to find network for floating ips with ID "
                        "{0}".format(network_name_or_id))
                network_id = network['id']
            else:
                network_id = self._get_floating_network_id()
        kwargs = {
            'floating_network_id': network_id,
        }
        if not port:
            if server:
                (port_obj, fixed_ip_address) = self._nat_destination_port(
                    server, fixed_address=fixed_address,
                    nat_destination=nat_destination)
                if port_obj:
                    port = port_obj['id']
                if fixed_ip_address:
                    kwargs['fixed_ip_address'] = fixed_ip_address
        if port:
            kwargs['port_id'] = port

        fip = self._submit_create_fip(kwargs)
        fip_id = fip['id']

        if port:
            # The FIP is only going to become active in this context
            # when we've attached it to something, which only occurs
            # if we've provided a port as a parameter
            if wait:
                try:
                    for count in utils.iterate_timeout(
                            timeout,
                            "Timeout waiting for the floating IP"
                            " to be ACTIVE",
                            wait=self._FLOAT_AGE):
                        fip = self.get_floating_ip(fip_id)
                        if fip and fip['status'] == 'ACTIVE':
                            break
                except exc.OpenStackCloudTimeout:
                    self.log.error(
                        "Timed out on floating ip %(fip)s becoming active."
                        " Deleting", {'fip': fip_id})
                    try:
                        self.delete_floating_ip(fip_id)
                    except Exception as e:
                        self.log.error(
                            "FIP LEAK: Attempted to delete floating ip "
                            "%(fip)s but received %(exc)s exception: "
                            "%(err)s", {'fip': fip_id, 'exc': e.__class__,
                                        'err': str(e)})
                    raise
            if fip['port_id'] != port:
                if server:
                    raise exc.OpenStackCloudException(
                        "Attempted to create FIP on port {port} for server"
                        " {server} but FIP has port {port_id}".format(
                            port=port, port_id=fip['port_id'],
                            server=server['id']))
                else:
                    raise exc.OpenStackCloudException(
                        "Attempted to create FIP on port {port}"
                        " but something went wrong".format(port=port))
        return fip

    def _nova_create_floating_ip(self, pool=None):
        with _utils.shade_exceptions(
                "Unable to create floating IP in pool {pool}".format(
                    pool=pool)):
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise exc.OpenStackCloudResourceNotFound(
                        "unable to find a floating ip pool")
                pool = pools[0]['name']

            data = proxy._json_response(self.compute.post(
                '/os-floating-ips', json=dict(pool=pool)))
            pool_ip = self._get_and_munchify('floating_ip', data)
            # TODO(mordred) Remove this - it's just for compat
            data = proxy._json_response(
                self.compute.get('/os-floating-ips/{id}'.format(
                    id=pool_ip['id'])))
            return self._get_and_munchify('floating_ip', data)

    def delete_floating_ip(self, floating_ip_id, retry=1):
        """Deallocate a floating IP from a project.

        :param floating_ip_id: a floating IP address ID.
        :param retry: number of times to retry. Optional, defaults to 1,
                      which is in addition to the initial delete call.
                      A value of 0 will also cause no checking of results to
                      occur.

        :returns: True if the IP address has been deleted, False if the IP
                  address was not found.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        for count in range(0, max(0, retry) + 1):
            result = self._delete_floating_ip(floating_ip_id)

            if (retry == 0) or not result:
                return result

            # Wait for the cached floating ip list to be regenerated
            if self._FLOAT_AGE:
                time.sleep(self._FLOAT_AGE)

            # neutron sometimes returns success when deleting a floating
            # ip. That's awesome. SO - verify that the delete actually
            # worked. Some clouds will set the status to DOWN rather than
            # deleting the IP immediately. This is, of course, a bit absurd.
            f_ip = self.get_floating_ip(id=floating_ip_id)
            if not f_ip or f_ip['status'] == 'DOWN':
                return True

        raise exc.OpenStackCloudException(
            "Attempted to delete Floating IP {ip} with ID {id} a total of"
            " {retry} times. Although the cloud did not indicate any errors"
            " the floating ip is still in existence. Aborting further"
            " operations.".format(
                id=floating_ip_id, ip=f_ip['floating_ip_address'],
                retry=retry + 1))

    def _delete_floating_ip(self, floating_ip_id):
        if self._use_neutron_floating():
            try:
                return self._neutron_delete_floating_ip(floating_ip_id)
            except exc.OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
        return self._nova_delete_floating_ip(floating_ip_id)

    def _neutron_delete_floating_ip(self, floating_ip_id):
        try:
            proxy._json_response(self.network.delete(
                "/floatingips/{fip_id}.json".format(fip_id=floating_ip_id),
                error_message="unable to delete floating IP"))
        except exc.OpenStackCloudResourceNotFound:
            return False
        except Exception as e:
            raise exc.OpenStackCloudException(
                "Unable to delete floating IP ID {fip_id}: {msg}".format(
                    fip_id=floating_ip_id, msg=str(e)))
        return True

    def _nova_delete_floating_ip(self, floating_ip_id):
        try:
            proxy._json_response(
                self.compute.delete(
                    '/os-floating-ips/{id}'.format(id=floating_ip_id)),
                error_message='Unable to delete floating IP {fip_id}'.format(
                    fip_id=floating_ip_id))
        except exc.OpenStackCloudURINotFound:
            return False
        return True

    def delete_unattached_floating_ips(self, retry=1):
        """Safely delete unattached floating ips.

        If the cloud can safely purge any unattached floating ips without
        race conditions, do so.

        Safely here means a specific thing. It means that you are not running
        this while another process that might do a two step create/attach
        is running. You can safely run this  method while another process
        is creating servers and attaching floating IPs to them if either that
        process is using add_auto_ip from shade, or is creating the floating
        IPs by passing in a server to the create_floating_ip call.

        :param retry: number of times to retry. Optional, defaults to 1,
                      which is in addition to the initial delete call.
                      A value of 0 will also cause no checking of results to
                      occur.

        :returns: Number of Floating IPs deleted, False if none

        :raises: ``OpenStackCloudException``, on operation error.
        """
        processed = []
        if self._use_neutron_floating():
            for ip in self.list_floating_ips():
                if not ip['attached']:
                    processed.append(self.delete_floating_ip(
                        floating_ip_id=ip['id'], retry=retry))
        return len(processed) if all(processed) else False

    def _attach_ip_to_server(
            self, server, floating_ip,
            fixed_address=None, wait=False,
            timeout=60, skip_attach=False, nat_destination=None):
        """Attach a floating IP to a server.

        :param server: Server dict
        :param floating_ip: Floating IP dict to attach
        :param fixed_address: (optional) fixed address to which attach the
                              floating IP to.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param skip_attach: (optional) Skip the actual attach and just do
                            the wait. Defaults to False.
        :param nat_destination: The fixed network the server's port for the
                                FIP to attach to will come from.

        :returns: The server ``munch.Munch``

        :raises: OpenStackCloudException, on operation error.
        """
        # Short circuit if we're asking to attach an IP that's already
        # attached
        ext_ip = meta.get_server_ip(server, ext_tag='floating', public=True)
        if not ext_ip and floating_ip['port_id']:
            # When we came here from reuse_fip and created FIP it might be
            # already attached, but the server info might be also
            # old to check whether it belongs to us now, thus refresh
            # the server data and try again. There are some clouds, which
            # explicitely forbids FIP assign call if it is already assigned.
            server = self.get_server_by_id(server['id'])
            ext_ip = meta.get_server_ip(server, ext_tag='floating',
                                        public=True)
        if ext_ip == floating_ip['floating_ip_address']:
            return server

        if self._use_neutron_floating():
            if not skip_attach:
                try:
                    self._neutron_attach_ip_to_server(
                        server=server, floating_ip=floating_ip,
                        fixed_address=fixed_address,
                        nat_destination=nat_destination)
                except exc.OpenStackCloudURINotFound as e:
                    self.log.debug(
                        "Something went wrong talking to neutron API: "
                        "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                    # Fall-through, trying with Nova
        else:
            # Nova network
            self._nova_attach_ip_to_server(
                server_id=server['id'], floating_ip_id=floating_ip['id'],
                fixed_address=fixed_address)

        if wait:
            # Wait for the address to be assigned to the server
            server_id = server['id']
            for _ in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the floating IP to be attached.",
                    wait=self._SERVER_AGE):
                server = self.get_server_by_id(server_id)
                ext_ip = meta.get_server_ip(
                    server, ext_tag='floating', public=True)
                if ext_ip == floating_ip['floating_ip_address']:
                    return server
        return server

    def _neutron_attach_ip_to_server(
            self, server, floating_ip, fixed_address=None,
            nat_destination=None):

        # Find an available port
        (port, fixed_address) = self._nat_destination_port(
            server, fixed_address=fixed_address,
            nat_destination=nat_destination)
        if not port:
            raise exc.OpenStackCloudException(
                "unable to find a port for server {0}".format(
                    server['id']))

        floating_ip_args = {'port_id': port['id']}
        if fixed_address is not None:
            floating_ip_args['fixed_ip_address'] = fixed_address

        return proxy._json_response(
            self.network.put(
                "/floatingips/{fip_id}.json".format(fip_id=floating_ip['id']),
                json={'floatingip': floating_ip_args}),
            error_message=("Error attaching IP {ip} to "
                           "server {server_id}".format(
                               ip=floating_ip['id'],
                               server_id=server['id'])))

    def _nova_attach_ip_to_server(self, server_id, floating_ip_id,
                                  fixed_address=None):
        f_ip = self.get_floating_ip(
            id=floating_ip_id)
        if f_ip is None:
            raise exc.OpenStackCloudException(
                "unable to find floating IP {0}".format(floating_ip_id))
        error_message = "Error attaching IP {ip} to instance {id}".format(
            ip=floating_ip_id, id=server_id)
        body = {
            'address': f_ip['floating_ip_address']
        }
        if fixed_address:
            body['fixed_address'] = fixed_address
        return proxy._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json=dict(addFloatingIp=body)),
            error_message=error_message)

    def detach_ip_from_server(self, server_id, floating_ip_id):
        """Detach a floating IP from a server.

        :param server_id: ID of a server.
        :param floating_ip_id: Id of the floating IP to detach.

        :returns: True if the IP has been detached, or False if the IP wasn't
                  attached to any server.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self._use_neutron_floating():
            try:
                return self._neutron_detach_ip_from_server(
                    server_id=server_id, floating_ip_id=floating_ip_id)
            except exc.OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova

        # Nova network
        self._nova_detach_ip_from_server(
            server_id=server_id, floating_ip_id=floating_ip_id)

    def _neutron_detach_ip_from_server(self, server_id, floating_ip_id):
        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None or not f_ip['attached']:
            return False
        exceptions.raise_from_response(
            self.network.put(
                "/floatingips/{fip_id}.json".format(fip_id=floating_ip_id),
                json={"floatingip": {"port_id": None}}),
            error_message=("Error detaching IP {ip} from "
                           "server {server_id}".format(
                               ip=floating_ip_id, server_id=server_id)))

        return True

    def _nova_detach_ip_from_server(self, server_id, floating_ip_id):

        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None:
            raise exc.OpenStackCloudException(
                "unable to find floating IP {0}".format(floating_ip_id))
        error_message = "Error detaching IP {ip} from instance {id}".format(
            ip=floating_ip_id, id=server_id)
        return proxy._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json=dict(removeFloatingIp=dict(
                    address=f_ip['floating_ip_address']))),
            error_message=error_message)

        return True

    def _add_ip_from_pool(
            self, server, network, fixed_address=None, reuse=True,
            wait=False, timeout=60, nat_destination=None):
        """Add a floating IP to a server from a given pool

        This method reuses available IPs, when possible, or allocate new IPs
        to the current tenant.
        The floating IP is attached to the given fixed address or to the
        first server port/fixed address

        :param server: Server dict
        :param network: Name or ID of the network.
        :param fixed_address: a fixed address
        :param reuse: Try to reuse existing ips. Defaults to True.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param nat_destination: (optional) the name of the network of the
                                port to associate with the floating ip.

        :returns: the updated server ``munch.Munch``
        """
        if reuse:
            f_ip = self.available_floating_ip(network=network)
        else:
            start_time = time.time()
            f_ip = self.create_floating_ip(
                server=server,
                network=network, nat_destination=nat_destination,
                wait=wait, timeout=timeout)
            timeout = timeout - (time.time() - start_time)
            # Wait for cache invalidation time so that we don't try
            # to attach the FIP a second time below
            time.sleep(self._SERVER_AGE)
            server = self.get_server(server.id)

        # We run attach as a second call rather than in the create call
        # because there are code flows where we will not have an attached
        # FIP yet. However, even if it was attached in the create, we run
        # the attach function below to get back the server dict refreshed
        # with the FIP information.
        return self._attach_ip_to_server(
            server=server, floating_ip=f_ip, fixed_address=fixed_address,
            wait=wait, timeout=timeout, nat_destination=nat_destination)

    def add_ip_list(
            self, server, ips, wait=False, timeout=60,
            fixed_address=None):
        """Attach a list of IPs to a server.

        :param server: a server object
        :param ips: list of floating IP addresses or a single address
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param fixed_address: (optional) Fixed address of the server to
                                         attach the IP to

        :returns: The updated server ``munch.Munch``

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if type(ips) == list:
            ip = ips[0]
        else:
            ip = ips
        f_ip = self.get_floating_ip(
            id=None, filters={'floating_ip_address': ip})
        return self._attach_ip_to_server(
            server=server, floating_ip=f_ip, wait=wait, timeout=timeout,
            fixed_address=fixed_address)

    def add_auto_ip(self, server, wait=False, timeout=60, reuse=True):
        """Add a floating IP to a server.

        This method is intended for basic usage. For advanced network
        architecture (e.g. multiple external networks or servers with multiple
        interfaces), use other floating IP methods.

        This method can reuse available IPs, or allocate new IPs to the current
        project.

        :param server: a server dictionary.
        :param reuse: Whether or not to attempt to reuse IPs, defaults
                      to True.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param reuse: Try to reuse existing ips. Defaults to True.

        :returns: Floating IP address attached to server.

        """
        server = self._add_auto_ip(
            server, wait=wait, timeout=timeout, reuse=reuse)
        return server['interface_ip'] or None

    def _add_auto_ip(self, server, wait=False, timeout=60, reuse=True):
        skip_attach = False
        created = False
        if reuse:
            f_ip = self.available_floating_ip(server=server)
        else:
            start_time = time.time()
            f_ip = self.create_floating_ip(
                server=server, wait=wait, timeout=timeout)
            timeout = timeout - (time.time() - start_time)
            if server:
                # This gets passed in for both nova and neutron
                # but is only meaningful for the neutron logic branch
                skip_attach = True
            created = True

        try:
            # We run attach as a second call rather than in the create call
            # because there are code flows where we will not have an attached
            # FIP yet. However, even if it was attached in the create, we run
            # the attach function below to get back the server dict refreshed
            # with the FIP information.
            return self._attach_ip_to_server(
                server=server, floating_ip=f_ip, wait=wait, timeout=timeout,
                skip_attach=skip_attach)
        except exc.OpenStackCloudTimeout:
            if self._use_neutron_floating() and created:
                # We are here because we created an IP on the port
                # It failed. Delete so as not to leak an unmanaged
                # resource
                self.log.error(
                    "Timeout waiting for floating IP to become"
                    " active. Floating IP %(ip)s:%(id)s was created for"
                    " server %(server)s but is being deleted due to"
                    " activation failure.", {
                        'ip': f_ip['floating_ip_address'],
                        'id': f_ip['id'],
                        'server': server['id']})
                try:
                    self.delete_floating_ip(f_ip['id'])
                except Exception as e:
                    self.log.error(
                        "FIP LEAK: Attempted to delete floating ip "
                        "%(fip)s but received %(exc)s exception: %(err)s",
                        {'fip': f_ip['id'], 'exc': e.__class__, 'err': str(e)})
                    raise e
            raise

    def add_ips_to_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            wait=False, timeout=60, reuse=True, fixed_address=None,
            nat_destination=None):
        if ip_pool:
            server = self._add_ip_from_pool(
                server, ip_pool, reuse=reuse, wait=wait, timeout=timeout,
                fixed_address=fixed_address, nat_destination=nat_destination)
        elif ips:
            server = self.add_ip_list(
                server, ips, wait=wait, timeout=timeout,
                fixed_address=fixed_address)
        elif auto_ip:
            if self._needs_floating_ip(server, nat_destination):
                server = self._add_auto_ip(
                    server, wait=wait, timeout=timeout, reuse=reuse)
        return server

    def _needs_floating_ip(self, server, nat_destination):
        """Figure out if auto_ip should add a floating ip to this server.

        If the server has a public_v4 it does not need a floating ip.

        If the server does not have a private_v4 it does not need a
        floating ip.

        If self.private then the server does not need a floating ip.

        If the cloud runs nova, and the server has a private_v4 and not
        a public_v4, then the server needs a floating ip.

        If the server has a private_v4 and no public_v4 and the cloud has
        a network from which floating IPs come that is connected via a
        router to the network from which the private_v4 address came,
        then the server needs a floating ip.

        If the server has a private_v4 and no public_v4 and the cloud
        does not have a network from which floating ips come, or it has
        one but that network is not connected to the network from which
        the server's private_v4 address came via a router, then the
        server does not need a floating ip.
        """
        if not self._has_floating_ips():
            return False

        if server['public_v4']:
            return False

        if not server['private_v4']:
            return False

        if self.private:
            return False

        if not self.has_service('network'):
            return True

        # No floating ip network - no FIPs
        try:
            self._get_floating_network_id()
        except exc.OpenStackCloudException:
            return False

        (port_obj, fixed_ip_address) = self._nat_destination_port(
            server, nat_destination=nat_destination)

        if not port_obj or not fixed_ip_address:
            return False

        return True

    def _nat_destination_port(
            self, server, fixed_address=None, nat_destination=None):
        """Returns server port that is on a nat_destination network

        Find a port attached to the server which is on a network which
        has a subnet which can be the destination of NAT. Such a network
        is referred to in shade as a "nat_destination" network. So this
        then is a function which returns a port on such a network that is
        associated with the given server.

        :param server: Server dict.
        :param fixed_address: Fixed ip address of the port
        :param nat_destination: Name or ID of the network of the port.
        """
        # If we are caching port lists, we may not find the port for
        # our server if the list is old.  Try for at least 2 cache
        # periods if that is the case.
        if self._PORT_AGE:
            timeout = self._PORT_AGE * 2
        else:
            timeout = None
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for port to show up in list",
                wait=self._PORT_AGE):
            try:
                port_filter = {'device_id': server['id']}
                ports = self.search_ports(filters=port_filter)
                break
            except exc.OpenStackCloudTimeout:
                ports = None
        if not ports:
            return (None, None)
        port = None
        if not fixed_address:
            if len(ports) > 1:
                if nat_destination:
                    nat_network = self.get_network(nat_destination)
                    if not nat_network:
                        raise exc.OpenStackCloudException(
                            'NAT Destination {nat_destination} was configured'
                            ' but not found on the cloud. Please check your'
                            ' config and your cloud and try again.'.format(
                                nat_destination=nat_destination))
                else:
                    nat_network = self.get_nat_destination()

                if not nat_network:
                    raise exc.OpenStackCloudException(
                        'Multiple ports were found for server {server}'
                        ' but none of the networks are a valid NAT'
                        ' destination, so it is impossible to add a'
                        ' floating IP. If you have a network that is a valid'
                        ' destination for NAT and we could not find it,'
                        ' please file a bug. But also configure the'
                        ' nat_destination property of the networks list in'
                        ' your clouds.yaml file. If you do not have a'
                        ' clouds.yaml file, please make one - your setup'
                        ' is complicated.'.format(server=server['id']))

                maybe_ports = []
                for maybe_port in ports:
                    if maybe_port['network_id'] == nat_network['id']:
                        maybe_ports.append(maybe_port)
                if not maybe_ports:
                    raise exc.OpenStackCloudException(
                        'No port on server {server} was found matching'
                        ' your NAT destination network {dest}. Please '
                        ' check your config'.format(
                            server=server['id'], dest=nat_network['name']))
                ports = maybe_ports

            # Select the most recent available IPv4 address
            # To do this, sort the ports in reverse order by the created_at
            # field which is a string containing an ISO DateTime (which
            # thankfully sort properly) This way the most recent port created,
            # if there are more than one, will be the arbitrary port we
            # select.
            for port in sorted(
                    ports,
                    key=lambda p: p.get('created_at', 0),
                    reverse=True):
                for address in port.get('fixed_ips', list()):
                    try:
                        ip = ipaddress.ip_address(address['ip_address'])
                    except Exception:
                        continue
                    if ip.version == 4:
                        fixed_address = address['ip_address']
                        return port, fixed_address
            raise exc.OpenStackCloudException(
                "unable to find a free fixed IPv4 address for server "
                "{0}".format(server['id']))
        # unfortunately a port can have more than one fixed IP:
        # we can't use the search_ports filtering for fixed_address as
        # they are contained in a list. e.g.
        #
        #   "fixed_ips": [
        #     {
        #       "subnet_id": "008ba151-0b8c-4a67-98b5-0d2b87666062",
        #       "ip_address": "172.24.4.2"
        #     }
        #   ]
        #
        # Search fixed_address
        for p in ports:
            for fixed_ip in p['fixed_ips']:
                if fixed_address == fixed_ip['ip_address']:
                    return (p, fixed_address)
        return (None, None)

    def _has_floating_ips(self):
        if not self._floating_ip_source:
            return False
        else:
            return self._floating_ip_source in ('nova', 'neutron')

    def _use_neutron_floating(self):
        return (self.has_service('network')
                and self._floating_ip_source == 'neutron')
