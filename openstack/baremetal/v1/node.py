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

import collections
import enum

from openstack.baremetal.v1 import _common
from openstack import exceptions
from openstack import resource
from openstack import utils


class ValidationResult:
    """Result of a single interface validation.

    :ivar result: Result of a validation, ``True`` for success, ``False`` for
        failure, ``None`` for unsupported interface.
    :ivar reason: If ``result`` is ``False`` or ``None``, explanation of
        the result.
    """

    def __init__(self, result, reason):
        self.result = result
        self.reason = reason


class PowerAction(enum.Enum):
    """Mapping from an action to a target power state."""

    POWER_ON = 'power on'
    """Power on the node."""

    POWER_OFF = 'power off'
    """Power off the node (using hard power off)."""
    REBOOT = 'rebooting'
    """Reboot the node (using hard power off)."""

    SOFT_POWER_OFF = 'soft power off'
    """Power off the node using soft power off."""

    SOFT_REBOOT = 'soft rebooting'
    """Reboot the node using soft power off."""


class WaitResult(collections.namedtuple('WaitResult',
                                        ['success', 'failure', 'timeout'])):
    """A named tuple representing a result of waiting for several nodes.

    Each component is a list of :class:`~openstack.baremetal.v1.node.Node`
    objects:

    :ivar ~.success: a list of :class:`~openstack.baremetal.v1.node.Node`
        objects that reached the state.
    :ivar ~.timeout: a list of :class:`~openstack.baremetal.v1.node.Node`
        objects that reached timeout.
    :ivar ~.failure: a list of :class:`~openstack.baremetal.v1.node.Node`
        objects that hit a failure.
    """
    __slots__ = ()


