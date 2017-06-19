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

import datetime
import iso8601
import jsonpatch

from ironicclient import exceptions as ironic_exceptions

from shade.exc import *  # noqa
from shade import meta
from shade import openstackcloud
from shade import _tasks
from shade import _utils


class OperatorCloud(openstackcloud.OpenStackCloud):
    """Represent a privileged/operator connection to an OpenStack Cloud.

    `OperatorCloud` is the entry point for all admin operations, regardless
    of which OpenStack service those operations are for.

    See the :class:`OpenStackCloud` class for a description of most options.
    """

    def list_nics(self):
        with _utils.shade_exceptions("Error fetching machine port list"):
            return self.manager.submit_task(_tasks.MachinePortList())

    def list_nics_for_machine(self, uuid):
        with _utils.shade_exceptions(
                "Error fetching port list for node {node_id}".format(
                node_id=uuid)):
            return self.manager.submit_task(
                _tasks.MachineNodePortList(node_id=uuid))

    def get_nic_by_mac(self, mac):
        try:
            return self.manager.submit_task(
                _tasks.MachineNodePortGet(port_id=mac))
        except ironic_exceptions.ClientException:
            return None

    def list_machines(self):
        return self._normalize_machines(
            self.manager.submit_task(_tasks.MachineNodeList()))

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
                self.manager.submit_task(
                    _tasks.MachineNodeGet(node_id=name_or_id)))
        except ironic_exceptions.ClientException:
            return None

    def get_machine_by_mac(self, mac):
        """Get machine by port MAC address

        :param mac: Port MAC address to query in order to return a node.

        :returns: ``munch.Munch`` representing the node found or None
                  if the node is not found.
        """
        try:
            port = self.manager.submit_task(
                _tasks.MachinePortGetByAddress(address=mac))
            return self.manager.submit_task(
                _tasks.MachineNodeGet(node_id=port.node_uuid))
        except ironic_exceptions.ClientException:
            return None

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

        machine = self.get_machine(name_or_id)
        if not machine:
            raise OpenStackCloudException(
                "Machine inspection failed to find: %s." % name_or_id)

        # NOTE(TheJulia): If in available state, we can do this, however
        # We need to to move the host back to m
        if "available" in machine['provision_state']:
            return_to_available = True
            # NOTE(TheJulia): Changing available machine to managedable state
            # and due to state transitions we need to until that transition has
            # completd.
            self.node_set_provision_state(machine['uuid'], 'manage',
                                          wait=True, timeout=timeout)
        elif ("manage" not in machine['provision_state'] and
                "inspect failed" not in machine['provision_state']):
            raise OpenStackCloudException(
                "Machine must be in 'manage' or 'available' state to "
                "engage inspection: Machine: %s State: %s"
                % (machine['uuid'], machine['provision_state']))
        with _utils.shade_exceptions("Error inspecting machine"):
            machine = self.node_set_provision_state(machine['uuid'], 'inspect')
            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for node transition to "
                        "target state of 'inspect'"):
                    machine = self.get_machine(name_or_id)

                    if "inspect failed" in machine['provision_state']:
                        raise OpenStackCloudException(
                            "Inspection of node %s failed, last error: %s"
                            % (machine['uuid'], machine['last_error']))

                    if "manageable" in machine['provision_state']:
                        break

            if return_to_available:
                machine = self.node_set_provision_state(
                    machine['uuid'], 'provide', wait=wait, timeout=timeout)

            return(machine)

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

        :param list nics:
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
        with _utils.shade_exceptions("Error registering machine with Ironic"):
            machine = self.manager.submit_task(_tasks.MachineCreate(**kwargs))

        created_nics = []
        try:
            for row in nics:
                nic = self.manager.submit_task(
                    _tasks.MachinePortCreate(address=row['mac'],
                                             node_uuid=machine['uuid']))
                created_nics.append(nic.uuid)

        except Exception as e:
            self.log.debug("ironic NIC registration failed", exc_info=True)
            # TODO(mordred) Handle failures here
            try:
                for uuid in created_nics:
                    try:
                        self.manager.submit_task(
                            _tasks.MachinePortDelete(
                                port_id=uuid))
                    except Exception:
                        pass
            finally:
                self.manager.submit_task(
                    _tasks.MachineDelete(node_id=machine['uuid']))
            raise OpenStackCloudException(
                "Error registering NICs with the baremetal service: %s"
                % str(e))

        with _utils.shade_exceptions(
                "Error transitioning node to available state"):
            if wait:
                for count in _utils._iterate_timeout(
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
                        raise OpenStackCloudException(
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
                    for count in _utils._iterate_timeout(
                            lock_timeout,
                            "Timeout waiting for reservation to clear "
                            "before setting provide state"):
                        machine = self.get_machine(machine['uuid'])
                        if (machine['reservation'] is None and
                           machine['provision_state'] is not 'enroll'):

                            self.node_set_provision_state(
                                machine['uuid'], 'provide')
                            machine = self.get_machine(machine['uuid'])
                            break

                        elif machine['provision_state'] in [
                                'cleaning',
                                'available']:
                            break

                        elif machine['last_error'] is not None:
                            raise OpenStackCloudException(
                                "Machine encountered a failure: %s"
                                % machine['last_error'])

        return machine

    def unregister_machine(self, nics, uuid, wait=False, timeout=600):
        """Unregister Baremetal from Ironic

        Removes entries for Network Interfaces and baremetal nodes
        from an Ironic API

        :param list nics: An array of strings that consist of MAC addresses
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
            raise OpenStackCloudException(
                "Error unregistering node '%s' due to current provision "
                "state '%s'" % (uuid, machine['provision_state']))

        for nic in nics:
            with _utils.shade_exceptions(
                    "Error removing NIC {nic} from baremetal API for node "
                    "{uuid}".format(nic=nic, uuid=uuid)):
                port = self.manager.submit_task(
                    _tasks.MachinePortGetByAddress(address=nic['mac']))
                self.manager.submit_task(
                    _tasks.MachinePortDelete(port_id=port.uuid))
        with _utils.shade_exceptions(
                "Error unregistering machine {node_id} from the baremetal "
                "API".format(node_id=uuid)):
            self.manager.submit_task(
                _tasks.MachineDelete(node_id=uuid))
            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for machine to be deleted"):
                    if not self.get_machine(uuid):
                        break

    def patch_machine(self, name_or_id, patch):
        """Patch Machine Information

        This method allows for an interface to manipulate node entries
        within Ironic.  Specifically, it is a pass-through for the
        ironicclient.nodes.update interface which allows the Ironic Node
        properties to be updated.

        :param node_id: The server object to attach to.
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

        with _utils.shade_exceptions(
            "Error updating machine via patch operation on node "
            "{node}".format(node=name_or_id)
        ):
            return self.manager.submit_task(
                _tasks.MachinePatch(node_id=name_or_id,
                                    patch=patch,
                                    http_method='PATCH'))

    def update_machine(self, name_or_id, chassis_uuid=None, driver=None,
                       driver_info=None, name=None, instance_info=None,
                       instance_uuid=None, properties=None):
        """Update a machine with new configuration information

        A user-friendly method to perform updates of a machine, in whole or
        part.

        :param string name_or_id: A machine name or UUID to be updated.
        :param string chassis_uuid: Assign a chassis UUID to the machine.
                                    NOTE: As of the Kilo release, this value
                                    cannot be changed once set. If a user
                                    attempts to change this value, then the
                                    Ironic API, as of Kilo, will reject the
                                    request.
        :param string driver: The driver name for controlling the machine.
        :param dict driver_info: The dictonary defining the configuration
                                 that the driver will utilize to control
                                 the machine.  Permutations of this are
                                 dependent upon the specific driver utilized.
        :param string name: A human relatable name to represent the machine.
        :param dict instance_info: A dictonary of configuration information
                                   that conveys to the driver how the host
                                   is to be configured when deployed.
                                   be deployed to the machine.
        :param string instance_uuid: A UUID value representing the instance
                                     that the deployed machine represents.
        :param dict properties: A dictonary defining the properties of a
                                machine.

        :raises: OpenStackCloudException on operation error.

        :returns: ``munch.Munch`` containing a machine sub-dictonary consisting
                  of the updated data returned from the API update operation,
                  and a list named changes which contains all of the API paths
                  that received updates.
        """
        machine = self.get_machine(name_or_id)
        if not machine:
            raise OpenStackCloudException(
                "Machine update failed to find Machine: %s. " % name_or_id)

        machine_config = {}
        new_config = {}

        try:
            if chassis_uuid:
                machine_config['chassis_uuid'] = machine['chassis_uuid']
                new_config['chassis_uuid'] = chassis_uuid

            if driver:
                machine_config['driver'] = machine['driver']
                new_config['driver'] = driver

            if driver_info:
                machine_config['driver_info'] = machine['driver_info']
                new_config['driver_info'] = driver_info

            if name:
                machine_config['name'] = machine['name']
                new_config['name'] = name

            if instance_info:
                machine_config['instance_info'] = machine['instance_info']
                new_config['instance_info'] = instance_info

            if instance_uuid:
                machine_config['instance_uuid'] = machine['instance_uuid']
                new_config['instance_uuid'] = instance_uuid

            if properties:
                machine_config['properties'] = machine['properties']
                new_config['properties'] = properties
        except KeyError as e:
            self.log.debug(
                "Unexpected machine response missing key %s [%s]",
                e.args[0], name_or_id)
            raise OpenStackCloudException(
                "Machine update failed - machine [%s] missing key %s. "
                "Potential API issue."
                % (name_or_id, e.args[0]))

        try:
            patch = jsonpatch.JsonPatch.from_diff(machine_config, new_config)
        except Exception as e:
            raise OpenStackCloudException(
                "Machine update failed - Error generating JSON patch object "
                "for submission to the API. Machine: %s Error: %s"
                % (name_or_id, str(e)))

        with _utils.shade_exceptions(
            "Machine update failed - patch operation failed on Machine "
            "{node}".format(node=name_or_id)
        ):
            if not patch:
                return dict(
                    node=machine,
                    changes=None
                )
            else:
                machine = self.patch_machine(machine['uuid'], list(patch))
                change_list = []
                for change in list(patch):
                    change_list.append(change['path'])
                return dict(
                    node=machine,
                    changes=change_list
                )

    def validate_node(self, uuid):
        with _utils.shade_exceptions():
            ifaces = self.manager.submit_task(
                _tasks.MachineNodeValidate(node_uuid=uuid))

        if not ifaces.deploy or not ifaces.power:
            raise OpenStackCloudException(
                "ironic node %s failed to validate. "
                "(deploy: %s, power: %s)" % (ifaces.deploy, ifaces.power))

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
        with _utils.shade_exceptions(
            "Baremetal machine node failed change provision state to "
            "{state}".format(state=state)
        ):
            machine = self.manager.submit_task(
                _tasks.MachineSetProvision(node_uuid=name_or_id,
                                           state=state,
                                           configdrive=configdrive))

            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for node transition to "
                        "target state of '%s'" % state):
                    machine = self.get_machine(name_or_id)
                    if 'failed' in machine['provision_state']:
                        raise OpenStackCloudException(
                            "Machine encountered a failure.")
                    # NOTE(TheJulia): This performs matching if the requested
                    # end state matches the state the node has reached.
                    if state in machine['provision_state']:
                        break
                    # NOTE(TheJulia): This performs matching for cases where
                    # the reqeusted state action ends in available state.
                    if ("available" in machine['provision_state'] and
                            state in ["provide", "deleted"]):
                        break
            else:
                machine = self.get_machine(name_or_id)
            return machine

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
        with _utils.shade_exceptions(
            "Error setting machine maintenance state to {state} on node "
            "{node}".format(state=state, node=name_or_id)
        ):
            if state:
                result = self.manager.submit_task(
                    _tasks.MachineSetMaintenance(node_id=name_or_id,
                                                 state='true',
                                                 maint_reason=reason))
            else:
                result = self.manager.submit_task(
                    _tasks.MachineSetMaintenance(node_id=name_or_id,
                                                 state='false'))
            if result is not None:
                raise OpenStackCloudException(
                    "Failed setting machine maintenance state to %s "
                    "on node %s. Received: %s" % (
                        state, name_or_id, result))
            return None

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
        self.set_machine_maintenance_state(name_or_id, False)

    def _set_machine_power_state(self, name_or_id, state):
        """Set machine power state to on or off

        This private method allows a user to turn power on or off to
        a node via the Baremetal API.

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "on"
                                   state.
        :params string state: A value of "on", "off", or "reboot" that is
                              passed to the baremetal API to be asserted to
                              the machine.  In the case of the "reboot" state,
                              Ironic will return the host to the "on" state.

        :raises: OpenStackCloudException on operation error or.

        :returns: None
        """
        with _utils.shade_exceptions(
            "Error setting machine power state to {state} on node "
            "{node}".format(state=state, node=name_or_id)
        ):
            power = self.manager.submit_task(
                _tasks.MachineSetPower(node_id=name_or_id,
                                       state=state))
            if power is not None:
                raise OpenStackCloudException(
                    "Failed setting machine power state %s on node %s. "
                    "Received: %s" % (state, name_or_id, power))
            return None

    def set_machine_power_on(self, name_or_id):
        """Activate baremetal machine power

        This is a method that sets the node power state to "on".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "on"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self._set_machine_power_state(name_or_id, 'on')

    def set_machine_power_off(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "off".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "off"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns:
        """
        self._set_machine_power_state(name_or_id, 'off')

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
        self._set_machine_power_state(name_or_id, 'reboot')

    def activate_node(self, uuid, configdrive=None,
                      wait=False, timeout=1200):
        self.node_set_provision_state(
            uuid, 'active', configdrive, wait=wait, timeout=timeout)

    def deactivate_node(self, uuid, wait=False,
                        timeout=1200):
        self.node_set_provision_state(
            uuid, 'deleted', wait=wait, timeout=timeout)

    def set_node_instance_info(self, uuid, patch):
        with _utils.shade_exceptions():
            return self.manager.submit_task(
                _tasks.MachineNodeUpdate(node_id=uuid, patch=patch))

    def purge_node_instance_info(self, uuid):
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        with _utils.shade_exceptions():
            return self.manager.submit_task(
                _tasks.MachineNodeUpdate(node_id=uuid, patch=patch))

    @_utils.valid_kwargs('type', 'service_type', 'description')
    def create_service(self, name, enabled=True, **kwargs):
        """Create a service.

        :param name: Service name.
        :param type: Service type. (type or service_type required.)
        :param service_type: Service type. (type or service_type required.)
        :param description: Service description (optional).
        :param enabled: Whether the service is enabled (v3 only)

        :returns: a ``munch.Munch`` containing the services description,
            i.e. the following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - service_type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.

        """
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        if self.cloud_config.get_api_version('identity').startswith('2'):
            kwargs['service_type'] = type_ or service_type
        else:
            kwargs['type'] = type_ or service_type
            kwargs['enabled'] = enabled

        with _utils.shade_exceptions(
            "Failed to create service {name}".format(name=name)
        ):
            service = self.manager.submit_task(
                _tasks.ServiceCreate(name=name, **kwargs)
            )

        return _utils.normalize_keystone_services([service])[0]

    @_utils.valid_kwargs('name', 'enabled', 'type', 'service_type',
                         'description')
    def update_service(self, name_or_id, **kwargs):
        # NOTE(SamYaple): Service updates are only available on v3 api
        if self.cloud_config.get_api_version('identity').startswith('2'):
            raise OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Service update requires Identity v3'
            )

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        # NOTE(SamYaple): Keystone v3 only accepts 'type' but shade accepts
        #                 both 'type' and 'service_type' with a preference
        #                 towards 'type'
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)
        if type_ or service_type:
            kwargs['type'] = type_ or service_type

        with _utils.shade_exceptions(
            "Error in updating service {service}".format(service=name_or_id)
        ):
            service = self.manager.submit_task(
                _tasks.ServiceUpdate(service=name_or_id, **kwargs)
            )

        return _utils.normalize_keystone_services([service])[0]

    def list_services(self):
        """List all Keystone services.

        :returns: a list of ``munch.Munch`` containing the services description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        with _utils.shade_exceptions():
            services = self.manager.submit_task(_tasks.ServiceList())
        return _utils.normalize_keystone_services(services)

    def search_services(self, name_or_id=None, filters=None):
        """Search Keystone services.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                        {'type': 'network'}.

        :returns: a list of ``munch.Munch`` containing the services description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        services = self.list_services()
        return _utils._filter_list(services, name_or_id, filters)

    def get_service(self, name_or_id, filters=None):
        """Get exactly one Keystone service.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                {'type': 'network'}

        :returns: a ``munch.Munch`` containing the services description,
            i.e. the following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call or if multiple matches are found.
        """
        return _utils._get_entity(self.search_services, name_or_id, filters)

    def delete_service(self, name_or_id):
        """Delete a Keystone service.

        :param name_or_id: Service name or id.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call
        """
        service = self.get_service(name_or_id=name_or_id)
        if service is None:
            self.log.debug("Service %s not found for deleting", name_or_id)
            return False

        if self.cloud_config.get_api_version('identity').startswith('2'):
            service_kwargs = {'id': service['id']}
        else:
            service_kwargs = {'service': service['id']}
        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        with _utils.shade_exceptions("Failed to delete service {id}".format(
                id=service['id'])):
            self.manager.submit_task(_tasks.ServiceDelete(**service_kwargs))

        return True

    @_utils.valid_kwargs('public_url', 'internal_url', 'admin_url')
    def create_endpoint(self, service_name_or_id, url=None, interface=None,
                        region=None, enabled=True, **kwargs):
        """Create a Keystone endpoint.

        :param service_name_or_id: Service name or id for this endpoint.
        :param url: URL of the endpoint
        :param interface: Interface type of the endpoint
        :param public_url: Endpoint public URL.
        :param internal_url: Endpoint internal URL.
        :param admin_url: Endpoint admin URL.
        :param region: Endpoint region.
        :param enabled: Whether the endpoint is enabled

        NOTE: Both v2 (public_url, internal_url, admin_url) and v3
              (url, interface) calling semantics are supported. But
              you can only use one of them at a time.

        :returns: a list of ``munch.Munch`` containing the endpoint description

        :raises: OpenStackCloudException if the service cannot be found or if
            something goes wrong during the openstack API call.
        """
        public_url = kwargs.pop('public_url', None)
        internal_url = kwargs.pop('internal_url', None)
        admin_url = kwargs.pop('admin_url', None)

        if (url or interface) and (public_url or internal_url or admin_url):
            raise OpenStackCloudException(
                "create_endpoint takes either url and interface OR"
                " public_url, internal_url, admin_url")

        service = self.get_service(name_or_id=service_name_or_id)
        if service is None:
            raise OpenStackCloudException("service {service} not found".format(
                service=service_name_or_id))

        endpoints = []
        endpoint_args = []
        if url:
            urlkwargs = {}
            if self.cloud_config.get_api_version('identity').startswith('2'):
                if interface != 'public':
                    raise OpenStackCloudException(
                        "Error adding endpoint for service {service}."
                        " On a v2 cloud the url/interface API may only be"
                        " used for public url. Try using the public_url,"
                        " internal_url, admin_url parameters instead of"
                        " url and interface".format(
                            service=service_name_or_id))
                urlkwargs['{}url'.format(interface)] = url
            else:
                urlkwargs['url'] = url
                urlkwargs['interface'] = interface
            endpoint_args.append(urlkwargs)
        else:
            expected_endpoints = {'public': public_url,
                                  'internal': internal_url,
                                  'admin': admin_url}
            if self.cloud_config.get_api_version('identity').startswith('2'):
                urlkwargs = {}
                for interface, url in expected_endpoints.items():
                    if url:
                        urlkwargs['{}url'.format(interface)] = url
                endpoint_args.append(urlkwargs)
            else:
                for interface, url in expected_endpoints.items():
                    if url:
                        urlkwargs = {}
                        urlkwargs['url'] = url
                        urlkwargs['interface'] = interface
                        endpoint_args.append(urlkwargs)

        if self.cloud_config.get_api_version('identity').startswith('2'):
            kwargs['service_id'] = service['id']
            # Keystone v2 requires 'region' arg even if it is None
            kwargs['region'] = region
        else:
            kwargs['service'] = service['id']
            kwargs['enabled'] = enabled
            if region is not None:
                kwargs['region'] = region

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        with _utils.shade_exceptions(
            "Failed to create endpoint for service"
            " {service}".format(service=service['name'])
        ):
            for args in endpoint_args:
                # NOTE(SamYaple): Add shared kwargs to endpoint args
                args.update(kwargs)
                endpoint = self.manager.submit_task(
                    _tasks.EndpointCreate(**args)
                )
                endpoints.append(endpoint)
            return endpoints

    @_utils.valid_kwargs('enabled', 'service_name_or_id', 'url', 'interface',
                         'region')
    def update_endpoint(self, endpoint_id, **kwargs):
        # NOTE(SamYaple): Endpoint updates are only available on v3 api
        if self.cloud_config.get_api_version('identity').startswith('2'):
            raise OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Endpoint update'
            )

        service_name_or_id = kwargs.pop('service_name_or_id', None)
        if service_name_or_id is not None:
            kwargs['service'] = service_name_or_id

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        with _utils.shade_exceptions(
            "Failed to update endpoint {}".format(endpoint_id)
        ):
            return self.manager.submit_task(_tasks.EndpointUpdate(
                endpoint=endpoint_id, **kwargs
            ))

    def list_endpoints(self):
        """List Keystone endpoints.

        :returns: a list of ``munch.Munch`` containing the endpoint description

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        # NOTE(SamYaple): With keystone v3 we can filter directly via the
        # the keystone api, but since the return of all the endpoints even in
        # large environments is small, we can continue to filter in shade just
        # like the v2 api.
        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        with _utils.shade_exceptions("Failed to list endpoints"):
            endpoints = self.manager.submit_task(_tasks.EndpointList())

        return endpoints

    def search_endpoints(self, id=None, filters=None):
        """List Keystone endpoints.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a list of ``munch.Munch`` containing the endpoint
            description. Each dict contains the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        endpoints = self.list_endpoints()
        return _utils._filter_list(endpoints, id, filters)

    def get_endpoint(self, id, filters=None):
        """Get exactly one Keystone endpoint.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a ``munch.Munch`` containing the endpoint description.
            i.e. a ``munch.Munch`` containing the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)
        """
        return _utils._get_entity(self.search_endpoints, id, filters)

    def delete_endpoint(self, id):
        """Delete a Keystone endpoint.

        :param id: Id of the endpoint to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        endpoint = self.get_endpoint(id=id)
        if endpoint is None:
            self.log.debug("Endpoint %s not found for deleting", id)
            return False

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        if self.cloud_config.get_api_version('identity').startswith('2'):
            endpoint_kwargs = {'id': endpoint['id']}
        else:
            endpoint_kwargs = {'endpoint': endpoint['id']}
        with _utils.shade_exceptions("Failed to delete endpoint {id}".format(
                id=id)):
            self.manager.submit_task(_tasks.EndpointDelete(**endpoint_kwargs))

        return True

    def create_domain(
            self, name, description=None, enabled=True):
        """Create a Keystone domain.

        :param name: The name of the domain.
        :param description: A description of the domain.
        :param enabled: Is the domain enabled or not (default True).

        :returns: a ``munch.Munch`` containing the domain description

        :raise OpenStackCloudException: if the domain cannot be created
        """
        with _utils.shade_exceptions("Failed to create domain {name}".format(
                name=name)):
            domain = self.manager.submit_task(_tasks.DomainCreate(
                name=name,
                description=description,
                enabled=enabled))
        return _utils.normalize_domains([domain])[0]

    def update_domain(
            self, domain_id=None, name=None, description=None,
            enabled=None, name_or_id=None):
        if domain_id is None:
            if name_or_id is None:
                raise OpenStackCloudException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(None, name_or_id)
            if dom is None:
                raise OpenStackCloudException(
                    "Domain {0} not found for updating".format(name_or_id)
                )
            domain_id = dom['id']

        with _utils.shade_exceptions(
                "Error in updating domain {domain}".format(domain=domain_id)):
            domain = self.manager.submit_task(_tasks.DomainUpdate(
                domain=domain_id, name=name, description=description,
                enabled=enabled))
        return _utils.normalize_domains([domain])[0]

    def delete_domain(self, domain_id=None, name_or_id=None):
        """Delete a Keystone domain.

        :param domain_id: ID of the domain to delete.
        :param name_or_id: Name or ID of the domain to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        if domain_id is None:
            if name_or_id is None:
                raise OpenStackCloudException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(None, name_or_id)
            if dom is None:
                self.log.debug(
                    "Domain %s not found for deleting", name_or_id)
                return False
            domain_id = dom['id']

        with _utils.shade_exceptions(
                "Failed to delete domain {id}".format(id=domain_id)):
            # Deleting a domain is expensive, so disabling it first increases
            # the changes of success
            domain = self.update_domain(domain_id, enabled=False)
            self.manager.submit_task(_tasks.DomainDelete(domain=domain['id']))

        return True

    def list_domains(self):
        """List Keystone domains.

        :returns: a list of ``munch.Munch`` containing the domain description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        with _utils.shade_exceptions("Failed to list domains"):
            domains = self.manager.submit_task(_tasks.DomainList())
        return _utils.normalize_domains(domains)

    def search_domains(self, filters=None, name_or_id=None):
        """Search Keystone domains.

        :param name_or_id: domain name or id
        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a list of ``munch.Munch`` containing the domain description.
            Each ``munch.Munch`` contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        if filters is None:
            filters = {}
        if name_or_id is not None:
            domains = self.list_domains()
            return _utils._filter_list(domains, name_or_id, filters)
        else:
            with _utils.shade_exceptions("Failed to list domains"):
                domains = self.manager.submit_task(
                    _tasks.DomainList(**filters))
            return _utils.normalize_domains(domains)

    def get_domain(self, domain_id=None, name_or_id=None, filters=None):
        """Get exactly one Keystone domain.

        :param domain_id: domain id.
        :param name_or_id: domain name or id.
        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a ``munch.Munch`` containing the domain description, or None
            if not found. Each ``munch.Munch`` contains the following
            attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        if domain_id is None:
            return _utils._get_entity(self.search_domains, filters, name_or_id)
        else:
            with _utils.shade_exceptions(
                "Failed to get domain "
                "{domain_id}".format(domain_id=domain_id)
            ):
                domain = self.manager.submit_task(
                    _tasks.DomainGet(domain=domain_id))
            return _utils.normalize_domains([domain])[0]

    @_utils.cache_on_arguments()
    def list_groups(self):
        """List Keystone Groups.

        :returns: A list of ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        with _utils.shade_exceptions("Failed to list groups"):
            groups = self.manager.submit_task(_tasks.GroupList())
        return _utils.normalize_groups(groups)

    def search_groups(self, name_or_id=None, filters=None):
        """Search Keystone groups.

        :param name: Group name or id.
        :param filters: A dict containing additional filters to use.

        :returns: A list of ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        groups = self.list_groups()
        return _utils._filter_list(groups, name_or_id, filters)

    def get_group(self, name_or_id, filters=None):
        """Get exactly one Keystone group.

        :param id: Group name or id.
        :param filters: A dict containing additional filters to use.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        return _utils._get_entity(self.search_groups, name_or_id, filters)

    def create_group(self, name, description, domain=None):
        """Create a group.

        :param string name: Group name.
        :param string description: Group description.
        :param string domain: Domain name or ID for the group.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        with _utils.shade_exceptions(
            "Error creating group {group}".format(group=name)
        ):
            domain_id = None
            if domain:
                dom = self.get_domain(domain)
                if not dom:
                    raise OpenStackCloudException(
                        "Creating group {group} failed: Invalid domain "
                        "{domain}".format(group=name, domain=domain)
                    )
                domain_id = dom['id']

            group = self.manager.submit_task(_tasks.GroupCreate(
                name=name, description=description, domain=domain_id)
            )
        self.list_groups.invalidate(self)
        return _utils.normalize_groups([group])[0]

    def update_group(self, name_or_id, name=None, description=None):
        """Update an existing group

        :param string name: New group name.
        :param string description: New group description.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        self.list_groups.invalidate(self)
        group = self.get_group(name_or_id)
        if group is None:
            raise OpenStackCloudException(
                "Group {0} not found for updating".format(name_or_id)
            )

        with _utils.shade_exceptions(
            "Unable to update group {name}".format(name=name_or_id)
        ):
            group = self.manager.submit_task(_tasks.GroupUpdate(
                group=group['id'], name=name, description=description))

        self.list_groups.invalidate(self)
        return _utils.normalize_groups([group])[0]

    def delete_group(self, name_or_id):
        """Delete a group

        :param name_or_id: ID or name of the group to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        group = self.get_group(name_or_id)
        if group is None:
            self.log.debug(
                "Group %s not found for deleting", name_or_id)
            return False

        with _utils.shade_exceptions(
            "Unable to delete group {name}".format(name=name_or_id)
        ):
            self.manager.submit_task(_tasks.GroupDelete(group=group['id']))

        self.list_groups.invalidate(self)
        return True

    def list_roles(self):
        """List Keystone roles.

        :returns: a list of ``munch.Munch`` containing the role description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        with _utils.shade_exceptions():
            roles = self.manager.submit_task(_tasks.RoleList())

        return roles

    def search_roles(self, name_or_id=None, filters=None):
        """Seach Keystone roles.

        :param string name: role name or id.
        :param dict filters: a dict containing additional filters to use.

        :returns: a list of ``munch.Munch`` containing the role description.
            Each ``munch.Munch`` contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        roles = self.list_roles()
        return _utils._filter_list(roles, name_or_id, filters)

    def get_role(self, name_or_id, filters=None):
        """Get exactly one Keystone role.

        :param id: role name or id.
        :param filters: a dict containing additional filters to use.

        :returns: a single ``munch.Munch`` containing the role description.
            Each ``munch.Munch`` contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        return _utils._get_entity(self.search_roles, name_or_id, filters)

    def _keystone_v2_role_assignments(self, user, project=None,
                                      role=None, **kwargs):
        with _utils.shade_exceptions("Failed to list role assignments"):
            roles = self.manager.submit_task(
                _tasks.RolesForUser(user=user, tenant=project)
            )
        ret = []
        for tmprole in roles:
            if role is not None and role != tmprole.id:
                continue
            ret.append({
                'role': {
                    'id': tmprole.id
                },
                'scope': {
                    'project': {
                        'id': project,
                    }
                },
                'user': {
                    'id': user,
                }
            })
        return ret

    def list_role_assignments(self, filters=None):
        """List Keystone role assignments

        :param dict filters: Dict of filter conditions. Acceptable keys are:

            * 'user' (string) - User ID to be used as query filter.
            * 'group' (string) - Group ID to be used as query filter.
            * 'project' (string) - Project ID to be used as query filter.
            * 'domain' (string) - Domain ID to be used as query filter.
            * 'role' (string) - Role ID to be used as query filter.
            * 'os_inherit_extension_inherited_to' (string) - Return inherited
              role assignments for either 'projects' or 'domains'
            * 'effective' (boolean) - Return effective role assignments.
            * 'include_subtree' (boolean) - Include subtree

            'user' and 'group' are mutually exclusive, as are 'domain' and
            'project'.

            NOTE: For keystone v2, only user, project, and role are used.
                  Project and user are both required in filters.

        :returns: a list of ``munch.Munch`` containing the role assignment
            description. Contains the following attributes::

                - id: <role id>
                - user|group: <user or group id>
                - project|domain: <project or domain id>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        if not filters:
            filters = {}

        if self.cloud_config.get_api_version('identity').startswith('2'):
            if filters.get('project') is None or filters.get('user') is None:
                raise OpenStackCloudException(
                    "Must provide project and user for keystone v2"
                )
            assignments = self._keystone_v2_role_assignments(**filters)
        else:
            with _utils.shade_exceptions("Failed to list role assignments"):
                assignments = self.manager.submit_task(
                    _tasks.RoleAssignmentList(**filters)
                )
        return _utils.normalize_role_assignments(assignments)

    def create_flavor(self, name, ram, vcpus, disk, flavorid="auto",
                      ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True):
        """Create a new flavor.

        :param name: Descriptive name of the flavor
        :param ram: Memory in MB for the flavor
        :param vcpus: Number of VCPUs for the flavor
        :param disk: Size of local disk in GB
        :param flavorid: ID for the flavor (optional)
        :param ephemeral: Ephemeral space size in GB
        :param swap: Swap space in MB
        :param rxtx_factor: RX/TX factor
        :param is_public: Make flavor accessible to the public

        :returns: A ``munch.Munch`` describing the new flavor.

        :raises: OpenStackCloudException on operation error.
        """
        with _utils.shade_exceptions("Failed to create flavor {name}".format(
                name=name)):
            payload = {
                'disk': disk,
                'OS-FLV-EXT-DATA:ephemeral': ephemeral,
                'id': flavorid,
                'os-flavor-access:is_public': is_public,
                'name': name,
                'ram': ram,
                'rxtx_factor': rxtx_factor,
                'swap': swap,
                'vcpus': vcpus,
            }
            if flavorid == 'auto':
                payload['id'] = None
            flavor = self._compute_client.post(
                '/flavors',
                json=dict(flavor=payload))

        return self._normalize_flavor(flavor)

    def delete_flavor(self, name_or_id):
        """Delete a flavor

        :param name_or_id: ID or name of the flavor to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        flavor = self.get_flavor(name_or_id, get_extra=False)
        if flavor is None:
            self.log.debug(
                "Flavor %s not found for deleting", name_or_id)
            return False

        with _utils.shade_exceptions("Unable to delete flavor {name}".format(
                name=name_or_id)):
            self._compute_client.delete(
                '/flavors/{id}'.format(id=flavor['id']))

        return True

    def set_flavor_specs(self, flavor_id, extra_specs):
        """Add extra specs to a flavor

        :param string flavor_id: ID of the flavor to update.
        :param dict extra_specs: Dictionary of key-value pairs.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        try:
            self._compute_client.post(
                "/flavors/{id}/os-extra_specs".format(id=flavor_id),
                json=dict(extra_specs=extra_specs))
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to set flavor specs: {0}".format(str(e))
            )

    def unset_flavor_specs(self, flavor_id, keys):
        """Delete extra specs from a flavor

        :param string flavor_id: ID of the flavor to update.
        :param list keys: List of spec keys to delete.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        for key in keys:
            try:
                self._compute_client.delete(
                    "/flavors/{id}/os-extra_specs/{key}".format(
                        id=flavor_id, key=key))
            except Exception as e:
                raise OpenStackCloudException(
                    "Unable to delete flavor spec {0}: {1}".format(
                        key, str(e)))

    def _mod_flavor_access(self, action, flavor_id, project_id):
        """Common method for adding and removing flavor access
        """
        with _utils.shade_exceptions("Error trying to {action} access from "
                                     "flavor ID {flavor}".format(
                                         action=action, flavor=flavor_id)):
            endpoint = '/flavors/{id}/action'.format(id=flavor_id)
            access = {'tenant': project_id}
            access_key = '{action}TenantAccess'.format(action=action)

            self._compute_client.post(endpoint, json={access_key: access})

    def add_flavor_access(self, flavor_id, project_id):
        """Grant access to a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.
        :param string project_id: ID of the project/tenant.

        :raises: OpenStackCloudException on operation error.
        """
        self._mod_flavor_access('add', flavor_id, project_id)

    def remove_flavor_access(self, flavor_id, project_id):
        """Revoke access from a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.
        :param string project_id: ID of the project/tenant.

        :raises: OpenStackCloudException on operation error.
        """
        self._mod_flavor_access('remove', flavor_id, project_id)

    def list_flavor_access(self, flavor_id):
        """List access from a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.

        :returns: a list of ``munch.Munch`` containing the access description

        :raises: OpenStackCloudException on operation error.
        """
        with _utils.shade_exceptions("Error trying to list access from "
                                     "flavor ID {flavor}".format(
                flavor=flavor_id)):
            projects = self._compute_client.get(
                '/flavors/{id}/os-flavor-access'.format(id=flavor_id))
        return _utils.normalize_flavor_accesses(projects)

    def create_role(self, name):
        """Create a Keystone role.

        :param string name: The name of the role.

        :returns: a ``munch.Munch`` containing the role description

        :raise OpenStackCloudException: if the role cannot be created
        """
        with _utils.shade_exceptions():
            role = self.manager.submit_task(
                _tasks.RoleCreate(name=name)
            )
        return role

    def delete_role(self, name_or_id):
        """Delete a Keystone role.

        :param string id: Name or id of the role to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        role = self.get_role(name_or_id)
        if role is None:
            self.log.debug(
                "Role %s not found for deleting", name_or_id)
            return False

        with _utils.shade_exceptions("Unable to delete role {name}".format(
                name=name_or_id)):
            self.manager.submit_task(_tasks.RoleDelete(role=role['id']))

        return True

    def _get_grant_revoke_params(self, role, user=None, group=None,
                                 project=None, domain=None):
        role = self.get_role(role)
        if role is None:
            return {}
        data = {'role': role.id}

        # domain and group not available in keystone v2.0
        keystone_version = self.cloud_config.get_api_version('identity')
        is_keystone_v2 = keystone_version.startswith('2')

        filters = {}
        if not is_keystone_v2 and domain:
            filters['domain_id'] = data['domain'] = \
                self.get_domain(domain)['id']

        if user:
            data['user'] = self.get_user(user, filters=filters)

        if project:
            # drop domain in favor of project
            data.pop('domain', None)
            data['project'] = self.get_project(project, filters=filters)

        if not is_keystone_v2 and group:
            data['group'] = self.get_group(group, filters=filters)

        return data

    def grant_role(self, name_or_id, user=None, group=None,
                   project=None, domain=None, wait=False, timeout=60):
        """Grant a role to a user.

        :param string name_or_id: The name or id of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool wait: Wait for role to be granted
        :param int timeout: Timeout to wait for role to be granted

        NOTE: domain is a required argument when the grant is on a project,
            user or group specified by name. In that situation, they are all
            considered to be in that domain. If different domains are in use
            in the same role grant, it is required to specify those by ID.

        NOTE: for wait and timeout, sometimes granting roles is not
              instantaneous for granting roles.

        NOTE: project is required for keystone v2

        :returns: True if the role is assigned, otherwise False

        :raise OpenStackCloudException: if the role cannot be granted
        """
        data = self._get_grant_revoke_params(name_or_id, user, group,
                                             project, domain)
        filters = data.copy()
        if not data:
            raise OpenStackCloudException(
                'Role {0} not found.'.format(name_or_id))

        if data.get('user') is not None and data.get('group') is not None:
            raise OpenStackCloudException(
                'Specify either a group or a user, not both')
        if data.get('user') is None and data.get('group') is None:
            raise OpenStackCloudException(
                'Must specify either a user or a group')
        if self.cloud_config.get_api_version('identity').startswith('2') and \
                data.get('project') is None:
            raise OpenStackCloudException(
                'Must specify project for keystone v2')

        if self.list_role_assignments(filters=filters):
            self.log.debug('Assignment already exists')
            return False

        with _utils.shade_exceptions(
                "Error granting access to role: {0}".format(
                data)):
            if self.cloud_config.get_api_version('identity').startswith('2'):
                data['tenant'] = data.pop('project')
                self.manager.submit_task(_tasks.RoleAddUser(**data))
            else:
                if data.get('project') is None and data.get('domain') is None:
                    raise OpenStackCloudException(
                        'Must specify either a domain or project')
                self.manager.submit_task(_tasks.RoleGrantUser(**data))
        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for role to be granted"):
                if self.list_role_assignments(filters=filters):
                    break
        return True

    def revoke_role(self, name_or_id, user=None, group=None,
                    project=None, domain=None, wait=False, timeout=60):
        """Revoke a role from a user.

        :param string name_or_id: The name or id of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool wait: Wait for role to be revoked
        :param int timeout: Timeout to wait for role to be revoked

        NOTE: for wait and timeout, sometimes revoking roles is not
              instantaneous for revoking roles.

        NOTE: project is required for keystone v2

        :returns: True if the role is revoke, otherwise False

        :raise OpenStackCloudException: if the role cannot be removed
        """
        data = self._get_grant_revoke_params(name_or_id, user, group,
                                             project, domain)
        filters = data.copy()

        if not data:
            raise OpenStackCloudException(
                'Role {0} not found.'.format(name_or_id))

        if data.get('user') is not None and data.get('group') is not None:
            raise OpenStackCloudException(
                'Specify either a group or a user, not both')
        if data.get('user') is None and data.get('group') is None:
            raise OpenStackCloudException(
                'Must specify either a user or a group')
        if self.cloud_config.get_api_version('identity').startswith('2') and \
                data.get('project') is None:
            raise OpenStackCloudException(
                'Must specify project for keystone v2')

        if not self.list_role_assignments(filters=filters):
            self.log.debug('Assignment does not exist')
            return False

        with _utils.shade_exceptions(
                "Error revoking access to role: {0}".format(
                data)):
            if self.cloud_config.get_api_version('identity').startswith('2'):
                data['tenant'] = data.pop('project')
                self.manager.submit_task(_tasks.RoleRemoveUser(**data))
            else:
                if data.get('project') is None and data.get('domain') is None:
                    raise OpenStackCloudException(
                        'Must specify either a domain or project')
                self.manager.submit_task(_tasks.RoleRevokeUser(**data))
        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for role to be revoked"):
                if not self.list_role_assignments(filters=filters):
                    break
        return True

    def list_hypervisors(self):
        """List all hypervisors

        :returns: A list of hypervisor ``munch.Munch``.
        """

        return self._compute_client.get(
            '/os-hypervisors/detail',
            error_message="Error fetching hypervisor list")

    def search_aggregates(self, name_or_id=None, filters=None):
        """Seach host aggregates.

        :param name: aggregate name or id.
        :param filters: a dict containing additional filters to use.

        :returns: a list of dicts containing the aggregates

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        aggregates = self.list_aggregates()
        return _utils._filter_list(aggregates, name_or_id, filters)

    def list_aggregates(self):
        """List all available host aggregates.

        :returns: A list of aggregate dicts.

        """
        return self._compute_client.get(
            '/os-aggregates',
            error_message="Error fetching aggregate list")

    def get_aggregate(self, name_or_id, filters=None):
        """Get an aggregate by name or ID.

        :param name_or_id: Name or ID of the aggregate.
        :param dict filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'availability_zone': 'nova',
                  'metadata': {
                      'cpu_allocation_ratio': '1.0'
                  }
                }

        :returns: An aggregate dict or None if no matching aggregate is
                  found.

        """
        return _utils._get_entity(self.search_aggregates, name_or_id, filters)

    def create_aggregate(self, name, availability_zone=None):
        """Create a new host aggregate.

        :param name: Name of the host aggregate being created
        :param availability_zone: Availability zone to assign hosts

        :returns: a dict representing the new host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        return self._compute_client.post(
            '/os-aggregates',
            json={'aggregate': {
                'name': name,
                'availability_zone': availability_zone
            }},
            error_message="Unable to create host aggregate {name}".format(
                name=name))

    @_utils.valid_kwargs('name', 'availability_zone')
    def update_aggregate(self, name_or_id, **kwargs):
        """Update a host aggregate.

        :param name_or_id: Name or ID of the aggregate being updated.
        :param name: New aggregate name
        :param availability_zone: Availability zone to assign to hosts

        :returns: a dict representing the updated host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        return self._compute_client.put(
            '/os-aggregates/{id}'.format(id=aggregate['id']),
            json={'aggregate': kwargs},
            error_message="Error updating aggregate {name}".format(
                name=name_or_id))

    def delete_aggregate(self, name_or_id):
        """Delete a host aggregate.

        :param name_or_id: Name or ID of the host aggregate to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            self.log.debug("Aggregate %s not found for deleting", name_or_id)
            return False

        return self._compute_client.delete(
            '/os-aggregates/{id}'.format(id=aggregate['id']),
            error_message="Error deleting aggregate {name}".format(
                name=name_or_id))

        return True

    def set_aggregate_metadata(self, name_or_id, metadata):
        """Set aggregate metadata, replacing the existing metadata.

        :param name_or_id: Name of the host aggregate to update
        :param metadata: Dict containing metadata to replace (Use
                {'key': None} to remove a key)

        :returns: a dict representing the new host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        err_msg = "Unable to set metadata for host aggregate {name}".format(
            name=name_or_id)

        return self._compute_client.post(
            '/os-aggregates/{id}/action'.format(id=aggregate['id']),
            json={'set_metadata': {'metadata': metadata}},
            error_message=err_msg)

    def add_host_to_aggregate(self, name_or_id, host_name):
        """Add a host to an aggregate.

        :param name_or_id: Name or ID of the host aggregate.
        :param host_name: Host to add.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        err_msg = "Unable to add host {host} to aggregate {name}".format(
            host=host_name, name=name_or_id)

        return self._compute_client.post(
            '/os-aggregates/{id}/action'.format(id=aggregate['id']),
            json={'add_host': {'host': host_name}},
            error_message=err_msg)

    def remove_host_from_aggregate(self, name_or_id, host_name):
        """Remove a host from an aggregate.

        :param name_or_id: Name or ID of the host aggregate.
        :param host_name: Host to remove.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        err_msg = "Unable to remove host {host} to aggregate {name}".format(
            host=host_name, name=name_or_id)

        return self._compute_client.post(
            '/os-aggregates/{id}/action'.format(id=aggregate['id']),
            json={'remove_host': {'host': host_name}},
            error_message=err_msg)

    def get_volume_type_access(self, name_or_id):
        """Return a list of volume_type_access.

        :param name_or_id: Name or ID of the volume type.

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)

        data = self._volume_client.get(
            '/types/{id}/os-volume-type-access'.format(id=volume_type.id),
            error_message="Unable to get volume type access"
                          " {name}".format(name=name_or_id))
        return self._normalize_volume_type_accesses(
            meta.get_and_munchify('volume_type_access', data))

    def add_volume_type_access(self, name_or_id, project_id):
        """Grant access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        NOTE: the call works even if the project does not exist.

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)
        with _utils.shade_exceptions():
            payload = {'project': project_id}
            self._volume_client.post(
                '/types/{id}/action'.format(id=volume_type.id),
                json=dict(addProjectAccess=payload),
                error_message="Unable to authorize {project} "
                              "to use volume type {name}".format(
                              name=name_or_id, project=project_id))

    def remove_volume_type_access(self, name_or_id, project_id):
        """Revoke access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)
        with _utils.shade_exceptions():
            payload = {'project': project_id}
            self._volume_client.post(
                '/types/{id}/action'.format(id=volume_type.id),
                json=dict(removeProjectAccess=payload),
                error_message="Unable to revoke {project} "
                              "to use volume type {name}".format(
                              name=name_or_id, project=project_id))

    def set_compute_quotas(self, name_or_id, **kwargs):
        """ Set a quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        # compute_quotas = {key: val for key, val in kwargs.items()
        #                  if key in quota.COMPUTE_QUOTAS}
        # TODO(ghe): Manage volume and network quotas
        # network_quotas = {key: val for key, val in kwargs.items()
        #                  if key in quota.NETWORK_QUOTAS}
        # volume_quotas = {key: val for key, val in kwargs.items()
        #                 if key in quota.VOLUME_QUOTAS}

        kwargs['force'] = True
        self._compute_client.put(
            '/os-quota-sets/{project}'.format(project=proj.id),
            json={'quota_set': kwargs},
            error_message="No valid quota or resource")

    def get_compute_quotas(self, name_or_id):
        """ Get quota for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        return self._compute_client.get(
            '/os-quota-sets/{project}'.format(project=proj.id))

    def delete_compute_quotas(self, name_or_id):
        """ Delete quota for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 nova client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        return self._compute_client.delete(
            '/os-quota-sets/{project}'.format(project=proj.id))

    def get_compute_usage(self, name_or_id, start=None, end=None):
        """ Get usage for a specific project

        :param name_or_id: project name or id
        :param start: :class:`datetime.datetime` or string. Start date in UTC
                      Defaults to 2010-07-06T12:00:00Z (the date the OpenStack
                      project was started)
        :param end: :class:`datetime.datetime` or string. End date in UTC.
                    Defaults to now
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the usage
        """
        def parse_date(date):
            try:
                return iso8601.parse_date(date)
            except iso8601.iso8601.ParseError:
                # Yes. This is an exception mask. However,iso8601 is an
                # implementation detail - and the error message is actually
                # less informative.
                raise OpenStackCloudException(
                    "Date given, {date}, is invalid. Please pass in a date"
                    " string in ISO 8601 format -"
                    " YYYY-MM-DDTHH:MM:SS".format(
                        date=date))

        def parse_datetime_for_nova(date):
            # Must strip tzinfo from the date- it breaks Nova. Also,
            # Nova is expecting this in UTC. If someone passes in an
            # ISO8601 date string or a datetime with timzeone data attached,
            # strip the timezone data but apply offset math first so that
            # the user's well formed perfectly valid date will be used
            # correctly.
            offset = date.utcoffset()
            if offset:
                date = date - datetime.timedelta(hours=offset)
            return date.replace(tzinfo=None)

        if not start:
            start = parse_date('2010-07-06')
        elif not isinstance(start, datetime.datetime):
            start = parse_date(start)
        if not end:
            end = datetime.datetime.utcnow()
        elif not isinstance(start, datetime.datetime):
            end = parse_date(end)

        start = parse_datetime_for_nova(start)
        end = parse_datetime_for_nova(end)

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist: {}".format(
                name=proj.id))

        usage = self._compute_client.get(
            '/os-simple-tenant-usage/{project}'.format(project=proj.id),
            params=dict(start=start.isoformat(), end=end.isoformat()),
            error_message="Unable to get usage for project: {name}".format(
                name=proj.id))

        return self._normalize_compute_usage(usage)

    def set_volume_quotas(self, name_or_id, **kwargs):
        """ Set a volume quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        kwargs['tenant_id'] = proj.id
        self._volume_client.put(
            '/os-quota-sets/{tenant_id}'.format(tenant_id=proj.id),
            json={'quota_set': kwargs},
            error_message="No valid quota or resource")

    def get_volume_quotas(self, name_or_id):
        """ Get volume quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        return self._volume_client.get(
            '/os-quota-sets/{tenant_id}'.format(tenant_id=proj.id),
            error_message="cinder client call failed")

    def delete_volume_quotas(self, name_or_id):
        """ Delete volume quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 cinder client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        return self._volume_client.delete(
            '/os-quota-sets/{tenant_id}'.format(tenant_id=proj.id),
            error_message="cinder client call failed")

    def set_network_quotas(self, name_or_id, **kwargs):
        """ Set a network quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        self._network_client.put(
            '/quotas/{project_id}.json'.format(project_id=proj.id),
            json={'quota': kwargs},
            error_message=("Error setting Neutron's quota for "
                           "project {0}".format(proj.id)))

    def get_network_quotas(self, name_or_id):
        """ Get network quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        return self._network_client.get(
            '/quotas/{project_id}.json'.format(project_id=proj.id),
            error_message=("Error fetching Neutron's quota for "
                           "project {0}".format(proj.id)))

    def delete_network_quotas(self, name_or_id):
        """ Delete network quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 network client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        self._network_client.delete(
            '/quotas/{project_id}.json'.format(project_id=proj.id),
            error_message=("Error deleting Neutron's quota for "
                           "project {0}".format(proj.id)))

    def list_magnum_services(self):
        """List all Magnum services.
        :returns: a list of dicts containing the service details.

        :raises: OpenStackCloudException on operation error.
        """
        with _utils.shade_exceptions("Error fetching Magnum services list"):
            return self._normalize_magnum_services(
                self._container_infra_client.get('/mservices'))
