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
import jsonpatch
import types  # noqa
import warnings

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import utils


class BaremetalCloudMixin(_normalize.Normalizer):

    @property
    def _baremetal_client(self):
        if 'baremetal' not in self._raw_clients:
            client = self._get_raw_client('baremetal')
            # Do this to force version discovery. We need to do that, because
            # the endpoint-override trick we do for neutron because
            # ironicclient just appends a /v1 won't work and will break
            # keystoneauth - because ironic's versioned discovery endpoint
            # is non-compliant and doesn't return an actual version dict.
            client = self._get_versioned_client(
                'baremetal', min_version=1, max_version='1.latest')
            self._raw_clients['baremetal'] = client
        return self._raw_clients['baremetal']

    def list_nics(self):
        """Return a list of all bare metal ports."""
        return [nic._to_munch() for nic in self.baremetal.ports(details=True)]

    def list_nics_for_machine(self, uuid):
        """Returns a list of ports present on the machine node.

        :param uuid: String representing machine UUID value in
                     order to identify the machine.
        :returns: A list of ports.
        """
        # TODO(dtantsur): support node names here.
        return [nic._to_munch()
                for nic in self.baremetal.ports(details=True, node_id=uuid)]

    def get_nic_by_mac(self, mac):
        """Get bare metal NIC by its hardware address (usually MAC)."""
        results = [nic._to_munch()
                   for nic in self.baremetal.ports(address=mac, details=True)]
        try:
            return results[0]
        except IndexError:
            return None

    def list_machines(self):
        """List Machines.

        :returns: list of ``munch.Munch`` representing machines.
        """
        return [self._normalize_machine(node._to_munch())
                for node in self.baremetal.nodes()]

    def get_machine(self, name_or_id):
        """Get Machine by name or uuid

        Search the baremetal host out by utilizing the supplied id value
        which can consist of a name or UUID.

        :param name_or_id: A node name or UUID that will be looked up.

        :returns: ``munch.Munch`` representing the node found or None if no
                  nodes are found.
        """
        try:
            return self._normalize_machine(
                self.baremetal.get_node(name_or_id)._to_munch())
        except exc.OpenStackCloudResourceNotFound:
            return None

    def get_machine_by_mac(self, mac):
        """Get machine by port MAC address

        :param mac: Port MAC address to query in order to return a node.

        :returns: ``munch.Munch`` representing the node found or None
                  if the node is not found.
        """
        nic = self.get_nic_by_mac(mac)
        if nic is None:
            return None
        else:
            return self.get_machine(nic['node_uuid'])

    def inspect_machine(self, name_or_id, wait=False, timeout=3600):
        """Inspect a Barmetal machine

        Engages the Ironic node inspection behavior in order to collect
        metadata about the baremetal machine.

        :param name_or_id: String representing machine name or UUID value in
                           order to identify the machine.

        :param wait: Boolean value controlling if the method is to wait for
                     the desired state to be reached or a failure to occur.

        :param timeout: Integer value, defautling to 3600 seconds, for the$
                        wait state to reach completion.

        :returns: ``munch.Munch`` representing the current state of the machine
                  upon exit of the method.
        """

        return_to_available = False

        node = self.baremetal.get_node(name_or_id)

        # NOTE(TheJulia): If in available state, we can do this. However,
        # we need to to move the machine back to manageable first.
        if node.provision_state == 'available':
            if node.instance_id:
                raise exc.OpenStackCloudException(
                    "Refusing to inspect available machine %(node)s "
                    "which is associated with an instance "
                    "(instance_uuid %(inst)s)" %
                    {'node': node.id, 'inst': node.instance_id})

            return_to_available = True
            # NOTE(TheJulia): Changing available machine to managedable state
            # and due to state transitions we need to until that transition has
            # completed.
            node = self.baremetal.set_node_provision_state(node, 'manage',
                                                           wait=True,
                                                           timeout=timeout)

        if node.provision_state not in ('manageable', 'inspect failed'):
            raise exc.OpenStackCloudException(
                "Machine %(node)s must be in 'manageable', 'inspect failed' "
                "or 'available' provision state to start inspection, the "
                "current state is %(state)s" %
                {'node': node.id, 'state': node.provision_state})

        node = self.baremetal.set_node_provision_state(node, 'inspect',
                                                       wait=True,
                                                       timeout=timeout)

        if return_to_available:
            node = self.baremetal.set_node_provision_state(node, 'provide',
                                                           wait=True,
                                                           timeout=timeout)

        return node._to_munch()

    def register_machine(self, nics, wait=False, timeout=3600,
                         lock_timeout=600, **kwargs):
        """Register Baremetal with Ironic

        Allows for the registration of Baremetal nodes with Ironic
        and population of pertinant node information or configuration
        to be passed to the Ironic API for the node.

        This method also creates ports for a list of MAC addresses passed
        in to be utilized for boot and potentially network configuration.

        If a failure is detected creating the network ports, any ports
        created are deleted, and the node is removed from Ironic.

        :param nics:
           An array of MAC addresses that represent the
           network interfaces for the node to be created.

           Example::

              [
                  {'mac': 'aa:bb:cc:dd:ee:01'},
                  {'mac': 'aa:bb:cc:dd:ee:02'}
              ]

        :param wait: Boolean value, defaulting to false, to wait for the
                     node to reach the available state where the node can be
                     provisioned. It must be noted, when set to false, the
                     method will still wait for locks to clear before sending
                     the next required command.

        :param timeout: Integer value, defautling to 3600 seconds, for the
                        wait state to reach completion.

        :param lock_timeout: Integer value, defaulting to 600 seconds, for
                             locks to clear.

        :param kwargs: Key value pairs to be passed to the Ironic API,
                       including uuid, name, chassis_uuid, driver_info,
                       parameters.

        :raises: OpenStackCloudException on operation error.

        :returns: Returns a ``munch.Munch`` representing the new
                  baremetal node.
        """

        msg = ("Baremetal machine node failed to be created.")
        port_msg = ("Baremetal machine port failed to be created.")

        url = '/nodes'
        # TODO(TheJulia): At some point we need to figure out how to
        # handle data across when the requestor is defining newer items
        # with the older api.
        machine = self._baremetal_client.post(url,
                                              json=kwargs,
                                              error_message=msg,
                                              microversion="1.6")

        created_nics = []
        try:
            for row in nics:
                payload = {'address': row['mac'],
                           'node_uuid': machine['uuid']}
                nic = self._baremetal_client.post('/ports',
                                                  json=payload,
                                                  error_message=port_msg)
                created_nics.append(nic['uuid'])

        except Exception as e:
            self.log.debug("ironic NIC registration failed", exc_info=True)
            # TODO(mordred) Handle failures here
            try:
                for uuid in created_nics:
                    try:
                        port_url = '/ports/{uuid}'.format(uuid=uuid)
                        # NOTE(TheJulia): Added in hope that it is logged.
                        port_msg = ('Failed to delete port {port} for node '
                                    '{node}').format(port=uuid,
                                                     node=machine['uuid'])
                        self._baremetal_client.delete(port_url,
                                                      error_message=port_msg)
                    except Exception:
                        pass
            finally:
                version = "1.6"
                msg = "Baremetal machine failed to be deleted."
                url = '/nodes/{node_id}'.format(
                    node_id=machine['uuid'])
                self._baremetal_client.delete(url,
                                              error_message=msg,
                                              microversion=version)
            raise exc.OpenStackCloudException(
                "Error registering NICs with the baremetal service: %s"
                % str(e))

        with _utils.shade_exceptions(
                "Error transitioning node to available state"):
            if wait:
                for count in utils.iterate_timeout(
                        timeout,
                        "Timeout waiting for node transition to "
                        "available state"):

                    machine = self.get_machine(machine['uuid'])

                    # Note(TheJulia): Per the Ironic state code, a node
                    # that fails returns to enroll state, which means a failed
                    # node cannot be determined at this point in time.
                    if machine['provision_state'] in ['enroll']:
                        self.node_set_provision_state(
                            machine['uuid'], 'manage')
                    elif machine['provision_state'] in ['manageable']:
                        self.node_set_provision_state(
                            machine['uuid'], 'provide')
                    elif machine['last_error'] is not None:
                        raise exc.OpenStackCloudException(
                            "Machine encountered a failure: %s"
                            % machine['last_error'])

                    # Note(TheJulia): Earlier versions of Ironic default to
                    # None and later versions default to available up until
                    # the introduction of enroll state.
                    # Note(TheJulia): The node will transition through
                    # cleaning if it is enabled, and we will wait for
                    # completion.
                    elif machine['provision_state'] in ['available', None]:
                        break

            else:
                if machine['provision_state'] in ['enroll']:
                    self.node_set_provision_state(machine['uuid'], 'manage')
                    # Note(TheJulia): We need to wait for the lock to clear
                    # before we attempt to set the machine into provide state
                    # which allows for the transition to available.
                    for count in utils.iterate_timeout(
                            lock_timeout,
                            "Timeout waiting for reservation to clear "
                            "before setting provide state"):
                        machine = self.get_machine(machine['uuid'])
                        if (machine['reservation'] is None
                                and machine['provision_state'] != 'enroll'):
                            # NOTE(TheJulia): In this case, the node has
                            # has moved on from the previous state and is
                            # likely not being verified, as no lock is
                            # present on the node.
                            self.node_set_provision_state(
                                machine['uuid'], 'provide')
                            machine = self.get_machine(machine['uuid'])
                            break

                        elif machine['provision_state'] in [
                                'cleaning',
                                'available']:
                            break

                        elif machine['last_error'] is not None:
                            raise exc.OpenStackCloudException(
                                "Machine encountered a failure: %s"
                                % machine['last_error'])
        if not isinstance(machine, str):
            return self._normalize_machine(machine)
        else:
            return machine

    def unregister_machine(self, nics, uuid, wait=False, timeout=600):
        """Unregister Baremetal from Ironic

        Removes entries for Network Interfaces and baremetal nodes
        from an Ironic API

        :param nics: An array of strings that consist of MAC addresses
                          to be removed.
        :param string uuid: The UUID of the node to be deleted.

        :param wait: Boolean value, defaults to false, if to block the method
                     upon the final step of unregistering the machine.

        :param timeout: Integer value, representing seconds with a default
                        value of 600, which controls the maximum amount of
                        time to block the method's completion on.

        :raises: OpenStackCloudException on operation failure.
        """

        machine = self.get_machine(uuid)
        invalid_states = ['active', 'cleaning', 'clean wait', 'clean failed']
        if machine['provision_state'] in invalid_states:
            raise exc.OpenStackCloudException(
                "Error unregistering node '%s' due to current provision "
                "state '%s'" % (uuid, machine['provision_state']))

        # NOTE(TheJulia) There is a high possibility of a lock being present
        # if the machine was just moved through the state machine. This was
        # previously concealed by exception retry logic that detected the
        # failure, and resubitted the request in python-ironicclient.
        try:
            self.wait_for_baremetal_node_lock(machine, timeout=timeout)
        except exc.OpenStackCloudException as e:
            raise exc.OpenStackCloudException(
                "Error unregistering node '%s': Exception occured while"
                " waiting to be able to proceed: %s" % (machine['uuid'], e))

        for nic in nics:
            port_msg = ("Error removing NIC {nic} from baremetal API for "
                        "node {uuid}").format(nic=nic, uuid=uuid)
            port_url = '/ports/detail?address={mac}'.format(mac=nic['mac'])
            port = self._baremetal_client.get(port_url, microversion=1.6,
                                              error_message=port_msg)
            port_url = '/ports/{uuid}'.format(uuid=port['ports'][0]['uuid'])
            _utils._call_client_and_retry(self._baremetal_client.delete,
                                          port_url, retry_on=[409, 503],
                                          error_message=port_msg)

        with _utils.shade_exceptions(
                "Error unregistering machine {node_id} from the baremetal "
                "API".format(node_id=uuid)):

            # NOTE(TheJulia): While this should not matter microversion wise,
            # ironic assumes all calls without an explicit microversion to be
            # version 1.0. Ironic expects to deprecate support for older
            # microversions in future releases, as such, we explicitly set
            # the version to what we have been using with the client library..
            version = "1.6"
            msg = "Baremetal machine failed to be deleted"
            url = '/nodes/{node_id}'.format(
                node_id=uuid)
            _utils._call_client_and_retry(self._baremetal_client.delete,
                                          url, retry_on=[409, 503],
                                          error_message=msg,
                                          microversion=version)

            if wait:
                for count in utils.iterate_timeout(
                        timeout,
                        "Timeout waiting for machine to be deleted"):
                    if not self.get_machine(uuid):
                        break

    def patch_machine(self, name_or_id, patch):
        """Patch Machine Information

        This method allows for an interface to manipulate node entries
        within Ironic.

        :param string name_or_id: A machine name or UUID to be updated.
        :param patch:
           The JSON Patch document is a list of dictonary objects
           that comply with RFC 6902 which can be found at
           https://tools.ietf.org/html/rfc6902.

           Example patch construction::

               patch=[]
               patch.append({
                   'op': 'remove',
                   'path': '/instance_info'
               })
               patch.append({
                   'op': 'replace',
                   'path': '/name',
                   'value': 'newname'
               })
               patch.append({
                   'op': 'add',
                   'path': '/driver_info/username',
                   'value': 'administrator'
               })

        :raises: OpenStackCloudException on operation error.

        :returns: ``munch.Munch`` representing the newly updated node.
        """
        return self._normalize_machine(
            self.baremetal.patch_node(name_or_id, patch))

    def update_machine(self, name_or_id, **attrs):
        """Update a machine with new configuration information

        A user-friendly method to perform updates of a machine, in whole or
        part.

        :param string name_or_id: A machine name or UUID to be updated.
        :param attrs: Attributes to updated on the machine.

        :raises: OpenStackCloudException on operation error.

        :returns: ``munch.Munch`` containing a machine sub-dictonary consisting
                  of the updated data returned from the API update operation,
                  and a list named changes which contains all of the API paths
                  that received updates.
        """
        machine = self.get_machine(name_or_id)
        if not machine:
            raise exc.OpenStackCloudException(
                "Machine update failed to find Machine: %s. " % name_or_id)

        new_config = dict(machine, **attrs)

        try:
            patch = jsonpatch.JsonPatch.from_diff(machine, new_config)
        except Exception as e:
            raise exc.OpenStackCloudException(
                "Machine update failed - Error generating JSON patch object "
                "for submission to the API. Machine: %s Error: %s"
                % (name_or_id, e))

        if not patch:
            return dict(
                node=machine,
                changes=None
            )

        change_list = [change['path'] for change in patch]
        node = self.baremetal.update_node(machine, **attrs)
        return dict(
            node=self._normalize_machine(node._to_munch()),
            changes=change_list
        )

    def attach_port_to_machine(self, name_or_id, port_name_or_id):
        """Attach a virtual port to the bare metal machine.

        :param string name_or_id: A machine name or UUID.
        :param string port_name_or_id: A port name or UUID.
            Note that this is a Network service port, not a bare metal NIC.
        :return: Nothing.
        """
        machine = self.get_machine(name_or_id)
        port = self.get_port(port_name_or_id)
        self.baremetal.attach_vif_to_node(machine, port['id'])

    def detach_port_from_machine(self, name_or_id, port_name_or_id):
        """Detach a virtual port from the bare metal machine.

        :param string name_or_id: A machine name or UUID.
        :param string port_name_or_id: A port name or UUID.
            Note that this is a Network service port, not a bare metal NIC.
        :return: Nothing.
        """
        machine = self.get_machine(name_or_id)
        port = self.get_port(port_name_or_id)
        self.baremetal.detach_vif_from_node(machine, port['id'])

    def list_ports_attached_to_machine(self, name_or_id):
        """List virtual ports attached to the bare metal machine.

        :param string name_or_id: A machine name or UUID.
        :returns: List of ``munch.Munch`` representing the ports.
        """
        machine = self.get_machine(name_or_id)
        vif_ids = self.baremetal.list_node_vifs(machine)
        return [self.get_port(vif) for vif in vif_ids]

    def validate_machine(self, name_or_id, for_deploy=True):
        """Validate parameters of the machine.

        :param string name_or_id: The Name or UUID value representing the
                                  baremetal node.
        :param bool for_deploy: If ``True``, validate readiness for deployment,
                                otherwise validate only the power management
                                properties.
        :raises: :exc:`~openstack.exceptions.ValidationException`
        """
        if for_deploy:
            ifaces = ('boot', 'deploy', 'management', 'power')
        else:
            ifaces = ('power',)
        self.baremetal.validate_node(name_or_id, required=ifaces)

    def validate_node(self, uuid):
        warnings.warn('validate_node is deprecated, please use '
                      'validate_machine instead', DeprecationWarning)
        self.baremetal.validate_node(uuid)

    def node_set_provision_state(self,
                                 name_or_id,
                                 state,
                                 configdrive=None,
                                 wait=False,
                                 timeout=3600):
        """Set Node Provision State

        Enables a user to provision a Machine and optionally define a
        config drive to be utilized.

        :param string name_or_id: The Name or UUID value representing the
                                  baremetal node.
        :param string state: The desired provision state for the
                             baremetal node.
        :param string configdrive: An optional URL or file or path
                                   representing the configdrive. In the
                                   case of a directory, the client API
                                   will create a properly formatted
                                   configuration drive file and post the
                                   file contents to the API for
                                   deployment.
        :param boolean wait: A boolean value, defaulted to false, to control
                             if the method will wait for the desire end state
                             to be reached before returning.
        :param integer timeout: Integer value, defaulting to 3600 seconds,
                                representing the amount of time to wait for
                                the desire end state to be reached.

        :raises: OpenStackCloudException on operation error.

        :returns: ``munch.Munch`` representing the current state of the machine
                  upon exit of the method.
        """
        node = self.baremetal.set_node_provision_state(
            name_or_id, target=state, config_drive=configdrive,
            wait=wait, timeout=timeout)
        return node._to_munch()

    def set_machine_maintenance_state(
            self,
            name_or_id,
            state=True,
            reason=None):
        """Set Baremetal Machine Maintenance State

        Sets Baremetal maintenance state and maintenance reason.

        :param string name_or_id: The Name or UUID value representing the
                                  baremetal node.
        :param boolean state: The desired state of the node.  True being in
                              maintenance where as False means the machine
                              is not in maintenance mode.  This value
                              defaults to True if not explicitly set.
        :param string reason: An optional freeform string that is supplied to
                              the baremetal API to allow for notation as to why
                              the node is in maintenance state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        if state:
            self.baremetal.set_node_maintenance(name_or_id, reason)
        else:
            self.baremetal.unset_node_maintenance(name_or_id)

    def remove_machine_from_maintenance(self, name_or_id):
        """Remove Baremetal Machine from Maintenance State

        Similarly to set_machine_maintenance_state, this method
        removes a machine from maintenance state.  It must be noted
        that this method simpily calls set_machine_maintenace_state
        for the name_or_id requested and sets the state to False.

        :param string name_or_id: The Name or UUID value representing the
                                  baremetal node.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self.baremetal.unset_node_maintenance(name_or_id)

    def set_machine_power_on(self, name_or_id):
        """Activate baremetal machine power

        This is a method that sets the node power state to "on".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "on"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self.baremetal.set_node_power_state(name_or_id, 'power on')

    def set_machine_power_off(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "off".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "off"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns:
        """
        self.baremetal.set_node_power_state(name_or_id, 'power off')

    def set_machine_power_reboot(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "reboot", which
        in essence changes the machine power state to "off", and that back
        to "on".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "off"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self.baremetal.set_node_power_state(name_or_id, 'rebooting')

    def activate_node(self, uuid, configdrive=None,
                      wait=False, timeout=1200):
        self.node_set_provision_state(
            uuid, 'active', configdrive, wait=wait, timeout=timeout)

    def deactivate_node(self, uuid, wait=False,
                        timeout=1200):
        self.node_set_provision_state(
            uuid, 'deleted', wait=wait, timeout=timeout)

    def set_node_instance_info(self, uuid, patch):
        warnings.warn("The set_node_instance_info call is deprecated, "
                      "use patch_machine or update_machine instead",
                      DeprecationWarning)
        return self.patch_machine(uuid, patch)

    def purge_node_instance_info(self, uuid):
        warnings.warn("The purge_node_instance_info call is deprecated, "
                      "use patch_machine or update_machine instead",
                      DeprecationWarning)
        return self.patch_machine(uuid,
                                  dict(path='/instance_info', op='remove'))

    def wait_for_baremetal_node_lock(self, node, timeout=30):
        """Wait for a baremetal node to have no lock.

        DEPRECATED, use ``wait_for_node_reservation`` on the `baremetal` proxy.

        :raises: OpenStackCloudException upon client failure.
        :returns: None
        """
        warnings.warn("The wait_for_baremetal_node_lock call is deprecated "
                      "in favor of wait_for_node_reservation on the baremetal "
                      "proxy", DeprecationWarning)
        self.baremetal.wait_for_node_reservation(node, timeout)
