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

import typing as ty

import requests

from openstack.baremetal.v1 import _common
from openstack.baremetal.v1 import allocation as _allocation
from openstack.baremetal.v1 import chassis as _chassis
from openstack.baremetal.v1 import conductor as _conductor
from openstack.baremetal.v1 import deploy_templates as _deploytemplates
from openstack.baremetal.v1 import driver as _driver
from openstack.baremetal.v1 import node as _node
from openstack.baremetal.v1 import port as _port
from openstack.baremetal.v1 import port_group as _portgroup
from openstack.baremetal.v1 import volume_connector as _volumeconnector
from openstack.baremetal.v1 import volume_target as _volumetarget
from openstack import exceptions
from openstack import proxy
from openstack import resource
from openstack import utils


class Proxy(proxy.Proxy):
    retriable_status_codes = _common.RETRIABLE_STATUS_CODES

    _resource_registry = {
        "allocation": _allocation.Allocation,
        "chassis": _chassis.Chassis,
        "conductor": _conductor.Conductor,
        "deploy_template": _deploytemplates.DeployTemplate,
        "driver": _driver.Driver,
        "node": _node.Node,
        "port": _port.Port,
        "port_group": _portgroup.PortGroup,
        "volume_connector": _volumeconnector.VolumeConnector,
        "volume_target": _volumetarget.VolumeTarget,
    }

    def _get_with_fields(self, resource_type, value, fields=None):
        """Fetch a bare metal resource.

        :param resource_type: The type of resource to get.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value to get. Can be either the ID of a
            resource or a :class:`~openstack.resource.Resource`
            subclass.
        :param fields: Limit the resource fields to fetch.

        :returns: The result of the ``fetch``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value)
        kwargs = {}
        if fields:
            kwargs['fields'] = _common.fields_type(fields, resource_type)
        return res.fetch(
            self,
            error_message=f"No {resource_type.__name__} found for {value}",
            **kwargs,
        )

    # ========== Chassis ==========

    def chassis(self, details=False, **query):
        """Retrieve a generator of chassis.

        :param details: A boolean indicating whether the detailed information
            for every chassis should be returned.
        :param dict query: Optional query parameters to be sent to
            restrict the chassis to be returned. Available parameters include:

            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of items be
              returned from the query.
            * ``marker``: Specifies the ID of the last-seen chassis. Use the
              ``limit`` parameter to make an initial limited request and
              use the ID of the last-seen chassis from the response as
              the ``marker`` value in a subsequent limited request.
            * ``sort_dir``: Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query parameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of chassis instances.
        """
        return _chassis.Chassis.list(self, details=details, **query)

    def create_chassis(self, **attrs):
        """Create a new chassis from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.chassis.Chassis`.

        :returns: The results of chassis creation.
        :rtype: :class:`~openstack.baremetal.v1.chassis.Chassis`.
        """
        return self._create(_chassis.Chassis, **attrs)

    # TODO(stephenfin): Delete this. You can't lookup a chassis by name so this
    # is identical to get_chassis
    def find_chassis(self, name_or_id, ignore_missing=True, *, details=True):
        """Find a single chassis.

        :param str name_or_id: The ID of a chassis.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the chassis does not exist.  When set to `True``, None will
            be returned when attempting to find a nonexistent chassis.
        :param details: A boolean indicating whether the detailed information
            for the chassis should be returned.

        :returns: One :class:`~openstack.baremetal.v1.chassis.Chassis` object
            or None.
        """
        return self._find(
            _chassis.Chassis,
            name_or_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def get_chassis(self, chassis, fields=None):
        """Get a specific chassis.

        :param chassis: The value can be the ID of a chassis or a
            :class:`~openstack.baremetal.v1.chassis.Chassis` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~openstack.baremetal.v1.chassis.Chassis`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            chassis matching the name or ID could be found.
        """
        return self._get_with_fields(_chassis.Chassis, chassis, fields=fields)

    def update_chassis(self, chassis, **attrs):
        """Update a chassis.

        :param chassis: Either the ID of a chassis, or an instance
            of :class:`~openstack.baremetal.v1.chassis.Chassis`.
        :param dict attrs: The attributes to update on the chassis represented
            by the ``chassis`` parameter.

        :returns: The updated chassis.
        :rtype: :class:`~openstack.baremetal.v1.chassis.Chassis`
        """
        return self._update(_chassis.Chassis, chassis, **attrs)

    def patch_chassis(self, chassis, patch):
        """Apply a JSON patch to the chassis.

        :param chassis: The value can be the ID of a chassis or a
            :class:`~openstack.baremetal.v1.chassis.Chassis` instance.
        :param patch: JSON patch to apply.

        :returns: The updated chassis.
        :rtype: :class:`~openstack.baremetal.v1.chassis.Chassis`
        """
        return self._get_resource(_chassis.Chassis, chassis).patch(self, patch)

    def delete_chassis(self, chassis, ignore_missing=True):
        """Delete a chassis.

        :param chassis: The value can be either the ID of a chassis or
            a :class:`~openstack.baremetal.v1.chassis.Chassis` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the chassis could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            chassis.

        :returns: The instance of the chassis which was deleted.
        :rtype: :class:`~openstack.baremetal.v1.chassis.Chassis`.
        """
        return self._delete(
            _chassis.Chassis, chassis, ignore_missing=ignore_missing
        )

    # ========== Drivers ==========

    def drivers(self, details=False, **query):
        """Retrieve a generator of drivers.

        :param bool details: A boolean indicating whether the detailed
            information for every driver should be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of driver instances.
        """
        # NOTE(dtantsur): details are available starting with API microversion
        # 1.30. Thus we do not send any value if not needed.
        if details:
            query['details'] = True
        return self._list(_driver.Driver, **query)

    def get_driver(self, driver):
        """Get a specific driver.

        :param driver: The value can be the name of a driver or a
            :class:`~openstack.baremetal.v1.driver.Driver` instance.

        :returns: One :class:`~openstack.baremetal.v1.driver.Driver`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            driver matching the name could be found.
        """
        return self._get(_driver.Driver, driver)

    def list_driver_vendor_passthru(self, driver):
        """Get driver's vendor_passthru methods.

        :param driver: The value can be the name of a driver or a
            :class:`~openstack.baremetal.v1.driver.Driver` instance.

        :returns: One :dict: of vendor methods with corresponding usages
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            driver matching the name could be found.
        """
        driver = self.get_driver(driver)
        return driver.list_vendor_passthru(self)

    def call_driver_vendor_passthru(
        self,
        driver: ty.Union[str, _driver.Driver],
        verb: str,
        method: str,
        body: object = None,
    ) -> requests.Response:
        """Call driver's vendor_passthru method.

        :param driver: The value can be the name of a driver or a
            :class:`~openstack.baremetal.v1.driver.Driver` instance.
        :param verb: One of GET, POST, PUT, DELETE,
            depending on the driver and method.
        :param method: Name of vendor method.
        :param body: passed to the vendor function as json body.

        :returns: Server response
        """
        return self.get_driver(driver).call_vendor_passthru(
            self, verb, method, body
        )

    # ========== Nodes ==========

    def nodes(self, details=False, **query):
        """Retrieve a generator of nodes.

        :param details: A boolean indicating whether the detailed information
            for every node should be returned.
        :param dict query: Optional query parameters to be sent to restrict
            the nodes returned. Available parameters include:

            * ``associated``: Only return those which are, or are not,
              associated with an ``instance_id``.
            * ``conductor_group``: Only return those in the specified
              ``conductor_group``.
            * ``driver``: Only return those with the specified ``driver``.
            * ``fault``: Only return those with the specified fault type.
            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``instance_id``: Only return the node with this specific instance
              UUID or an empty set if not found.
            * ``is_maintenance``: Only return those with ``maintenance`` set to
              ``True`` or ``False``.
            * ``limit``: Requests at most the specified number of nodes be
              returned from the query.
            * ``marker``: Specifies the ID of the last-seen node. Use the
              ``limit`` parameter to make an initial limited request and
              use the ID of the last-seen node from the response as
              the ``marker`` value in a subsequent limited request.
            * ``provision_state``: Only return those nodes with the specified
              ``provision_state``.
            * ``resource_class``: Only return those with the specified
              ``resource_class``.
            * ``shard``: Only return nodes matching the supplied shard key.
            * ``sort_dir``: Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query pa rameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of :class:`~openstack.baremetal.v1.node.Node`
        """
        return _node.Node.list(self, details=details, **query)

    def create_node(self, **attrs):
        """Create a new node from attributes.

        See :meth:`~openstack.baremetal.v1.node.Node.create` for an explanation
        of the initial provision state.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.node.Node`.

        :returns: The results of node creation.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        """
        return self._create(_node.Node, **attrs)

    def find_node(self, name_or_id, ignore_missing=True, *, details=True):
        """Find a single node.

        :param str name_or_id: The name or ID of a node.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the node does not exist.  When set to `True``, None will
            be returned when attempting to find a nonexistent node.
        :param details: A boolean indicating whether the detailed information
            for the node should be returned.
        :returns: One :class:`~openstack.baremetal.v1.node.Node` object
            or None.
        """
        return self._find(
            _node.Node,
            name_or_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def get_node(self, node, fields=None):
        """Get a specific node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~openstack.baremetal.v1.node.Node`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            node matching the name or ID could be found.
        """
        return self._get_with_fields(_node.Node, node, fields=fields)

    def get_node_inventory(self, node):
        """Get a specific node's hardware inventory.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.

        :returns: The node inventory
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            inventory could be found.
        """
        res = self._get_resource(_node.Node, node)
        return res.get_node_inventory(self, node)

    def update_node(self, node, retry_on_conflict=True, **attrs):
        """Update a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param bool retry_on_conflict: Whether to retry HTTP CONFLICT error.
            Most of the time it can be retried, since it is caused by the node
            being locked. However, when setting ``instance_id``, this is
            a normal code and should not be retried.
        :param dict attrs: The attributes to update on the node represented
            by the ``node`` parameter.

        :returns: The updated node.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node, **attrs)
        return res.commit(self, retry_on_conflict=retry_on_conflict)

    def patch_node(
        self, node, patch, reset_interfaces=None, retry_on_conflict=True
    ):
        """Apply a JSON patch to the node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param patch: JSON patch to apply.
        :param bool reset_interfaces: whether to reset the node hardware
            interfaces to their defaults. This works only when changing
            drivers. Added in API microversion 1.45.
        :param bool retry_on_conflict: Whether to retry HTTP CONFLICT error.
            Most of the time it can be retried, since it is caused by the node
            being locked. However, when setting ``instance_id``, this is
            a normal code and should not be retried.

            See `Update Node
            <https://docs.openstack.org/api-ref/baremetal/?expanded=update-node-detail#update-node>`_
            for details.

        :returns: The updated node.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node)
        return res.patch(
            self,
            patch,
            retry_on_conflict=retry_on_conflict,
            reset_interfaces=reset_interfaces,
        )

    def set_node_provision_state(
        self,
        node,
        target,
        config_drive=None,
        clean_steps=None,
        rescue_password=None,
        wait=False,
        timeout=None,
        deploy_steps=None,
    ):
        """Run an action modifying node's provision state.

        This call is asynchronous, it will return success as soon as the Bare
        Metal service acknowledges the request.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param target: Provisioning action, e.g. ``active``, ``provide``.
            See the Bare Metal service documentation for available actions.
        :param config_drive: Config drive to pass to the node, only valid
            for ``active` and ``rebuild`` targets. You can use functions from
            :mod:`openstack.baremetal.configdrive` to build it.
        :param clean_steps: Clean steps to execute, only valid for ``clean``
            target.
        :param rescue_password: Password for the rescue operation, only valid
            for ``rescue`` target.
        :param wait: Whether to wait for the node to get into the expected
            state. The expected state is determined from a combination of
            the current provision state and ``target``.
        :param timeout: If ``wait`` is set to ``True``, specifies how much (in
            seconds) to wait for the expected state to be reached. The value of
            ``None`` (the default) means no client-side timeout.
        :param deploy_steps: Deploy steps to execute, only valid for ``active``
            and ``rebuild`` target.

        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        :raises: ValueError if ``config_drive``, ``clean_steps``,
            ``deploy_steps`` or ``rescue_password`` are provided with an
            invalid ``target``.
        """
        res = self._get_resource(_node.Node, node)
        return res.set_provision_state(
            self,
            target,
            config_drive=config_drive,
            clean_steps=clean_steps,
            rescue_password=rescue_password,
            wait=wait,
            timeout=timeout,
            deploy_steps=deploy_steps,
        )

    def get_node_boot_device(self, node):
        """Get node boot device

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :return: The node boot device
        """
        res = self._get_resource(_node.Node, node)
        return res.get_boot_device(self)

    def set_node_boot_device(self, node, boot_device, persistent=False):
        """Set node boot device

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param boot_device: Boot device to assign to the node.
        :param persistent: If the boot device change is maintained after node
            reboot
        :return: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node)
        return res.set_boot_device(self, boot_device, persistent=persistent)

    def get_node_supported_boot_devices(self, node):
        """Get supported boot devices for node

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :return: The node boot device
        """
        res = self._get_resource(_node.Node, node)
        return res.get_supported_boot_devices(self)

    def set_node_boot_mode(self, node, target):
        """Make a request to change node's boot mode

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param target: Boot mode to set for node, one of either 'uefi'/'bios'.
        """
        res = self._get_resource(_node.Node, node)
        return res.set_boot_mode(self, target)

    def set_node_secure_boot(self, node, target):
        """Make a request to change node's secure boot state

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param target: Boolean indicating secure boot state to set.
            True/False corresponding to 'on'/'off' respectively.
        """
        res = self._get_resource(_node.Node, node)
        return res.set_secure_boot(self, target)

    def inject_nmi_to_node(self, node):
        """Inject NMI to node.

        Injects a non-maskable interrupt (NMI) message to the node. This is
        used when response time is critical, such as during non-recoverable
        hardware errors. In addition, virsh inject-nmi is useful for triggering
        a crashdump in Windows guests.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :return: None
        """
        res = self._get_resource(_node.Node, node)
        res.inject_nmi(self)

    def wait_for_nodes_provision_state(
        self,
        nodes,
        expected_state,
        timeout=None,
        abort_on_failed_state=True,
        fail=True,
    ):
        """Wait for the nodes to reach the expected state.

        :param nodes: List of nodes - name, ID or
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param expected_state: The expected provisioning state to reach.
        :param timeout: If ``wait`` is set to ``True``, specifies how much (in
            seconds) to wait for the expected state to be reached. The value of
            ``None`` (the default) means no client-side timeout.
        :param abort_on_failed_state: If ``True`` (the default), abort waiting
            if any node reaches a failure state which does not match the
            expected one. Note that the failure state for ``enroll`` ->
            ``manageable`` transition is ``enroll`` again.
        :param fail: If set to ``False`` this call will not raise on timeouts
            and provisioning failures.

        :return: If `fail` is ``True`` (the default), the list of
            :class:`~openstack.baremetal.v1.node.Node` instances that reached
            the requested state. If `fail` is ``False``, a
            :class:`~openstack.baremetal.v1.node.WaitResult` named tuple.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if a node
            reaches an error state and ``abort_on_failed_state`` is ``True``.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` on timeout.
        """
        log_nodes = ', '.join(
            n.id if isinstance(n, _node.Node) else n for n in nodes
        )

        finished = []
        failed = []
        remaining = nodes
        try:
            for count in utils.iterate_timeout(
                timeout,
                f"Timeout waiting for nodes {log_nodes} to reach "
                f"target state '{expected_state}'",
            ):
                nodes = [self.get_node(n) for n in remaining]
                remaining = []
                for n in nodes:
                    try:
                        if n._check_state_reached(
                            self, expected_state, abort_on_failed_state
                        ):
                            finished.append(n)
                        else:
                            remaining.append(n)
                    except exceptions.ResourceFailure:
                        if fail:
                            raise
                        else:
                            failed.append(n)

                if not remaining:
                    if fail:
                        return finished
                    else:
                        return _node.WaitResult(finished, failed, [])

                self.log.debug(
                    'Still waiting for nodes %(nodes)s to reach state '
                    '"%(target)s"',
                    {
                        'nodes': ', '.join(n.id for n in remaining),
                        'target': expected_state,
                    },
                )
        except exceptions.ResourceTimeout:
            if fail:
                raise
            else:
                return _node.WaitResult(finished, failed, remaining)

    def set_node_power_state(self, node, target, wait=False, timeout=None):
        """Run an action modifying node's power state.

        This call is asynchronous, it will return success as soon as the Bare
        Metal service acknowledges the request.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param target: Target power state, one of
            :class:`~openstack.baremetal.v1.node.PowerAction` or a string.
        :param wait: Whether to wait for the node to get into the expected
            state.
        :param timeout: If ``wait`` is set to ``True``, specifies how much (in
            seconds) to wait for the expected state to be reached. The value of
            ``None`` (the default) means no client-side timeout.
        """
        self._get_resource(_node.Node, node).set_power_state(
            self, target, wait=wait, timeout=timeout
        )

    def wait_for_node_power_state(self, node, expected_state, timeout=None):
        """Wait for the node to reach the power state.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param timeout: How much (in seconds) to wait for the target state
            to be reached. The value of ``None`` (the default) means
            no timeout.

        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node)
        return res.wait_for_power_state(self, expected_state, timeout=timeout)

    def wait_for_node_reservation(self, node, timeout=None):
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

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param timeout: How much (in seconds) to wait for the lock to be
            released. The value of ``None`` (the default) means no timeout.

        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node)
        return res.wait_for_reservation(self, timeout=timeout)

    def validate_node(self, node, required=('boot', 'deploy', 'power')):
        """Validate required information on a node.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param required: List of interfaces that are required to pass
            validation. The default value is the list of minimum required
            interfaces for provisioning.

        :return: dict mapping interface names to
            :class:`~openstack.baremetal.v1.node.ValidationResult` objects.
        :raises: :exc:`~openstack.exceptions.ValidationException` if validation
            fails for a required interface.
        """
        res = self._get_resource(_node.Node, node)
        return res.validate(self, required=required)

    def set_node_maintenance(self, node, reason=None):
        """Enable maintenance mode on the node.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param reason: Optional reason for maintenance.
        :return: This :class:`Node` instance.
        """
        res = self._get_resource(_node.Node, node)
        return res.set_maintenance(self, reason)

    def unset_node_maintenance(self, node):
        """Disable maintenance mode on the node.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :return: This :class:`Node` instance.
        """
        res = self._get_resource(_node.Node, node)
        return res.unset_maintenance(self)

    def delete_node(self, node, ignore_missing=True):
        """Delete a node.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the node could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            node.

        :returns: The instance of the node which was deleted.
        :rtype: :class:`~openstack.baremetal.v1.node.Node`.
        """
        return self._delete(_node.Node, node, ignore_missing=ignore_missing)

    # ========== Node actions ==========

    def add_node_trait(self, node, trait):
        """Add a trait to a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param trait: trait to remove from the node.
        :returns: The updated node
        """
        res = self._get_resource(_node.Node, node)
        return res.add_trait(self, trait)

    def remove_node_trait(self, node, trait, ignore_missing=True):
        """Remove a trait from a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param trait: trait to remove from the node.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the trait could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            trait.
        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node)
        return res.remove_trait(self, trait, ignore_missing=ignore_missing)

    def call_node_vendor_passthru(self, node, verb, method, body=None):
        """Calls vendor_passthru for a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param verb: The HTTP verb, one of GET, SET, POST, DELETE.
        :param method: The method to call using vendor_passthru.
        :param body: The JSON body in the HTTP call.
        :returns: The raw response from the method.
        """
        res = self._get_resource(_node.Node, node)
        return res.call_vendor_passthru(self, verb, method, body)

    def list_node_vendor_passthru(self, node):
        """Lists vendor_passthru for a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :returns: A list of vendor_passthru methods for the node.
        """
        res = self._get_resource(_node.Node, node)
        return res.list_vendor_passthru(self)

    def get_node_console(self, node):
        """Get the console for a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :returns: Connection information for the console.
        """
        res = self._get_resource(_node.Node, node)
        return res.get_console(self)

    def enable_node_console(self, node):
        """Enable the console for a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :returns: None
        """
        res = self._get_resource(_node.Node, node)
        return res.set_console_mode(self, True)

    def disable_node_console(self, node):
        """Disable the console for a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :returns: None
        """
        res = self._get_resource(_node.Node, node)
        return res.set_console_mode(self, False)

    def set_node_traits(self, node, traits):
        """Set traits for a node.

        Removes any existing traits and adds the traits passed in to this
        method.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :param traits: list of traits to add to the node.
        :returns: The updated :class:`~openstack.baremetal.v1.node.Node`
        """
        res = self._get_resource(_node.Node, node)
        return res.set_traits(self, traits)

    def list_node_firmware(self, node):
        """Lists firmware components for a node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.baremetal.v1.node.Node` instance.
        :returns: A list of the node's firmware components.
        """
        res = self._get_resource(_node.Node, node)
        return res.list_firmware(self)

    # ========== Ports ==========

    def ports(self, details=False, **query):
        """Retrieve a generator of ports.

        :param details: A boolean indicating whether the detailed information
            for every port should be returned.
        :param dict query: Optional query parameters to be sent to restrict
            the ports returned. Available parameters include:

            * ``address``: Only return ports with the specified physical
              hardware address, typically a MAC address.
            * ``driver``: Only return those with the specified ``driver``.
            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of ports be
              returned from the query.
            * ``marker``: Specifies the ID of the last-seen port. Use the
              ``limit`` parameter to make an initial limited request and
              use the ID of the last-seen port from the response as
              the ``marker`` value in a subsequent limited request.
            * ``node``:only return the ones associated with this specific node
              (name or UUID), or an empty set if not found.
            * ``node_id``:only return the ones associated with this specific
              node UUID, or an empty set if not found.
            * ``portgroup``: only return the ports associated with this
              specific Portgroup (name or UUID), or an empty set if not
              found.  Added in API microversion 1.24.
            * ``sort_dir``: Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query parameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of port instances.
        """
        return _port.Port.list(self, details=details, **query)

    def create_port(self, **attrs):
        """Create a new port from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.port.Port`.

        :returns: The results of port creation.
        :rtype: :class:`~openstack.baremetal.v1.port.Port`.
        """
        return self._create(_port.Port, **attrs)

    # TODO(stephenfin): Delete this. You can't lookup a port by name so this is
    # identical to get_port
    def find_port(self, name_or_id, ignore_missing=True, *, details=True):
        """Find a single port.

        :param str name_or_id: The ID of a port.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the port does not exist.  When set to `True``, None will
            be returned when attempting to find a nonexistent port.
        :param details: A boolean indicating whether the detailed information
            for every port should be returned.
        :returns: One :class:`~openstack.baremetal.v1.port.Port` object
            or None.
        """
        return self._find(
            _port.Port,
            name_or_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def get_port(self, port, fields=None):
        """Get a specific port.

        :param port: The value can be the ID of a port or a
            :class:`~openstack.baremetal.v1.port.Port` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~openstack.baremetal.v1.port.Port`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            port matching the name or ID could be found.
        """
        return self._get_with_fields(_port.Port, port, fields=fields)

    def update_port(self, port, **attrs):
        """Update a port.

        :param port: Either the ID of a port or an instance
            of :class:`~openstack.baremetal.v1.port.Port`.
        :param dict attrs: The attributes to update on the port represented
            by the ``port`` parameter.

        :returns: The updated port.
        :rtype: :class:`~openstack.baremetal.v1.port.Port`
        """
        return self._update(_port.Port, port, **attrs)

    def patch_port(self, port, patch):
        """Apply a JSON patch to the port.

        :param port: The value can be the ID of a port or a
            :class:`~openstack.baremetal.v1.port.Port` instance.
        :param patch: JSON patch to apply.

        :returns: The updated port.
        :rtype: :class:`~openstack.baremetal.v1.port.Port`
        """
        return self._get_resource(_port.Port, port).patch(self, patch)

    def delete_port(self, port, ignore_missing=True):
        """Delete a port.

        :param port: The value can be either the ID of a port or
            a :class:`~openstack.baremetal.v1.port.Port` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the port could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            port.

        :returns: The instance of the port which was deleted.
        :rtype: :class:`~openstack.baremetal.v1.port.Port`.
        """
        return self._delete(_port.Port, port, ignore_missing=ignore_missing)

    # ========== Port groups ==========

    def port_groups(self, details=False, **query):
        """Retrieve a generator of port groups.

        :param details: A boolean indicating whether the detailed information
            for every port group should be returned.
        :param dict query: Optional query parameters to be sent to restrict
            the port groups returned. Available parameters include:

            * ``address``: Only return portgroups with the specified physical
              hardware address, typically a MAC address.
            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of portgroups
              returned from the query.
            * ``marker``: Specifies the ID of the last-seen portgroup. Use the
              ``limit`` parameter to make an initial limited request and
              use the ID of the last-seen portgroup from the response as
              the ``marker`` value in a subsequent limited request.
            * ``node``:only return the ones associated with this specific node
              (name or UUID), or an empty set if not found.
            * ``sort_dir``: Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query parameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of port group instances.
        """
        return _portgroup.PortGroup.list(self, details=details, **query)

    def create_port_group(self, **attrs):
        """Create a new portgroup from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.port_group.PortGroup`.

        :returns: The results of portgroup creation.
        :rtype: :class:`~openstack.baremetal.v1.port_group.PortGroup`.
        """
        return self._create(_portgroup.PortGroup, **attrs)

    def find_port_group(
        self,
        name_or_id,
        ignore_missing=True,
        *,
        details=True,
    ):
        """Find a single port group.

        :param str name_or_id: The name or ID of a portgroup.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the port group does not exist.  When set to `True``, None will
            be returned when attempting to find a nonexistent port group.
        :param details: A boolean indicating whether the detailed information
            for the port group should be returned.
        :returns: One :class:`~openstack.baremetal.v1.port_group.PortGroup`
            object or None.
        """
        return self._find(
            _portgroup.PortGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def get_port_group(self, port_group, fields=None):
        """Get a specific port group.

        :param port_group: The value can be the name or ID of a chassis or a
            :class:`~openstack.baremetal.v1.port_group.PortGroup` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~openstack.baremetal.v1.port_group.PortGroup`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            port group matching the name or ID could be found.
        """
        return self._get_with_fields(
            _portgroup.PortGroup, port_group, fields=fields
        )

    def update_port_group(self, port_group, **attrs):
        """Update a port group.

        :param port_group: Either the name or the ID of a port group or
            an instance of
            :class:`~openstack.baremetal.v1.port_group.PortGroup`.
        :param dict attrs: The attributes to update on the port group
            represented by the ``port_group`` parameter.

        :returns: The updated port group.
        :rtype: :class:`~openstack.baremetal.v1.port_group.PortGroup`
        """
        return self._update(_portgroup.PortGroup, port_group, **attrs)

    def patch_port_group(self, port_group, patch):
        """Apply a JSON patch to the port_group.

        :param port_group: The value can be the ID of a port group or a
            :class:`~openstack.baremetal.v1.port_group.PortGroup` instance.
        :param patch: JSON patch to apply.

        :returns: The updated port group.
        :rtype: :class:`~openstack.baremetal.v1.port_group.PortGroup`
        """
        res = self._get_resource(_portgroup.PortGroup, port_group)
        return res.patch(self, patch)

    def delete_port_group(self, port_group, ignore_missing=True):
        """Delete a port group.

        :param port_group: The value can be either the name or ID of
            a port group or a
            :class:`~openstack.baremetal.v1.port_group.PortGroup`
            instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the port group could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            port group.

        :returns: The instance of the port group which was deleted.
        :rtype: :class:`~openstack.baremetal.v1.port_group.PortGroup`.
        """
        return self._delete(
            _portgroup.PortGroup, port_group, ignore_missing=ignore_missing
        )

    # ========== Virtual Media ==========

    def attach_vmedia_to_node(
        self,
        node,
        device_type,
        image_url,
        image_download_source=None,
        retry_on_conflict=True,
    ):
        """Attach virtual media device to a node.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param device_type: The type of virtual media device.
        :param image_url: The URL of the image to attach.
        :param image_download_source: The source of the image download.
        :param retry_on_conflict: Whether to retry HTTP CONFLICT errors.
            This can happen when either the virtual media is already used on
            a node or the node is locked. Since the latter happens more often,
            the default value is True.
        :return: ``None``
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VMEDIA API.
        """
        res = self._get_resource(_node.Node, node)
        res.attach_vmedia(
            self,
            device_type=device_type,
            image_url=image_url,
            image_download_source=image_download_source,
            retry_on_conflict=retry_on_conflict,
        )

    def detach_vmedia_from_node(self, node, device_types=None):
        """Detach virtual media from the node.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param device_types: A list with the types of virtual media
            devices to detach.
        :return: ``True`` if the virtual media was detached,
            otherwise ``False``.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VMEDIA API.
        """
        res = self._get_resource(_node.Node, node)
        return res.detach_vmedia(self, device_types=device_types)

    # ========== VIFs ==========

    def attach_vif_to_node(
        self,
        node: ty.Union[_node.Node, str],
        vif_id: str,
        retry_on_conflict: bool = True,
        *,
        port_id: ty.Optional[str] = None,
        port_group_id: ty.Optional[str] = None,
    ) -> None:
        """Attach a VIF to the node.

        The exact form of the VIF ID depends on the network interface used by
        the node. In the most common case it is a Network service port
        (NOT a Bare Metal port) ID. A VIF can only be attached to one node
        at a time.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param vif_id: Backend-specific VIF ID.
        :param retry_on_conflict: Whether to retry HTTP CONFLICT errors.
            This can happen when either the VIF is already used on a node or
            the node is locked. Since the latter happens more often, the
            default value is True.
        :param port_id: The UUID of the port to attach the VIF to. Only one of
            port_id or port_group_id can be provided.
        :param port_group_id: The UUID of the portgroup to attach to. Only one
            of port_group_id or port_id can be provided.
        :return: None
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VIF API.
        :raises: :exc:`~openstack.exceptions.InvalidRequest` if both port_id
            and port_group_id are provided.
        """
        res = self._get_resource(_node.Node, node)
        res.attach_vif(
            self,
            vif_id=vif_id,
            retry_on_conflict=retry_on_conflict,
            port_id=port_id,
            port_group_id=port_group_id,
        )

    def detach_vif_from_node(self, node, vif_id, ignore_missing=True):
        """Detach a VIF from the node.

        The exact form of the VIF ID depends on the network interface used by
        the node. In the most common case it is a Network service port
        (NOT a Bare Metal port) ID.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param string vif_id: Backend-specific VIF ID.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the VIF does not exist. Otherwise, ``False``
            is returned.
        :return: ``True`` if the VIF was detached, otherwise ``False``.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VIF API.
        """
        res = self._get_resource(_node.Node, node)
        return res.detach_vif(self, vif_id, ignore_missing=ignore_missing)

    def list_node_vifs(self, node):
        """List IDs of VIFs attached to the node.

        The exact form of the VIF ID depends on the network interface used by
        the node. In the most common case it is a Network service port
        (NOT a Bare Metal port) ID.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :return: List of VIF IDs as strings.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the server
            does not support the VIF API.
        """
        res = self._get_resource(_node.Node, node)
        return res.list_vifs(self)

    # ========== Allocations ==========

    def allocations(self, **query):
        """Retrieve a generator of allocations.

        :param dict query: Optional query parameters to be sent to restrict
            the allocation to be returned. Available parameters include:

            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of items be
              returned from the query.
            * ``marker``: Specifies the ID of the last-seen allocation. Use the
              ``limit`` parameter to make an initial limited request and
              use the ID of the last-seen allocation from the response as
              the ``marker`` value in a subsequent limited request.
            * ``sort_dir``: Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query parameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of allocation instances.
        """
        return _allocation.Allocation.list(self, **query)

    def create_allocation(self, **attrs):
        """Create a new allocation from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.allocation.Allocation`.

        :returns: The results of allocation creation.
        :rtype: :class:`~openstack.baremetal.v1.allocation.Allocation`.
        """
        return self._create(_allocation.Allocation, **attrs)

    def get_allocation(self, allocation, fields=None):
        """Get a specific allocation.

        :param allocation: The value can be the name or ID of an allocation or
            a :class:`~openstack.baremetal.v1.allocation.Allocation` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~openstack.baremetal.v1.allocation.Allocation`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            allocation matching the name or ID could be found.
        """
        return self._get_with_fields(
            _allocation.Allocation, allocation, fields=fields
        )

    def update_allocation(self, allocation, **attrs):
        """Update an allocation.

        :param allocation: The value can be the name or ID of an allocation or
            a :class:`~openstack.baremetal.v1.allocation.Allocation` instance.
        :param dict attrs: The attributes to update on the allocation
            represented by the ``allocation`` parameter.

        :returns: The updated allocation.
        :rtype: :class:`~openstack.baremetal.v1.allocation.Allocation`
        """
        return self._update(_allocation.Allocation, allocation, **attrs)

    def patch_allocation(self, allocation, patch):
        """Apply a JSON patch to the allocation.

        :param allocation: The value can be the name or ID of an allocation or
            a :class:`~openstack.baremetal.v1.allocation.Allocation` instance.
        :param patch: JSON patch to apply.

        :returns: The updated allocation.
        :rtype: :class:`~openstack.baremetal.v1.allocation.Allocation`
        """
        return self._get_resource(_allocation.Allocation, allocation).patch(
            self, patch
        )

    def delete_allocation(self, allocation, ignore_missing=True):
        """Delete an allocation.

        :param allocation: The value can be the name or ID of an allocation or
            a :class:`~openstack.baremetal.v1.allocation.Allocation` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the allocation could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            allocation.

        :returns: The instance of the allocation which was deleted.
        :rtype: :class:`~openstack.baremetal.v1.allocation.Allocation`.
        """
        return self._delete(
            _allocation.Allocation, allocation, ignore_missing=ignore_missing
        )

    def wait_for_allocation(
        self, allocation, timeout=None, ignore_error=False
    ):
        """Wait for the allocation to become active.

        :param allocation: The value can be the name or ID of an allocation or
            a :class:`~openstack.baremetal.v1.allocation.Allocation` instance.
        :param timeout: How much (in seconds) to wait for the allocation.
            The value of ``None`` (the default) means no client-side timeout.
        :param ignore_error: If ``True``, this call will raise an exception
            if the allocation reaches the ``error`` state. Otherwise the error
            state is considered successful and the call returns.

        :returns: The instance of the allocation.
        :rtype: :class:`~openstack.baremetal.v1.allocation.Allocation`.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if allocation
            fails and ``ignore_error`` is ``False``.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` on timeout.
        """
        res = self._get_resource(_allocation.Allocation, allocation)
        return res.wait(self, timeout=timeout, ignore_error=ignore_error)

    # ========== Volume connectors ==========

    def volume_connectors(self, details=False, **query):
        """Retrieve a generator of volume_connector.

        :param details: A boolean indicating whether the detailed information
            for every volume_connector should be returned.
        :param dict query: Optional query parameters to be sent to restrict
            the volume_connectors returned. Available parameters include:

            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of
              volume_connector be returned from the query.
            * ``marker``: Specifies the ID of the last-seen volume_connector.
              Use the ``limit`` parameter to make an initial limited request
              and use the ID of the last-seen volume_connector from the
              response as the ``marker`` value in subsequent limited request.
            * ``node``:only return the ones associated with this specific node
              (name or UUID), or an empty set if not found.
            * ``sort_dir``:Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query parameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of volume_connector instances.
        """
        if details:
            query['detail'] = True
        return _volumeconnector.VolumeConnector.list(self, **query)

    def create_volume_connector(self, **attrs):
        """Create a new volume_connector from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`.

        :returns: The results of volume_connector creation.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`.
        """
        return self._create(_volumeconnector.VolumeConnector, **attrs)

    # TODO(stephenfin): Delete this. You can't lookup a volume connector by
    # name so this is identical to get_volume_connector
    def find_volume_connector(
        self,
        vc_id,
        ignore_missing=True,
        *,
        details=True,
    ):
        """Find a single volume connector.

        :param str vc_id: The ID of a volume connector.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume connector does not exist.  When set to `True``,
            None will be returned when attempting to find a nonexistent
            volume connector.
        :param details: A boolean indicating whether the detailed information
            for the volume connector should be returned.

        :returns: One
            :class:`~openstack.baremetal.v1.volumeconnector.VolumeConnector`
            object or None.
        """
        return self._find(
            _volumeconnector.VolumeConnector,
            vc_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def get_volume_connector(self, volume_connector, fields=None):
        """Get a specific volume_connector.

        :param volume_connector: The value can be the ID of a
            volume_connector or a
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`
            instance.
        :param fields: Limit the resource fields to fetch.`

        :returns: One
            :class: `~openstack.baremetal.v1.volume_connector.VolumeConnector`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            volume_connector matching the name or ID could be found.`
        """
        return self._get_with_fields(
            _volumeconnector.VolumeConnector, volume_connector, fields=fields
        )

    def update_volume_connector(self, volume_connector, **attrs):
        """Update a volume_connector.

        :param volume_connector: Either the ID of a volume_connector
            or an instance of
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`.
        :param dict attrs: The attributes to update on the
            volume_connector represented by the ``volume_connector``
            parameter.

        :returns: The updated volume_connector.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`
        """
        return self._update(
            _volumeconnector.VolumeConnector, volume_connector, **attrs
        )

    def patch_volume_connector(self, volume_connector, patch):
        """Apply a JSON patch to the volume_connector.

        :param volume_connector: The value can be the ID of a
            volume_connector or a
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`
            instance.
        :param patch: JSON patch to apply.

        :returns: The updated volume_connector.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector.`
        """
        return self._get_resource(
            _volumeconnector.VolumeConnector, volume_connector
        ).patch(self, patch)

    def delete_volume_connector(self, volume_connector, ignore_missing=True):
        """Delete an volume_connector.

        :param volume_connector: The value can be either the ID of a
            volume_connector.VolumeConnector or a
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`
            instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume_connector could not be found.
            When set to ``True``, no exception will be raised when
            attempting to delete a non-existent volume_connector.

        :returns: The instance of the volume_connector which was deleted.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_connector.VolumeConnector`.
        """
        return self._delete(
            _volumeconnector.VolumeConnector,
            volume_connector,
            ignore_missing=ignore_missing,
        )

    # ========== Volume targets ==========

    def volume_targets(self, details=False, **query):
        """Retrieve a generator of volume_target.

        :param details: A boolean indicating whether the detailed information
            for every volume_target should be returned.
        :param dict query: Optional query parameters to be sent to restrict
            the volume_targets returned. Available parameters include:

            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of
              volume_connector be returned from the query.
            * ``marker``: Specifies the ID of the last-seen volume_target.
              Use the ``limit`` parameter to make an initial limited request
              and use the ID of the last-seen volume_target from the
              response as the ``marker`` value in subsequent limited request.
            * ``node``:only return the ones associated with this specific node
              (name or UUID), or an empty set if not found.
            * ``sort_dir``:Sorts the response by the requested sort direction.
              A valid value is ``asc`` (ascending) or ``desc``
              (descending). Default is ``asc``. You can specify multiple
              pairs of sort key and sort direction query parameters. If
              you omit the sort direction in a pair, the API uses the
              natural sorting direction of the server attribute that is
              provided as the ``sort_key``.
            * ``sort_key``: Sorts the response by the this attribute value.
              Default is ``id``. You can specify multiple pairs of sort
              key and sort direction query parameters. If you omit the
              sort direction in a pair, the API uses the natural sorting
              direction of the server attribute that is provided as the
              ``sort_key``.

        :returns: A generator of volume_target instances.
        """
        if details:
            query['detail'] = True
        return _volumetarget.VolumeTarget.list(self, **query)

    def create_volume_target(self, **attrs):
        """Create a new volume_target from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`.

        :returns: The results of volume_target creation.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`.
        """
        return self._create(_volumetarget.VolumeTarget, **attrs)

    # TODO(stephenfin): Delete this. You can't lookup a volume target by
    # name so this is identical to get_volume_connector
    def find_volume_target(self, vt_id, ignore_missing=True, *, details=True):
        """Find a single volume target.

        :param str vt_id: The ID of a volume target.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume connector does not exist.  When set to `True``,
            None will be returned when attempting to find a nonexistent
            volume target.
        :param details: A boolean indicating whether the detailed information
            for the volume target should be returned.

        :returns: One
            :class:`~openstack.baremetal.v1.volumetarget.VolumeTarget`
            object or None.
        """
        return self._find(
            _volumetarget.VolumeTarget,
            vt_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def get_volume_target(self, volume_target, fields=None):
        """Get a specific volume_target.

        :param volume_target: The value can be the ID of a
            volume_target or a
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`
            instance.
        :param fields: Limit the resource fields to fetch.`

        :returns: One
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            volume_target matching the name or ID could be found.`
        """
        return self._get_with_fields(
            _volumetarget.VolumeTarget, volume_target, fields=fields
        )

    def update_volume_target(self, volume_target, **attrs):
        """Update a volume_target.

        :param volume_target: Either the ID of a volume_target
            or an instance of
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`.
        :param dict attrs: The attributes to update on the
            volume_target represented by the ``volume_target`` parameter.

        :returns: The updated volume_target.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`
        """
        return self._update(_volumetarget.VolumeTarget, volume_target, **attrs)

    def patch_volume_target(self, volume_target, patch):
        """Apply a JSON patch to the volume_target.

        :param volume_target: The value can be the ID of a
            volume_target or a
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`
            instance.
        :param patch: JSON patch to apply.

        :returns: The updated volume_target.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget.`
        """
        return self._get_resource(
            _volumetarget.VolumeTarget, volume_target
        ).patch(self, patch)

    def delete_volume_target(self, volume_target, ignore_missing=True):
        """Delete an volume_target.

        :param volume_target: The value can be either the ID of a
            volume_target.VolumeTarget or a
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`
            instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume_target could not be found.
            When set to ``True``, no exception will be raised when
            attempting to delete a non-existent volume_target.

        :returns: The instance of the volume_target which was deleted.
        :rtype:
            :class:`~openstack.baremetal.v1.volume_target.VolumeTarget`.
        """
        return self._delete(
            _volumetarget.VolumeTarget,
            volume_target,
            ignore_missing=ignore_missing,
        )

    # ========== Deploy templates ==========

    def deploy_templates(self, details=False, **query):
        """Retrieve a generator of deploy_templates.

        :param details: A boolean indicating whether the detailed information
            for every deploy_templates should be returned.
        :param dict query: Optional query parameters to be sent to
            restrict the deploy_templates to be returned.

        :returns: A generator of Deploy templates instances.
        """
        if details:
            query['detail'] = True
        return _deploytemplates.DeployTemplate.list(self, **query)

    def create_deploy_template(self, **attrs):
        """Create a new deploy_template from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`.

        :returns: The results of deploy_template creation.
        :rtype:
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`.
        """
        return self._create(_deploytemplates.DeployTemplate, **attrs)

    def update_deploy_template(self, deploy_template, **attrs):
        """Update a deploy_template.

        :param deploy_template: Either the ID of a deploy_template,
            or an instance of
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`.
        :param dict attrs: The attributes to update on
            the deploy_template represented
            by the ``deploy_template`` parameter.

        :returns: The updated deploy_template.
        :rtype:
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`
        """
        return self._update(
            _deploytemplates.DeployTemplate, deploy_template, **attrs
        )

    def delete_deploy_template(self, deploy_template, ignore_missing=True):
        """Delete a deploy_template.

        :param deploy_template:The value can be
            either the ID of a deploy_template or a
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`
            instance.

        :param bool ignore_missing: When set to ``False``,
            an exception:class:`~openstack.exceptions.NotFoundException`
            will be raised when the deploy_template
            could not be found.
            When set to ``True``, no
            exception will be raised when attempting
            to delete a non-existent
            deploy_template.

        :returns: The instance of the deploy_template which was deleted.
        :rtype:
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`.
        """

        return self._delete(
            _deploytemplates.DeployTemplate,
            deploy_template,
            ignore_missing=ignore_missing,
        )

    def get_deploy_template(self, deploy_template, fields=None):
        """Get a specific deployment template.

        :param deploy_template: The value can be the name or ID
            of a deployment template
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`
            instance.

        :param fields: Limit the resource fields to fetch.

        :returns: One
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no deployment template matching the name or
            ID could be found.
        """
        return self._get_with_fields(
            _deploytemplates.DeployTemplate, deploy_template, fields=fields
        )

    def find_deploy_template(
        self,
        name_or_id,
        ignore_missing=True,
        *,
        details=True,
    ):
        """Find a single deployment template.

        :param str name_or_id: The name or ID of a deployment template.
        :param bool ignore_missing: When set to ``False``, an exception of
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the deployment template does not exist.  When set to `True``,
            None will be returned when attempting to find a nonexistent
            deployment template.
        :param details: A boolean indicating whether the detailed information
            for the deployment template should be returned.

        :returns: One
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate` or
            None.
        """
        return self._find(
            _deploytemplates.DeployTemplate,
            name_or_id,
            ignore_missing=ignore_missing,
            details=details,
        )

    def patch_deploy_template(self, deploy_template, patch):
        """Apply a JSON patch to the deploy_templates.

        :param deploy_templates: The value can be the ID of a
            deploy_template or a
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`
            instance.

        :param patch: JSON patch to apply.

        :returns: The updated deploy_template.
        :rtype:
            :class:`~openstack.baremetal.v1.deploy_templates.DeployTemplate`
        """
        return self._get_resource(
            _deploytemplates.DeployTemplate, deploy_template
        ).patch(self, patch)

    # ========== Conductors ==========

    def conductors(self, details=False, **query):
        """Retrieve a generator of conductors.

        :param bool details: A boolean indicating whether the detailed
            information for every conductor should be returned.

        :returns: A generator of conductor instances.
        """

        if details:
            query['details'] = True
        return _conductor.Conductor.list(self, **query)

    # NOTE(stephenfin): There is no 'find_conductor' since conductors are
    # identified by the host name, not an arbitrary UUID, meaning
    # 'find_conductor' would be identical to 'get_conductor'

    def get_conductor(self, conductor, fields=None):
        """Get a specific conductor.

        :param conductor: The value can be the name of a conductor or a
            :class:`~openstack.baremetal.v1.conductor.Conductor` instance.

        :returns: One :class:`~openstack.baremetal.v1.conductor.Conductor`

        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            conductor matching the name could be found.
        """
        return self._get_with_fields(
            _conductor.Conductor, conductor, fields=fields
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)
