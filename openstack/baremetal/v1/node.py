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

from openstack import _log
from openstack.baremetal import baremetal_service
from openstack.baremetal.v1 import _common
from openstack import exceptions
from openstack import resource
from openstack import utils


_logger = _log.setup_logging('openstack')


class Node(resource.Resource):

    resources_key = 'nodes'
    base_path = '/nodes'
    service = baremetal_service.BaremetalService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    update_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'associated', 'driver', 'fields', 'provision_state', 'resource_class',
        instance_id='instance_uuid',
        is_maintenance='maintenance',
    )

    # Properties
    #: The UUID of the chassis associated wit this node. Can be empty or None.
    chassis_id = resource.Body("chassis_uuid")
    #: The current clean step.
    clean_step = resource.Body("clean_step")
    #: Timestamp at which the node was last updated.
    created_at = resource.Body("created_at")
    #: The name of the driver.
    driver = resource.Body("driver")
    #: All the metadata required by the driver to manage this node. List of
    #: fields varies between drivers, and can be retrieved from the
    #: :class:`openstack.baremetal.v1.driver.Driver` resource.
    driver_info = resource.Body("driver_info", type=dict)
    #: Internal metadata set and stored by node's driver. This is read-only.
    driver_internal_info = resource.Body("driver_internal_info", type=dict)
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body("extra")
    #: The UUID of the node resource.
    id = resource.Body("uuid", alternate_id=True)
    #: Information used to customize the deployed image, e.g. size of root
    #: partition, config drive in the form of base64 encoded string and other
    #: metadata.
    instance_info = resource.Body("instance_info")
    #: UUID of the nova instance associated with this node.
    instance_id = resource.Body("instance_uuid")
    #: Whether console access is enabled on this node.
    is_console_enabled = resource.Body("console_enabled", type=bool)
    #: Whether node is currently in "maintenance mode". Nodes put into
    #: maintenance mode are removed from the available resource pool.
    is_maintenance = resource.Body("maintenance", type=bool)
    #: Any error from the most recent transaction that started but failed to
    #: finish.
    last_error = resource.Body("last_error")
    #: A list of relative links, including self and bookmark links.
    links = resource.Body("links", type=list)
    #: user settable description of the reason why the node was placed into
    #: maintenance mode.
    maintenance_reason = resource.Body("maintenance_reason")
    #: Human readable identifier for the node. May be undefined. Certain words
    #: are reserved. Added in API microversion 1.5
    name = resource.Body("name")
    #: Network interface provider to use when plumbing the network connections
    #: for this node. Introduced in API microversion 1.20.
    network_interface = resource.Body("network_interface")
    #: Links to the collection of ports on this node.
    ports = resource.Body("ports", type=list)
    #: Links to the collection of portgroups on this node. Available since
    #: API microversion 1.24.
    port_groups = resource.Body("portgroups", type=list)
    #: The current power state. Usually "power on" or "power off", but may be
    #: "None" if service is unable to determine the power state.
    power_state = resource.Body("power_state")
    #: Physical characteristics of the node. Content populated by the service
    #: during inspection.
    properties = resource.Body("properties", type=dict)
    #: The current provisioning state of the node.
    provision_state = resource.Body("provision_state")
    #: The current RAID configuration of the node.
    raid_config = resource.Body("raid_config")
    #: The name of an service conductor host which is holding a lock on this
    #: node, if a lock is held.
    reservation = resource.Body("reservation")
    #: A string to be used by external schedulers to identify this node as a
    #: unit of a specific type of resource. Added in API microversion 1.21.
    resource_class = resource.Body("resource_class")
    #: Links to the collection of states.
    states = resource.Body("states", type=list)
    #: The requested state if a provisioning action has been requested. For
    #: example, ``AVAILABLE``, ``DEPLOYING``, ``DEPLOYWAIT``, ``DEPLOYING``,
    #: ``ACTIVE`` etc.
    target_provision_state = resource.Body("target_provision_state")
    #: The requested state during a state transition.
    target_power_state = resource.Body("target_power_state")
    #: The requested RAID configuration of the node which will be applied when
    #: the node next transitions through the CLEANING state.
    target_raid_config = resource.Body("target_raid_config")
    #: Timestamp at which the node was last updated.
    updated_at = resource.Body("updated_at")

    def set_provision_state(self, session, target, config_drive=None,
                            clean_steps=None, rescue_password=None,
                            wait=False, timeout=True):
        """Run an action modifying this node's provision state.

        This call is asynchronous, it will return success as soon as the Bare
        Metal service acknowledges the request.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param target: Provisioning action, e.g. ``active``, ``provide``.
            See the Bare Metal service documentation for available actions.
        :param config_drive: Config drive to pass to the node, only valid
            for ``active` and ``rebuild`` targets.
        :param clean_steps: Clean steps to execute, only valid for ``clean``
            target.
        :param rescue_password: Password for the rescue operation, only valid
            for ``rescue`` target.
        :param wait: Whether to wait for the target state to be reached.
        :param timeout: Timeout (in seconds) to wait for the target state to be
            reached. If ``None``, wait without timeout.

        :return: This :class:`Node` instance.
        :raises: ValueError if ``config_drive``, ``clean_steps`` or
            ``rescue_password`` are provided with an invalid ``target``.
        """
        session = self._get_session(session)

        if target in _common.PROVISIONING_VERSIONS:
            version = '1.%d' % _common.PROVISIONING_VERSIONS[target]
        else:
            if config_drive and target == 'rebuild':
                version = '1.35'
            else:
                version = None
        version = utils.pick_microversion(session, version)

        body = {'target': target}
        if config_drive:
            if target not in ('active', 'rebuild'):
                raise ValueError('Config drive can only be provided with '
                                 '"active" and "rebuild" targets')
            # Not a typo - ironic accepts "configdrive" (without underscore)
            body['configdrive'] = config_drive

        if clean_steps is not None:
            if target != 'clean':
                raise ValueError('Clean steps can only be provided with '
                                 '"clean" target')
            body['clean_steps'] = clean_steps

        if rescue_password is not None:
            if target != 'rescue':
                raise ValueError('Rescue password can only be provided with '
                                 '"rescue" target')
            body['rescue_password'] = rescue_password

        if wait:
            try:
                expected_state = _common.EXPECTED_STATES[target]
            except KeyError:
                raise ValueError('For target %s the expected state is not '
                                 'known, cannot wait for it' % target)

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'states', 'provision')
        response = session.put(
            request.url, json=body,
            headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        msg = ("Failed to set provision state for bare metal node {node} "
               "to {target}".format(node=self.id, target=target))
        exceptions.raise_from_response(response, error_message=msg)

        if wait:
            return self.wait_for_provision_state(session,
                                                 expected_state,
                                                 timeout=timeout)
        else:
            return self.get(session)

    def wait_for_provision_state(self, session, expected_state, timeout=None,
                                 abort_on_failed_state=True):
        """Wait for the node to reach the expected state.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param expected_state: The expected provisioning state to reach.
        :param timeout: If ``wait`` is set to ``True``, specifies how much (in
            seconds) to wait for the expected state to be reached. The value of
            ``None`` (the default) means no client-side timeout.
        :param abort_on_failed_state: If ``True`` (the default), abort waiting
            if the node reaches a failure state which does not match the
            expected one. Note that the failure state for ``enroll`` ->
            ``manageable`` transition is ``enroll`` again.

        :return: This :class:`Node` instance.
        """
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for node %(node)s to reach "
                "target state '%(state)s'" % {'node': self.id,
                                              'state': expected_state}):
            self.get(session)
            if self._check_state_reached(session, expected_state,
                                         abort_on_failed_state):
                return self

            _logger.debug('Still waiting for node %(node)s to reach state '
                          '"%(target)s", the current state is "%(state)s"',
                          {'node': self.id, 'target': expected_state,
                           'state': self.provision_state})

    def _check_state_reached(self, session, expected_state,
                             abort_on_failed_state=True):
        """Wait for the node to reach the expected state.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param expected_state: The expected provisioning state to reach.
        :param abort_on_failed_state: If ``True`` (the default), abort waiting
            if the node reaches a failure state which does not match the
            expected one. Note that the failure state for ``enroll`` ->
            ``manageable`` transition is ``enroll`` again.

        :return: ``True`` if the target state is reached
        :raises: SDKException if ``abort_on_failed_state`` is ``True`` and
            a failure state is reached.
        """
        # NOTE(dtantsur): microversion 1.2 changed None to available
        if (self.provision_state == expected_state or
                (expected_state == 'available' and
                 self.provision_state is None)):
            return True
        elif not abort_on_failed_state:
            return False

        if self.provision_state.endswith(' failed'):
            raise exceptions.SDKException(
                "Node %(node)s reached failure state \"%(state)s\"; "
                "the last error is %(error)s" %
                {'node': self.id, 'state': self.provision_state,
                 'error': self.last_error})
        # Special case: a failure state for "manage" transition can be
        # "enroll"
        elif (expected_state == 'manageable' and
              self.provision_state == 'enroll' and self.last_error):
            raise exceptions.SDKException(
                "Node %(node)s could not reach state manageable: "
                "failed to verify management credentials; "
                "the last error is %(error)s" %
                {'node': self.id, 'error': self.last_error})


class NodeDetail(Node):

    base_path = '/nodes/detail'

    # capabilities
    allow_create = False
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'associated', 'driver', 'fields', 'provision_state', 'resource_class',
        instance_id='instance_uuid',
        is_maintenance='maintenance',
    )

    #: The UUID of the node resource.
    id = resource.Body("uuid", alternate_id=True)
