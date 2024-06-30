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

import contextlib
import sys
import warnings

import jsonpatch

from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import warnings as os_warnings


def _normalize_port_list(nics):
    ports = []
    for row in nics:
        if isinstance(row, str):
            address = row
            row = {}
        elif 'mac' in row:
            address = row.pop('mac')
        else:
            try:
                address = row.pop('address')
            except KeyError:
                raise TypeError(
                    "Either 'address' or 'mac' must be provided "
                    f"for port {row}"
                )
        ports.append(dict(row, address=address))
    return ports


class BaremetalCloudMixin(openstackcloud._OpenStackCloudMixin):
    def list_nics(self):
        """Return a list of all bare metal ports."""
        return list(self.baremetal.ports(details=True))

    def list_nics_for_machine(self, uuid):
        """Returns a list of ports present on the machine node.

        :param uuid: String representing machine UUID value in order to
            identify the machine.
        :returns: A list of ports.
        """
        # TODO(dtantsur): support node names here.
        return list(self.baremetal.ports(details=True, node_id=uuid))

    def get_nic_by_mac(self, mac):
        """Get bare metal NIC by its hardware address (usually MAC)."""
        results = list(self.baremetal.ports(address=mac, details=True))
        try:
            return results[0]
        except IndexError:
            return None

    def list_machines(self):
        """List Machines.

        :returns: list of :class:`~openstack.baremetal.v1.node.Node`.
        """
        return list(self.baremetal.nodes())

    def get_machine(self, name_or_id):
        """Get Machine by name or uuid

        Search the baremetal host out by utilizing the supplied id value
        which can consist of a name or UUID.

        :param name_or_id: A node name or UUID that will be looked up.

        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        :returns: The node found or None if no nodes are found.
        """
        return self.baremetal.find_node(name_or_id, ignore_missing=True)

    def get_machine_by_mac(self, mac):
        """Get machine by port MAC address

        :param mac: Port MAC address to query in order to return a node.

        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        :returns: The node found or None if no nodes are found.
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

        :param timeout: Integer value, defautling to 3600 seconds, for the
            wait state to reach completion.

        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        :returns: Current state of the node.
        """

        return_to_available = False

        node = self.baremetal.get_node(name_or_id)

        # NOTE(TheJulia): If in available state, we can do this. However,
        # we need to move the machine back to manageable first.
        if node.provision_state == 'available':
            if node.instance_id:
                raise exceptions.SDKException(
                    f"Refusing to inspect available machine {node.id} "
                    "which is associated with an instance "
                    f"(instance_uuid {node.instance_id})"
                )

            return_to_available = True
            # NOTE(TheJulia): Changing available machine to managedable state
            # and due to state transitions we need to until that transition has
            # completed.
            node = self.baremetal.set_node_provision_state(
                node, 'manage', wait=True, timeout=timeout
            )

        if node.provision_state not in ('manageable', 'inspect failed'):
            raise exceptions.SDKException(
                f"Machine {node.id} must be in 'manageable', 'inspect failed' "
                "or 'available' provision state to start inspection, the "
                f"current state is {node.provision_state}"
            )

        node = self.baremetal.set_node_provision_state(
            node, 'inspect', wait=True, timeout=timeout
        )

        if return_to_available:
            node = self.baremetal.set_node_provision_state(
                node, 'provide', wait=True, timeout=timeout
            )

        return node

    @contextlib.contextmanager
    def _delete_node_on_error(self, node):
        try:
            yield
        except Exception as exc:
            self.log.debug(
                "cleaning up node %s because of an error: %s", node.id, exc
            )
            tb = sys.exc_info()[2]
            try:
                self.baremetal.delete_node(node)
            except Exception:
                self.log.debug(
                    "could not remove node %s", node.id, exc_info=True
                )
            raise exc.with_traceback(tb)

    def register_machine(
        self,
        nics,
        wait=False,
        timeout=3600,
        lock_timeout=600,
        provision_state='available',
        **kwargs,
    ):
        """Register Baremetal with Ironic

        Allows for the registration of Baremetal nodes with Ironic
        and population of pertinant node information or configuration
        to be passed to the Ironic API for the node.

        This method also creates ports for a list of MAC addresses passed
        in to be utilized for boot and potentially network configuration.

        If a failure is detected creating the network ports, any ports
        created are deleted, and the node is removed from Ironic.

        :param nics:
            An array of ports that represent the network interfaces for the
            node to be created. The ports are created after the node is
            enrolled but before it goes through cleaning.

            Example::

                [
                    {'address': 'aa:bb:cc:dd:ee:01'},
                    {'address': 'aa:bb:cc:dd:ee:02'},
                ]

            Alternatively, you can provide an array of MAC addresses.
        :param wait: Boolean value, defaulting to false, to wait for the node
            to reach the available state where the node can be provisioned. It
            must be noted, when set to false, the method will still wait for
            locks to clear before sending the next required command.
        :param timeout: Integer value, defautling to 3600 seconds, for the wait
            state to reach completion.
        :param lock_timeout: Integer value, defaulting to 600 seconds, for
            locks to clear.
        :param provision_state: The expected provision state, one of "enroll"
            "manageable" or "available". Using "available" results in automated
            cleaning.
        :param kwargs: Key value pairs to be passed to the Ironic API,
            including uuid, name, chassis_uuid, driver_info, properties.

        :returns: Current state of the node.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if provision_state not in ('enroll', 'manageable', 'available'):
            raise ValueError(
                'Initial provision state must be enroll, '
                f'manageable or available, got {provision_state}'
            )

        # Available is tricky: it cannot be directly requested on newer API
        # versions, we need to go through cleaning. But we cannot go through
        # cleaning until we create ports.
        if provision_state != 'available':
            kwargs['provision_state'] = 'enroll'
        machine = self.baremetal.create_node(**kwargs)

        with self._delete_node_on_error(machine):
            # Making a node at least manageable
            if (
                machine.provision_state == 'enroll'
                and provision_state != 'enroll'
            ):
                machine = self.baremetal.set_node_provision_state(
                    machine, 'manage', wait=True, timeout=timeout
                )
                machine = self.baremetal.wait_for_node_reservation(
                    machine, timeout=lock_timeout
                )

            # Create NICs before trying to run cleaning
            created_nics = []
            try:
                for port in _normalize_port_list(nics):
                    nic = self.baremetal.create_port(
                        node_id=machine.id, **port
                    )
                    created_nics.append(nic.id)

            except Exception:
                for uuid in created_nics:
                    try:
                        self.baremetal.delete_port(uuid)
                    except Exception:  # noqa: S110
                        # the port might not have been actually created, so a
                        # failure to delete isn't necessarily an issue
                        pass
                raise

            if (
                machine.provision_state != 'available'
                and provision_state == 'available'
            ):
                machine = self.baremetal.set_node_provision_state(
                    machine, 'provide', wait=wait, timeout=timeout
                )

            return machine

    def unregister_machine(self, nics, uuid, wait=None, timeout=600):
        """Unregister Baremetal from Ironic

        Removes entries for Network Interfaces and baremetal nodes
        from an Ironic API

        :param nics: An array of strings that consist of MAC addresses
            to be removed.
        :param string uuid: The UUID of the node to be deleted.
        :param wait: DEPRECATED, do not use.
        :param timeout: Integer value, representing seconds with a default
            value of 600, which controls the maximum amount of time to block
            until a lock is released on machine.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            failure.
        """
        if wait is not None:
            warnings.warn(
                "wait argument is deprecated and has no effect",
                os_warnings.RemovedInSDK50Warning,
            )

        machine = self.get_machine(uuid)
        invalid_states = ['active', 'cleaning', 'clean wait', 'clean failed']
        if machine['provision_state'] in invalid_states:
            raise exceptions.SDKException(
                "Error unregistering node '{}' due to current provision "
                "state '{}'".format(uuid, machine['provision_state'])
            )

        # NOTE(TheJulia) There is a high possibility of a lock being present
        # if the machine was just moved through the state machine. This was
        # previously concealed by exception retry logic that detected the
        # failure, and resubitted the request in python-ironicclient.
        try:
            self.baremetal.wait_for_node_reservation(machine, timeout)
        except exceptions.SDKException as e:
            raise exceptions.SDKException(
                "Error unregistering node '{}': Exception occured while "
                "waiting to be able to proceed: {}".format(machine['uuid'], e)
            )

        for nic in _normalize_port_list(nics):
            try:
                port = next(self.baremetal.ports(address=nic['address']))
            except StopIteration:
                continue
            self.baremetal.delete_port(port.id)

        self.baremetal.delete_node(uuid)

    def patch_machine(self, name_or_id, patch):
        """Patch Machine Information

        This method allows for an interface to manipulate node entries
        within Ironic.

        :param string name_or_id: A machine name or UUID to be updated.
        :param patch:
            The JSON Patch document is a list of dictonary objects that comply
            with RFC 6902 which can be found at
            https://tools.ietf.org/html/rfc6902.

            Example patch construction::

                patch = []
                patch.append({'op': 'remove', 'path': '/instance_info'})
                patch.append(
                    {'op': 'replace', 'path': '/name', 'value': 'newname'}
                )
                patch.append(
                    {
                        'op': 'add',
                        'path': '/driver_info/username',
                        'value': 'administrator',
                    }
                )

        :returns: Current state of the node.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        return self.baremetal.patch_node(name_or_id, patch)

    def update_machine(self, name_or_id, **attrs):
        """Update a machine with new configuration information

        A user-friendly method to perform updates of a machine, in whole or
        part.

        :param string name_or_id: A machine name or UUID to be updated.
        :param attrs: Attributes to updated on the machine.

        :returns: Dictionary containing a machine sub-dictonary consisting
            of the updated data returned from the API update operation, and a
            list named changes which contains all of the API paths that
            received updates.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        machine = self.get_machine(name_or_id)
        if not machine:
            raise exceptions.SDKException(
                f"Machine update failed to find Machine: {name_or_id}. "
            )

        new_config = dict(machine._to_munch(), **attrs)

        try:
            patch = jsonpatch.JsonPatch.from_diff(
                machine._to_munch(), new_config
            )
        except Exception as e:
            raise exceptions.SDKException(
                "Machine update failed - Error generating JSON patch object "
                f"for submission to the API. Machine: {name_or_id} Error: {e}"
            )

        if not patch:
            return dict(node=machine, changes=None)

        change_list = [change['path'] for change in patch]
        node = self.baremetal.update_node(machine, **attrs)
        return dict(node=node, changes=change_list)

    def attach_port_to_machine(self, name_or_id, port_name_or_id):
        """Attach a virtual port to the bare metal machine.

        :param string name_or_id: A machine name or UUID.
        :param string port_name_or_id: A port name or UUID.
            Note that this is a Network service port, not a bare metal NIC.
        :return: Nothing.
        """
        machine = self.get_machine(name_or_id)
        port = self.network.find_port(port_name_or_id, ignore_missing=False)
        self.baremetal.attach_vif_to_node(machine, port['id'])

    def detach_port_from_machine(self, name_or_id, port_name_or_id):
        """Detach a virtual port from the bare metal machine.

        :param string name_or_id: A machine name or UUID.
        :param string port_name_or_id: A port name or UUID.
            Note that this is a Network service port, not a bare metal NIC.
        :return: Nothing.
        """
        machine = self.get_machine(name_or_id)
        port = self.network.find_port(port_name_or_id, ignore_missing=False)
        self.baremetal.detach_vif_from_node(machine, port['id'])

    def list_ports_attached_to_machine(self, name_or_id):
        """List virtual ports attached to the bare metal machine.

        :param string name_or_id: A machine name or UUID.
        :returns: List of ``openstack.Resource`` objects representing
            the ports.
        """
        machine = self.get_machine(name_or_id)
        vif_ids = self.baremetal.list_node_vifs(machine)
        return [
            self.network.find_port(vif, ignore_missing=False)
            for vif in vif_ids
        ]

    def validate_machine(self, name_or_id, for_deploy=True):
        """Validate parameters of the machine.

        :param string name_or_id: The Name or UUID value representing the
            baremetal node.
        :param bool for_deploy: If ``True``, validate readiness for deployment,
            otherwise validate only the power management properties.
        :raises: :exc:`~openstack.exceptions.ValidationException`
        """
        if for_deploy:
            ifaces = ['boot', 'deploy', 'management', 'power']
        else:
            ifaces = ['power']
        self.baremetal.validate_node(name_or_id, required=ifaces)

    def validate_node(self, uuid):
        warnings.warn(
            'validate_node is deprecated, please use validate_machine instead',
            os_warnings.RemovedInSDK50Warning,
        )
        self.baremetal.validate_node(uuid)

    def node_set_provision_state(
        self, name_or_id, state, configdrive=None, wait=False, timeout=3600
    ):
        """Set Node Provision State

        Enables a user to provision a Machine and optionally define a
        config drive to be utilized.

        :param string name_or_id: The Name or UUID value representing the
            baremetal node.
        :param string state: The desired provision state for the baremetal
            node.
        :param string configdrive: An optional URL or file or path
            representing the configdrive. In the case of a directory, the
            client API will create a properly formatted configuration drive
            file and post the file contents to the API for deployment.
        :param boolean wait: A boolean value, defaulted to false, to control
            if the method will wait for the desire end state to be reached
            before returning.
        :param integer timeout: Integer value, defaulting to 3600 seconds,
            representing the amount of time to wait for the desire end state to
            be reached.

        :returns: Current state of the machine upon exit of the method.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        node = self.baremetal.set_node_provision_state(
            name_or_id,
            target=state,
            config_drive=configdrive,
            wait=wait,
            timeout=timeout,
        )
        return node

    def set_machine_maintenance_state(
        self, name_or_id, state=True, reason=None
    ):
        """Set Baremetal Machine Maintenance State

        Sets Baremetal maintenance state and maintenance reason.

        :param string name_or_id: The Name or UUID value representing the
            baremetal node.
        :param boolean state: The desired state of the node. True being in
            maintenance where as False means the machine is not in maintenance
            mode.  This value defaults to True if not explicitly set.
        :param string reason: An optional freeform string that is supplied to
            the baremetal API to allow for notation as to why the node is in
            maintenance state.

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if state:
            self.baremetal.set_node_maintenance(name_or_id, reason)
        else:
            self.baremetal.unset_node_maintenance(name_or_id)

    def remove_machine_from_maintenance(self, name_or_id):
        """Remove Baremetal Machine from Maintenance State

        Similarly to set_machine_maintenance_state, this method removes a
        machine from maintenance state.  It must be noted that this method
        simpily calls set_machine_maintenace_state for the name_or_id requested
        and sets the state to False.

        :param string name_or_id: The Name or UUID value representing the
            baremetal node.

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        self.baremetal.unset_node_maintenance(name_or_id)

    def set_machine_power_on(self, name_or_id):
        """Activate baremetal machine power

        This is a method that sets the node power state to "on".

        :params string name_or_id: A string representing the baremetal
            node to have power turned to an "on" state.

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        self.baremetal.set_node_power_state(name_or_id, 'power on')

    def set_machine_power_off(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "off".

        :params string name_or_id: A string representing the baremetal
            node to have power turned to an "off" state.

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        self.baremetal.set_node_power_state(name_or_id, 'power off')

    def set_machine_power_reboot(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "reboot", which
        in essence changes the machine power state to "off", and that back
        to "on".

        :params string name_or_id: A string representing the baremetal
            node to have power turned to an "off" state.

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        self.baremetal.set_node_power_state(name_or_id, 'rebooting')

    def activate_node(self, uuid, configdrive=None, wait=False, timeout=1200):
        self.node_set_provision_state(
            uuid, 'active', configdrive, wait=wait, timeout=timeout
        )

    def deactivate_node(self, uuid, wait=False, timeout=1200):
        self.node_set_provision_state(
            uuid, 'deleted', wait=wait, timeout=timeout
        )

    def set_node_instance_info(self, uuid, patch):
        warnings.warn(
            "The set_node_instance_info call is deprecated, "
            "use patch_machine or update_machine instead",
            os_warnings.RemovedInSDK50Warning,
        )
        return self.patch_machine(uuid, patch)

    def purge_node_instance_info(self, uuid):
        warnings.warn(
            "The purge_node_instance_info call is deprecated, "
            "use patch_machine or update_machine instead",
            os_warnings.RemovedInSDK50Warning,
        )
        return self.patch_machine(
            uuid, dict(path='/instance_info', op='remove')
        )

    def wait_for_baremetal_node_lock(self, node, timeout=30):
        """Wait for a baremetal node to have no lock.

        DEPRECATED, use ``wait_for_node_reservation`` on the `baremetal` proxy.

        :raises: :class:`~openstack.exceptions.SDKException` upon client
            failure.
        :returns: None
        """
        warnings.warn(
            "The wait_for_baremetal_node_lock call is deprecated "
            "in favor of wait_for_node_reservation on the baremetal "
            "proxy",
            os_warnings.RemovedInSDK50Warning,
        )
        self.baremetal.wait_for_node_reservation(node, timeout)
