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

import jsonpatch

from ironicclient import client as ironic_client
from ironicclient import exceptions as ironic_exceptions
from novaclient import exceptions as nova_exceptions

from shade.exc import *  # noqa
from shade import openstackcloud
from shade import _tasks
from shade import _utils


class OperatorCloud(openstackcloud.OpenStackCloud):
    """Represent a privileged/operator connection to an OpenStack Cloud.

    `OperatorCloud` is the entry point for all admin operations, regardless
    of which OpenStack service those operations are for.

    See the :class:`OpenStackCloud` class for a description of most options.
    """

    def __init__(self, *args, **kwargs):
        super(OperatorCloud, self).__init__(*args, **kwargs)
        self._ironic_client = None

    # Set the ironic API microversion to a known-good
    # supported/tested with the contents of shade.
    #
    # Note(TheJulia): Defaulted to version 1.6 as the ironic
    # state machine changes which will increment the version
    # and break an automatic transition of an enrolled node
    # to an available state. Locking the version is intended
    # to utilize the original transition until shade supports
    # calling for node inspection to allow the transition to
    # take place automatically.
    ironic_api_microversion = '1.6'

    @property
    def ironic_client(self):
        if self._ironic_client is None:
            self._ironic_client = self._get_client(
                'baremetal', ironic_client.Client,
                os_ironic_api_version=self.ironic_api_microversion)
        return self._ironic_client

    def list_nics(self):
        try:
            return self.manager.submitTask(_tasks.MachinePortList())
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching machine port list: %s" % e)

    def list_nics_for_machine(self, uuid):
        try:
            return self.manager.submitTask(
                _tasks.MachineNodePortList(node_id=uuid))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching port list for node %s: %s" % (uuid, e))

    def get_nic_by_mac(self, mac):
        try:
            return self.manager.submitTask(
                _tasks.MachineNodePortGet(port_id=mac))
        except ironic_exceptions.ClientException:
            return None

    def list_machines(self):
        return self.manager.submitTask(_tasks.MachineNodeList())

    def get_machine(self, name_or_id):
        """Get Machine by name or uuid

        Search the baremetal host out by utilizing the supplied id value
        which can consist of a name or UUID.

        :param name_or_id: A node name or UUID that will be looked up.

        :returns: Dictonary representing the node found or None if no nodes
                  are found.
        """
        try:
            return self.manager.submitTask(
                _tasks.MachineNodeGet(node_id=name_or_id))
        except ironic_exceptions.ClientException:
            return None

    def get_machine_by_mac(self, mac):
        """Get machine by port MAC address

        :param mac: Port MAC address to query in order to return a node.

        :returns: Dictonary representing the node found or None
                  if the node is not found.
        """
        try:
            port = self.manager.submitTask(
                _tasks.MachinePortGetByAddress(address=mac))
            return self.manager.submitTask(
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

        :returns: Dictonary representing the current state of the machine
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
        try:
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

        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error inspecting machine: %s" % e)

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

        :returns: Returns a dictonary representing the new
                  baremetal node.
        """
        try:
            machine = self.manager.submitTask(_tasks.MachineCreate(**kwargs))

        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error registering machine with Ironic: %s" % str(e))

        created_nics = []
        try:
            for row in nics:
                nic = self.manager.submitTask(
                    _tasks.MachinePortCreate(address=row['mac'],
                                             node_uuid=machine['uuid']))
                created_nics.append(nic.uuid)

        except Exception as e:
            self.log.debug("ironic NIC registration failed", exc_info=True)
            # TODO(mordred) Handle failures here
            try:
                for uuid in created_nics:
                    try:
                        self.manager.submitTask(
                            _tasks.MachinePortDelete(
                                port_id=uuid))
                    except:
                        pass
            finally:
                self.manager.submitTask(
                    _tasks.MachineDelete(node_id=machine['uuid']))
            raise OpenStackCloudException(
                "Error registering NICs with the baremetal service: %s"
                % str(e))

        try:
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

        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error transitioning node to available state: %s"
                % e)
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
            try:
                port = self.manager.submitTask(
                    _tasks.MachinePortGetByAddress(address=nic['mac']))
                self.manager.submitTask(
                    _tasks.MachinePortDelete(port_id=port.uuid))
            except OpenStackCloudException:
                raise
            except Exception as e:
                raise OpenStackCloudException(
                    "Error removing NIC '%s' from baremetal API for "
                    "node '%s'. Error: %s" % (nic, uuid, str(e)))
        try:
            self.manager.submitTask(
                _tasks.MachineDelete(node_id=uuid))
            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for machine to be deleted"):
                    if not self.get_machine(uuid):
                        break

        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error unregistering machine %s from the baremetal API. "
                "Error: %s" % (uuid, str(e)))

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

        :returns: Dictonary representing the newly updated node.
        """

        try:
            return self.manager.submitTask(
                _tasks.MachinePatch(node_id=name_or_id,
                                    patch=patch,
                                    http_method='PATCH'))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error updating machine via patch operation. node: %s. "
                "%s" % (name_or_id, str(e)))

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

        :returns: Dictonary containing a machine sub-dictonary consisting
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
                "Unexpected machine response missing key %s [%s]" % (
                    e.args[0], name_or_id))
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

        try:
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
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Machine update failed - patch operation failed Machine: %s "
                "Error: %s" % (name_or_id, str(e)))

    def validate_node(self, uuid):
        try:
            ifaces = self.manager.submitTask(
                _tasks.MachineNodeValidate(node_uuid=uuid))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(str(e))

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

        :returns: Dictonary representing the current state of the machine
                  upon exit of the method.
        """
        try:
            machine = self.manager.submitTask(
                _tasks.MachineSetProvision(node_uuid=name_or_id,
                                           state=state,
                                           configdrive=configdrive))

            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for node transition to "
                        "target state of '%s'" % state):
                    machine = self.get_machine(name_or_id)
                    if state in machine['provision_state']:
                        break
                    if ("available" in machine['provision_state'] and
                            "provide" in state):
                        break
            else:
                machine = self.get_machine(name_or_id)
            return machine

        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Baremetal machine node failed change provision"
                " state to {state}: {msg}".format(state=state,
                                                  msg=str(e)))

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
                result = self.manager.submitTask(
                    _tasks.MachineSetMaintenance(node_id=name_or_id,
                                                 state='true',
                                                 maint_reason=reason))
            else:
                result = self.manager.submitTask(
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
            power = self.manager.submitTask(
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

    def activate_node(self, uuid, configdrive=None):
        self.node_set_provision_state(uuid, 'active', configdrive)

    def deactivate_node(self, uuid):
        self.node_set_provision_state(uuid, 'deleted')

    def set_node_instance_info(self, uuid, patch):
        with _utils.shade_exceptions():
            return self.manager.submitTask(
                _tasks.MachineNodeUpdate(node_id=uuid, patch=patch))

    def purge_node_instance_info(self, uuid):
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        try:
            return self.manager.submitTask(
                _tasks.MachineNodeUpdate(node_id=uuid, patch=patch))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(str(e))

    @_utils.valid_kwargs('type', 'service_type', 'description')
    def create_service(self, name, **kwargs):
        """Create a service.

        :param name: Service name.
        :param type: Service type. (type or service_type required.)
        :param service_type: Service type. (type or service_type required.)
        :param description: Service description (optional).

        :returns: a dict containing the services description, i.e. the
            following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - service_type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.

        """
        service_type = kwargs.get('type', kwargs.get('service_type'))
        description = kwargs.get('description', None)
        try:
            if self.cloud_config.get_api_version('identity').startswith('2'):
                service_kwargs = {'service_type': service_type}
            else:
                service_kwargs = {'type': service_type}

            service = self.manager.submitTask(_tasks.ServiceCreate(
                name=name, description=description, **service_kwargs))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create service {name}: {msg}".format(
                    name=name, msg=str(e)))
        return service

    def list_services(self):
        """List all Keystone services.

        :returns: a list of dict containing the services description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        try:
            services = self.manager.submitTask(_tasks.ServiceList())
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(str(e))
        return _utils.normalize_keystone_services(services)

    def search_services(self, name_or_id=None, filters=None):
        """Search Keystone services.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                        {'type': 'network'}.

        :returns: a list of dict containing the services description.

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

        :returns: a dict containing the services description, i.e. the
            following attributes::
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
            self.log.debug("Service %s not found for deleting" % name_or_id)
            return False

        if self.cloud_config.get_api_version('identity').startswith('2'):
            service_kwargs = {'id': service['id']}
        else:
            service_kwargs = {'service': service['id']}
        try:
            self.manager.submitTask(_tasks.ServiceDelete(**service_kwargs))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to delete service {id}: {msg}".format(
                    id=service['id'],
                    msg=str(e)))
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

        :returns: a list of dicts containing the endpoint description.

        :raises: OpenStackCloudException if the service cannot be found or if
            something goes wrong during the openstack API call.
        """
        if url and kwargs:
            raise OpenStackCloudException(
                "create_endpoint takes either url and interace OR"
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
                urlkwargs['%url' % interface] = url
                urlkwargs['service_id'] = service['id']
            else:
                urlkwargs['url'] = url
                urlkwargs['interface'] = interface
                urlkwargs['enabled'] = enabled
                urlkwargs['service'] = service['id']
            endpoint_args.append(urlkwargs)
        else:
            if self.cloud_config.get_api_version(
                    'identity').startswith('2'):
                urlkwargs = {}
                for arg_key, arg_val in kwargs.items():
                    urlkwargs[arg_key.replace('_', '')] = arg_val
                urlkwargs['service_id'] = service['id']
                endpoint_args.append(urlkwargs)
            else:
                for arg_key, arg_val in kwargs.items():
                    urlkwargs = {}
                    urlkwargs['url'] = arg_val
                    urlkwargs['interface'] = arg_key.split('_')[0]
                    urlkwargs['enabled'] = enabled
                    urlkwargs['service'] = service['id']
                    endpoint_args.append(urlkwargs)

        for args in endpoint_args:
            try:
                endpoint = self.manager.submitTask(_tasks.EndpointCreate(
                    region=region,
                    **args
                ))
            except OpenStackCloudException:
                raise
            except Exception as e:
                raise OpenStackCloudException(
                    "Failed to create endpoint for service {service}: "
                    "{msg}".format(service=service['name'],
                                   msg=str(e)))
            endpoints.append(endpoint)
        return endpoints

    def list_endpoints(self):
        """List Keystone endpoints.

        :returns: a list of dict containing the endpoint description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        # ToDo: support v3 api (dguerri)
        try:
            endpoints = self.manager.submitTask(_tasks.EndpointList())
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException("Failed to list endpoints: {msg}"
                                          .format(msg=str(e)))
        return endpoints

    def search_endpoints(self, id=None, filters=None):
        """List Keystone endpoints.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a list of dict containing the endpoint description. Each dict
            contains the following attributes::
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

        :returns: a dict containing the endpoint description. i.e. a dict
            containing the following attributes::
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
        # ToDo: support v3 api (dguerri)
        endpoint = self.get_endpoint(id=id)
        if endpoint is None:
            self.log.debug("Endpoint %s not found for deleting" % id)
            return False

        if self.cloud_config.get_api_version('identity').startswith('2'):
            endpoint_kwargs = {'id': endpoint['id']}
        else:
            endpoint_kwargs = {'endpoint': endpoint['id']}
        try:
            self.manager.submitTask(_tasks.EndpointDelete(**endpoint_kwargs))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to delete endpoint {id}: {msg}".format(
                    id=id,
                    msg=str(e)))
        return True

    def create_domain(
            self, name, description=None, enabled=True):
        """Create a Keystone domain.

        :param name: The name of the domain.
        :param description: A description of the domain.
        :param enabled: Is the domain enabled or not (default True).

        :returns: a dict containing the domain description

        :raise OpenStackCloudException: if the domain cannot be created
        """
        try:
            domain = self.manager.submitTask(_tasks.DomainCreate(
                name=name,
                description=description,
                enabled=enabled))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create domain {name}".format(name=name,
                                                        msg=str(e)))
        return _utils.normalize_domains([domain])[0]

    def update_domain(
            self, domain_id, name=None, description=None, enabled=None):
        try:
            domain = self.manager.submitTask(_tasks.DomainUpdate(
                domain=domain_id, description=description, enabled=enabled))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error in updating domain {domain}: {message}".format(
                    domain=domain_id, message=str(e)))
        return _utils.normalize_domains([domain])[0]

    def delete_domain(self, domain_id):
        """Delete a Keystone domain.

        :param domain_id: ID of the domain to delete.

        :returns: None

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        try:
            # Deleting a domain is expensive, so disabling it first increases
            # the changes of success
            domain = self.update_domain(domain_id, enabled=False)
            self.manager.submitTask(_tasks.DomainDelete(
                domain=domain['id']))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to delete domain {id}: {msg}".format(id=domain_id,
                                                             msg=str(e)))

    def list_domains(self):
        """List Keystone domains.

        :returns: a list of dicts containing the domain description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            domains = self.manager.submitTask(_tasks.DomainList())
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException("Failed to list domains: {msg}"
                                          .format(msg=str(e)))
        return _utils.normalize_domains(domains)

    def search_domains(self, filters=None):
        """Search Keystone domains.

        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a list of dicts containing the domain description. Each dict
            contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            domains = self.manager.submitTask(
                _tasks.DomainList(**filters))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException("Failed to list domains: {msg}"
                                          .format(msg=str(e)))
        return _utils.normalize_domains(domains)

    def get_domain(self, domain_id):
        """Get exactly one Keystone domain.

        :param domain_id: domain id.

        :returns: a dict containing the domain description, or None if not
            found. Each dict contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            domain = self.manager.submitTask(
                _tasks.DomainGet(domain=domain_id))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to get domain {domain_id}: {msg}".format(
                    domain_id=domain_id,
                    msg=str(e)))
            raise OpenStackCloudException(str(e))
        return _utils.normalize_domains([domain])[0]

    def list_roles(self):
        """List Keystone roles.

        :returns: a list of dicts containing the role description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            roles = self.manager.submitTask(_tasks.RoleList())
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(str(e))
        return roles

    def search_roles(self, name_or_id=None, filters=None):
        """Seach Keystone roles.

        :param string name: role name or id.
        :param dict filters: a dict containing additional filters to use.

        :returns: a list of dict containing the role description. Each dict
            contains the following attributes::

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

        :returns: a single dict containing the role description. Each dict
            contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        return _utils._get_entity(self.search_roles, name_or_id, filters)

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

        :returns: A dict describing the new flavor.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            flavor = self.manager.submitTask(
                _tasks.FlavorCreate(name=name, ram=ram, vcpus=vcpus, disk=disk,
                                    flavorid=flavorid, ephemeral=ephemeral,
                                    swap=swap, rxtx_factor=rxtx_factor,
                                    is_public=is_public)
            )
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create flavor {name}: {msg}".format(
                    name=name,
                    msg=str(e)))
        return flavor

    def delete_flavor(self, name_or_id):
        """Delete a flavor

        :param name_or_id: ID or name of the flavor to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        flavor = self.get_flavor(name_or_id)
        if flavor is None:
            self.log.debug(
                "Flavor {0} not found for deleting".format(name_or_id))
            return False

        try:
            self.manager.submitTask(_tasks.FlavorDelete(flavor=flavor['id']))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to delete flavor {0}: {1}".format(name_or_id, e)
            )

        return True

    def _mod_flavor_specs(self, action, flavor_id, specs):
        """Common method for modifying flavor extra specs.

        Nova (very sadly) doesn't expose this with a public API, so we
        must get the actual flavor object and make a method call on it.

        Two separate try-except blocks are used because Nova can raise
        a NotFound exception if FlavorGet() is given an invalid flavor ID,
        or if the unset_keys() method of the flavor object is given an
        invalid spec key. We need to be able to differentiate between these
        actions, thus the separate blocks.
        """
        try:
            flavor = self.manager.submitTask(
                _tasks.FlavorGet(flavor=flavor_id)
            )
        except nova_exceptions.NotFound:
            self.log.debug(
                "Flavor ID {0} not found. "
                "Cannot {1} extra specs.".format(flavor_id, action)
            )
            raise OpenStackCloudResourceNotFound(
                "Flavor ID {0} not found".format(flavor_id)
            )
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error getting flavor ID {0}: {1}".format(flavor_id, e)
            )

        try:
            if action == 'set':
                flavor.set_keys(specs)
            elif action == 'unset':
                flavor.unset_keys(specs)
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to {0} flavor specs: {1}".format(action, e)
            )

    def set_flavor_specs(self, flavor_id, extra_specs):
        """Add extra specs to a flavor

        :param string flavor_id: ID of the flavor to update.
        :param dict extra_specs: Dictionary of key-value pairs.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        self._mod_flavor_specs('set', flavor_id, extra_specs)

    def unset_flavor_specs(self, flavor_id, keys):
        """Delete extra specs from a flavor

        :param string flavor_id: ID of the flavor to update.
        :param list keys: List of spec keys to delete.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        self._mod_flavor_specs('unset', flavor_id, keys)

    def _mod_flavor_access(self, action, flavor_id, project_id):
        """Common method for adding and removing flavor access
        """
        try:
            if action == 'add':
                self.manager.submitTask(
                    _tasks.FlavorAddAccess(flavor=flavor_id,
                                           tenant=project_id)
                )
            elif action == 'remove':
                self.manager.submitTask(
                    _tasks.FlavorRemoveAccess(flavor=flavor_id,
                                              tenant=project_id)
                )
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error trying to {0} access from flavor ID {1}: {2}".format(
                    action, flavor_id, e)
            )

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

    def create_role(self, name):
        """Create a Keystone role.

        :param string name: The name of the role.

        :returns: a dict containing the role description

        :raise OpenStackCloudException: if the role cannot be created
        """
        try:
            role = self.manager.submitTask(
                _tasks.RoleCreate(name=name)
            )
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(str(e))
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
                "Role {0} not found for deleting".format(name_or_id))
            return False

        try:
            self.manager.submitTask(_tasks.RoleDelete(role=role['id']))
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to delete role {0}: {1}".format(name_or_id, e)
            )

        return True

    def list_hypervisors(self):
        """List all hypervisors

        :returns: A list of hypervisor dicts.
        """

        try:
            return self.manager.submitTask(_tasks.HypervisorList())
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching hypervisor list: %s" % str(e))