class Node(_common.ListMixin, resource.Resource):

    resources_key = 'nodes'
    base_path = '/nodes'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'associated', 'conductor_group', 'driver', 'fault',
        'provision_state', 'resource_class',
        fields={'type': _common.fields_type},
        instance_id='instance_uuid',
        is_maintenance='maintenance',
    )

    # The retired and retired_reason fields introduced in 1.61 (Ussuri).
    _max_microversion = '1.61'

    # Properties
    #: The UUID of the allocation associated with this node. Added in API
    #: microversion 1.52.
    allocation_id = resource.Body("allocation_uuid")
    #: A string or UUID of the tenant who owns the baremetal node. Added in API
    #: microversion 1.50.
    owner = resource.Body("owner")
    #: The UUID of the chassis associated wit this node. Can be empty or None.
    chassis_id = resource.Body("chassis_uuid")
    #: The current clean step.
    clean_step = resource.Body("clean_step")
    #: Hostname of the conductor currently handling this ndoe. Added in API
    # microversion 1.49.
    conductor = resource.Body("conductor")
    #: Conductor group this node is managed by. Added in API microversion 1.46.
    conductor_group = resource.Body("conductor_group")
    #: Timestamp at which the node was last updated.
    created_at = resource.Body("created_at")
    #: The current deploy step. Added in API microversion 1.44.
    deploy_step = resource.Body("deploy_step")
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
    #: Fault type that caused the node to enter maintenance mode.
    #: Introduced in API microversion 1.42.
    fault = resource.Body("fault")
    #: The UUID of the node resource.
    id = resource.Body("uuid", alternate_id=True)
    #: Information used to customize the deployed image, e.g. size of root
    #: partition, config drive in the form of base64 encoded string and other
    #: metadata.
    instance_info = resource.Body("instance_info")
    #: UUID of the nova instance associated with this node.
    instance_id = resource.Body("instance_uuid")
    #: Override enabling of automated cleaning. Added in API microversion 1.47.
    is_automated_clean_enabled = resource.Body("automated_clean", type=bool)
    #: Whether console access is enabled on this node.
    is_console_enabled = resource.Body("console_enabled", type=bool)
    #: Whether node is currently in "maintenance mode". Nodes put into
    #: maintenance mode are removed from the available resource pool.
    is_maintenance = resource.Body("maintenance", type=bool)
    # Whether the node is protected from undeploying. Added in API microversion
    # 1.48.
    is_protected = resource.Body("protected", type=bool)
    #: Whether the node is marked for retirement. Added in API microversion
    #: 1.61.
    is_retired = resource.Body("retired", type=bool)
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
    # The reason why this node is protected. Added in API microversion 1.48.
    protected_reason = resource.Body("protected_reason")
    #: The current provisioning state of the node.
    provision_state = resource.Body("provision_state")
    #: The reason why the node is marked for retirement. Added in API
    #: microversion 1.61.
    retired_reason = resource.Body("retired_reason")
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
    #: Traits of the node. Introduced in API microversion 1.37.
    traits = resource.Body("traits", type=list)
    #: Timestamp at which the node was last updated.
    updated_at = resource.Body("updated_at")

    # Hardware interfaces grouped together for convenience.

    #: BIOS interface to use when setting BIOS properties of the node.
    #: Introduced in API microversion 1.40.
    bios_interface = resource.Body("bios_interface")
    #: Boot interface to use when configuring boot of the node.
    #: Introduced in API microversion 1.31.
    boot_interface = resource.Body("boot_interface")
    #: Console interface to use when working with serial console.
    #: Introduced in API microversion 1.31.
    console_interface = resource.Body("console_interface")
    #: Deploy interface to use when deploying the node.
    #: Introduced in API microversion 1.31.
    deploy_interface = resource.Body("deploy_interface")
    #: Inspect interface to use when inspecting the node.
    #: Introduced in API microversion 1.31.
    inspect_interface = resource.Body("inspect_interface")
    #: Management interface to use for management actions on the node.
    #: Introduced in API microversion 1.31.
    management_interface = resource.Body("management_interface")
    #: Network interface provider to use when plumbing the network connections
    #: for this node. Introduced in API microversion 1.20.
    network_interface = resource.Body("network_interface")
    #: Power interface to use for power actions on the node.
    #: Introduced in API microversion 1.31.
    power_interface = resource.Body("power_interface")
    #: RAID interface to use for configuring RAID on the node.
    #: Introduced in API microversion 1.31.
    raid_interface = resource.Body("raid_interface")
    #: Rescue interface to use for rescuing of the node.
    #: Introduced in API microversion 1.38.
    rescue_interface = resource.Body("rescue_interface")
    #: Storage interface to use when attaching remote storage.
    #: Introduced in API microversion 1.33.
    storage_interface = resource.Body("storage_interface")
    #: Vendor interface to use for vendor-specific actions on the node.
    #: Introduced in API microversion 1.31.
    vendor_interface = resource.Body("vendor_interface")

    def _consume_body_attrs(self, attrs):
        if 'provision_state' in attrs and attrs['provision_state'] is None:
            # API version 1.1 uses None instead of "available". Make it
            # consistent.
            attrs['provision_state'] = 'available'
        return super(Node, self)._consume_body_attrs(attrs)

    def create(self, session, *args, **kwargs):
        """Create a remote resource based on this instance.

        The overridden version is capable of handling the populated
        ``provision_state`` field of one of three values: ``enroll``,
        ``manageable`` or ``available``. The default is currently
        ``available``, since it's the only state supported by all API versions.

        Note that Bare Metal API 1.4 is required for ``manageable`` and
        1.11 is required for ``enroll``.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :return: This :class:`Resource` instance.
        :raises: ValueError if the Node's ``provision_state`` is not one of
            ``None``, ``enroll``, ``manageable`` or ``available``.
        :raises: :exc:`~openstack.exceptions.NotSupported` if
            the ``provision_state`` cannot be reached with any API version
            supported by the server.
        """
        expected_provision_state = self.provision_state
        if expected_provision_state is None:
            expected_provision_state = 'available'

        if expected_provision_state not in ('enroll',
                                            'manageable',
                                            'available'):
            raise ValueError(
                "Node's provision_state must be one of 'enroll', "
                "'manageable' or 'available' for creation, got %s" %
                expected_provision_state)

        session = self._get_session(session)
        # Verify that the requested provision state is reachable with the API
        # version we are going to use.
        try:
            expected_version = _common.STATE_VERSIONS[expected_provision_state]
        except KeyError:
            pass
        else:
            self._assert_microversion_for(
                session, 'create', expected_version,
                error_message="Cannot create a node with initial provision "
                "state %s" % expected_provision_state)

        # Ironic cannot set provision_state itself, so marking it as unchanged
        self._clean_body_attrs({'provision_state'})
        super(Node, self).create(session, *args, **kwargs)

        if (self.provision_state == 'enroll'
                and expected_provision_state != 'enroll'):
            self.set_provision_state(session, 'manage', wait=True)

        if (self.provision_state == 'manageable'
                and expected_provision_state == 'available'):
            self.set_provision_state(session, 'provide', wait=True)

        if (self.provision_state == 'available'
                and expected_provision_state == 'manageable'):
            self.set_provision_state(session, 'manage', wait=True)

        return self

    def commit(self, session, *args, **kwargs):
        """Commit the state of the instance to the remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :return: This :class:`Node` instance.
        """
        # These fields have to be set through separate API.
        if ('maintenance_reason' in self._body.dirty
                or 'maintenance' in self._body.dirty):
            if not self.is_maintenance and self.maintenance_reason:
                if 'maintenance' in self._body.dirty:
                    self.maintenance_reason = None
                else:
                    raise ValueError('Maintenance reason cannot be set when '
                                     'maintenance is False')
            if self.is_maintenance:
                self._do_maintenance_action(
                    session, 'put', {'reason': self.maintenance_reason})
            else:
                # This corresponds to setting maintenance=False and
                # maintenance_reason=None in the same request.
                self._do_maintenance_action(session, 'delete')

            self._clean_body_attrs({'maintenance', 'maintenance_reason'})
            if not self.requires_commit:
                # Other fields are not updated, re-fetch the node to reflect
                # the new status.
                return self.fetch(session)

        return super(Node, self).commit(session, *args, **kwargs)

    def set_provision_state(self, session, target, config_drive=None,
                            clean_steps=None, rescue_password=None,
                            wait=False, timeout=None):
        """Run an action modifying this node's provision state.

        This call is asynchronous, it will return success as soon as the Bare
        Metal service acknowledges the request.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param target: Provisioning action, e.g. ``active``, ``provide``.
            See the Bare Metal service documentation for available actions.
        :param config_drive: Config drive to pass to the node, only valid
            for ``active` and ``rebuild`` targets. You can use functions from
            :mod:`openstack.baremetal.configdrive` to build it.
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
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the node
            reaches an error state while waiting for the state.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if timeout
            is reached while waiting for the state.
        """
        session = self._get_session(session)

        version = None
        if target in _common.PROVISIONING_VERSIONS:
            version = '1.%d' % _common.PROVISIONING_VERSIONS[target]

        if config_drive:
            # Some config drive actions require a higher version.
            if isinstance(config_drive, dict):
                version = _common.CONFIG_DRIVE_DICT_VERSION
            elif target == 'rebuild':
                version = _common.CONFIG_DRIVE_REBUILD_VERSION

        version = self._assert_microversion_for(session, 'commit', version)

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
            return self.fetch(session)

    def wait_for_power_state(self, session, expected_state, timeout=None):
        """Wait for the node to reach the expected power state.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param expected_state: The expected power state to reach.
        :param timeout: If ``wait`` is set to ``True``, specifies how much (in
            seconds) to wait for the expected state to be reached. The value of
            ``None`` (the default) means no client-side timeout.

        :return: This :class:`Node` instance.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` on timeout.
        """
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for node %(node)s to reach "
                "power state '%(state)s'" % {'node': self.id,
                                             'state': expected_state}):
            self.fetch(session)
            if self.power_state == expected_state:
                return self

            session.log.debug(
                'Still waiting for node %(node)s to reach power state '
                '"%(target)s", the current state is "%(state)s"',
                {'node': self.id, 'target': expected_state,
                 'state': self.power_state})

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
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the node
            reaches an error state and ``abort_on_failed_state`` is ``True``.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` on timeout.
        """
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for node %(node)s to reach "
                "target state '%(state)s'" % {'node': self.id,
                                              'state': expected_state}):
            self.fetch(session)
            if self._check_state_reached(session, expected_state,
                                         abort_on_failed_state):
                return self

            session.log.debug(
                'Still waiting for node %(node)s to reach state '
                '"%(target)s", the current state is "%(state)s"',
                {'node': self.id, 'target': expected_state,
                 'state': self.provision_state})

    def wait_for_reservation(self, session, timeout=None):
        """Wait for a lock on the node to be released.

        Bare metal nodes in ironic have a reservation lock that
        is used to represent that a conductor has locked the node
        while performing some sort of action, such as changing
        configuration as a result of a machine state change.

        This lock can occur during power syncronization, and prevents
        updates to objects attached to the node, such as ports.

        Note that nothing prevents a conductor from acquiring the lock again
        after this call returns, so it should be treated as best effort.

        Returns immediately if there is no reservation on the node.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param timeout: How much (in seconds) to wait for the lock to be
            released. The value of ``None`` (the default) means no timeout.

        :return: This :class:`Node` instance.
        """
        if self.reservation is None:
            return self

        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for the lock to be released on node %s" %
                self.id):
            self.fetch(session)
            if self.reservation is None:
                return self

            session.log.debug(
                'Still waiting for the lock to be released on node '
                '%(node)s, currently locked by conductor %(host)s',
                {'node': self.id, 'host': self.reservation})

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
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the node
            reaches an error state and ``abort_on_failed_state`` is ``True``.
        """
        # NOTE(dtantsur): microversion 1.2 changed None to available
        if (self.provision_state == expected_state
                or (expected_state == 'available'
                    and self.provision_state is None)):
            return True
        elif not abort_on_failed_state:
            return False

        if (self.provision_state.endswith(' failed')
                or self.provision_state == 'error'):
            raise exceptions.ResourceFailure(
                "Node %(node)s reached failure state \"%(state)s\"; "
                "the last error is %(error)s" %
                {'node': self.id, 'state': self.provision_state,
                 'error': self.last_error})
        # Special case: a failure state for "manage" transition can be
        # "enroll"
        elif (expected_state == 'manageable'
              and self.provision_state == 'enroll' and self.last_error):
            raise exceptions.ResourceFailure(
                "Node %(node)s could not reach state manageable: "
                "failed to verify management credentials; "
                "the last error is %(error)s" %
                {'node': self.id, 'error': self.last_error})

    def set_power_state(self, session, target, wait=False, timeout=None):
        """Run an action modifying this node's power state.

        This call is asynchronous, it will return success as soon as the Bare
        Metal service acknowledges the request.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param target: Target power state, as a :class:`PowerAction` or
            a string.
        :param wait: Whether to wait for the expected power state to be
            reached.
        :param timeout: Timeout (in seconds) to wait for the target state to be
            reached. If ``None``, wait without timeout.
        """
        if isinstance(target, PowerAction):
            target = target.value
        if wait:
            try:
                expected = _common.EXPECTED_POWER_STATES[target]
            except KeyError:
                raise ValueError("Cannot use target power state %s with wait, "
                                 "the expected state is not known" % target)

        session = self._get_session(session)

        if target.startswith("soft "):
            version = '1.27'
        else:
            version = None

        version = self._assert_microversion_for(session, 'commit', version)

        # TODO(dtantsur): server timeout support
        body = {'target': target}

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'states', 'power')
        response = session.put(
            request.url, json=body,
            headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        msg = ("Failed to set power state for bare metal node {node} "
               "to {target}".format(node=self.id, target=target))
        exceptions.raise_from_response(response, error_message=msg)

        if wait:
            self.wait_for_power_state(session, expected, timeout=timeout)

    def attach_vif(self, session, vif_id, retry_on_conflict=True):
        """Attach a VIF to the node.

        The exact form of the VIF ID depends on the network interface used by
        the node. In the most common case it is a Network service port
        (NOT a Bare Metal port) ID. A VIF can only be attached to one node
        at a time.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param string vif_id: Backend-specific VIF ID.
        :param retry_on_conflict: Whether to retry HTTP CONFLICT errors.
            This can happen when either the VIF is already used on a node or
            the node is locked. Since the latter happens more often, the
            default value is True.
        :return: ``None``
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VIF API.
        """
        session = self._get_session(session)
        version = self._assert_microversion_for(
            session, 'commit', _common.VIF_VERSION,
            error_message=("Cannot use VIF attachment API"))

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'vifs')
        body = {'id': vif_id}
        retriable_status_codes = _common.RETRIABLE_STATUS_CODES
        if not retry_on_conflict:
            retriable_status_codes = set(retriable_status_codes) - {409}
        response = session.post(
            request.url, json=body,
            headers=request.headers, microversion=version,
            retriable_status_codes=retriable_status_codes)

        msg = ("Failed to attach VIF {vif} to bare metal node {node}"
               .format(node=self.id, vif=vif_id))
        exceptions.raise_from_response(response, error_message=msg)

    def detach_vif(self, session, vif_id, ignore_missing=True):
        """Detach a VIF from the node.

        The exact form of the VIF ID depends on the network interface used by
        the node. In the most common case it is a Network service port
        (NOT a Bare Metal port) ID.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param string vif_id: Backend-specific VIF ID.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the VIF does not exist. Otherwise, ``False``
                    is returned.
        :return: ``True`` if the VIF was detached, otherwise ``False``.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VIF API.
        """
        session = self._get_session(session)
        version = self._assert_microversion_for(
            session, 'commit', _common.VIF_VERSION,
            error_message=("Cannot use VIF attachment API"))

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'vifs', vif_id)
        response = session.delete(
            request.url, headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        if ignore_missing and response.status_code == 400:
            session.log.debug(
                'VIF %(vif)s was already removed from node %(node)s',
                {'vif': vif_id, 'node': self.id})
            return False

        msg = ("Failed to detach VIF {vif} from bare metal node {node}"
               .format(node=self.id, vif=vif_id))
        exceptions.raise_from_response(response, error_message=msg)
        return True

    def list_vifs(self, session):
        """List IDs of VIFs attached to the node.

        The exact form of the VIF ID depends on the network interface used by
        the node. In the most common case it is a Network service port
        (NOT a Bare Metal port) ID.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :return: List of VIF IDs as strings.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VIF API.
        """
        session = self._get_session(session)
        version = self._assert_microversion_for(
            session, 'fetch', _common.VIF_VERSION,
            error_message=("Cannot use VIF attachment API"))

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'vifs')
        response = session.get(
            request.url, headers=request.headers, microversion=version)

        msg = ("Failed to list VIFs attached to bare metal node {node}"
               .format(node=self.id))
        exceptions.raise_from_response(response, error_message=msg)
        return [vif['id'] for vif in response.json()['vifs']]

    def validate(self, session, required=('boot', 'deploy', 'power')):
        """Validate required information on a node.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param required: List of interfaces that are required to pass
            validation. The default value is the list of minimum required
            interfaces for provisioning.

        :return: dict mapping interface names to :class:`ValidationResult`
            objects.
        :raises: :exc:`~openstack.exceptions.ValidationException` if validation
            fails for a required interface.
        """
        session = self._get_session(session)
        version = self._get_microversion_for(session, 'fetch')

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'validate')
        response = session.get(request.url, headers=request.headers,
                               microversion=version)

        msg = ("Failed to validate node {node}".format(node=self.id))
        exceptions.raise_from_response(response, error_message=msg)
        result = response.json()

        if required:
            failed = [
                '%s (%s)' % (key, value.get('reason', 'no reason'))
                for key, value in result.items()
                if key in required and not value.get('result')
            ]

            if failed:
                raise exceptions.ValidationException(
                    'Validation failed for required interfaces of node {node}:'
                    ' {failures}'.format(node=self.id,
                                         failures=', '.join(failed)))

        return {key: ValidationResult(value.get('result'), value.get('reason'))
                for key, value in result.items()}

    def set_maintenance(self, session, reason=None):
        """Enable maintenance mode on the node.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param reason: Optional reason for maintenance.
        :return: This :class:`Node` instance.
        """
        self._do_maintenance_action(session, 'put', {'reason': reason})
        return self.fetch(session)

    def unset_maintenance(self, session):
        """Disable maintenance mode on the node.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :return: This :class:`Node` instance.
        """
        self._do_maintenance_action(session, 'delete')
        return self.fetch(session)

    def _do_maintenance_action(self, session, verb, body=None):
        session = self._get_session(session)
        version = self._get_microversion_for(session, 'commit')
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'maintenance')
        response = getattr(session, verb)(
            request.url, json=body,
            headers=request.headers, microversion=version)
        msg = ("Failed to change maintenance mode for node {node}"
               .format(node=self.id))
        exceptions.raise_from_response(response, error_message=msg)

    def set_boot_device(self, session, boot_device, persistent=False):
        """Set node boot device

        :param session: The session to use for making this request.
        :param boot_device: Boot device to assign to the node.
        :param persistent: If the boot device change is maintained after node
            reboot
        :return: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        session = self._get_session(session)
        version = self._get_microversion_for(session, 'commit')
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'management', 'boot_device')

        body = {'boot_device': boot_device, 'persistent': persistent}

        response = session.put(
            request.url, json=body,
            headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        msg = ("Failed to set boot device for node {node}"
               .format(node=self.id))
        exceptions.raise_from_response(response, error_message=msg)

    def add_trait(self, session, trait):
        """Add a trait to a node.

        :param session: The session to use for making this request.
        :param trait: The trait to add to the node.
        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        session = self._get_session(session)
        version = utils.pick_microversion(session, '1.37')
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'traits', trait)
        response = session.put(
            request.url, json=None,
            headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        msg = ("Failed to add trait {trait} for node {node}"
               .format(trait=trait, node=self.id))
        exceptions.raise_from_response(response, error_message=msg)

        self.traits = list(set(self.traits or ()) | {trait})

    def remove_trait(self, session, trait, ignore_missing=True):
        """Remove a trait from a node.

        :param session: The session to use for making this request.
        :param trait: The trait to remove from the node.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the trait does not exist.
            Otherwise, ``False`` is returned.
        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        session = self._get_session(session)
        version = utils.pick_microversion(session, '1.37')
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'traits', trait)

        response = session.delete(
            request.url, headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        if ignore_missing or response.status_code == 400:
            session.log.debug(
                'Trait %(trait)s was already removed from node %(node)s',
                {'trait': trait, 'node': self.id})
            return False

        msg = ("Failed to remove trait {trait} from bare metal node {node}"
               .format(node=self.id, trait=trait))
        exceptions.raise_from_response(response, error_message=msg)

        self.traits = list(set(self.traits) - {trait})

        return True

    def set_traits(self, session, traits):
        """Set traits for a node.

        Removes any existing traits and adds the traits passed in to this
        method.

        :param session: The session to use for making this request.
        :param traits: list of traits to add to the node.
        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        session = self._get_session(session)
        version = utils.pick_microversion(session, '1.37')
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'traits')

        body = {'traits': traits}

        response = session.put(
            request.url, json=body,
            headers=request.headers, microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES)

        msg = ("Failed to set traits for node {node}"
               .format(node=self.id))
        exceptions.raise_from_response(response, error_message=msg)

        self.traits = traits

    def patch(self, session, patch=None, prepend_key=True, has_body=True,
              retry_on_conflict=None, base_path=None, reset_interfaces=None):

        if reset_interfaces is not None:
            # The id cannot be dirty for an commit
            self._body._dirty.discard("id")

            # Only try to update if we actually have anything to commit.
            if not patch and not self.requires_commit:
                return self

            if not self.allow_patch:
                raise exceptions.MethodNotSupported(self, "patch")

            session = self._get_session(session)
            microversion = self._assert_microversion_for(
                session, 'commit', _common.RESET_INTERFACES_VERSION)
            params = [('reset_interfaces', reset_interfaces)]

            request = self._prepare_request(requires_id=True,
                                            prepend_key=prepend_key,
                                            base_path=base_path, patch=True,
                                            params=params)

            if patch:
                request.body += self._convert_patch(patch)

            return self._commit(session, request, 'PATCH', microversion,
                                has_body=has_body,
                                retry_on_conflict=retry_on_conflict)

        else:
            return super(Node, self).patch(session, patch=patch,
                                           retry_on_conflict=retry_on_conflict)


NodeDetail = Node
