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

from openstack import _log
from openstack.baremetal.v1 import node as _node
from openstack.baremetal_introspection.v1 import introspection as _introspect
from openstack.baremetal_introspection.v1 import (
    introspection_rule as _introspection_rule,
)
from openstack import exceptions
from openstack import proxy
from openstack import resource


_logger = _log.setup_logging('openstack')


class Proxy(proxy.Proxy):
    _resource_registry = {
        "introspection": _introspect.Introspection,
        "introspection_rule": _introspection_rule.IntrospectionRule,
    }

    # ========== Introspections ==========

    def introspections(self, **query):
        """Retrieve a generator of introspection records.

        :param dict query: Optional query parameters to be sent to restrict
            the records to be returned. Available parameters include:

            * ``fields``: A list containing one or more fields to be returned
              in the response. This may lead to some performance gain
              because other fields of the resource are not refreshed.
            * ``limit``: Requests at most the specified number of items be
              returned from the query.
            * ``marker``: Specifies the ID of the last-seen introspection. Use
              the ``limit`` parameter to make an initial limited request and
              use the ID of the last-seen introspection from the response as
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

        :returns: A generator of :class:`~.introspection.Introspection`
            objects
        """
        return _introspect.Introspection.list(self, **query)

    def start_introspection(self, node, manage_boot=None):
        """Create a new introspection from attributes.

        :param node: The value can be either the name or ID of a node or
            a :class:`~openstack.baremetal.v1.node.Node` instance.
        :param bool manage_boot: Whether to manage boot parameters for the
            node. Defaults to the server default (which is `True`).

        :returns: :class:`~.introspection.Introspection` instance.
        """
        node = self._get_resource(_node.Node, node)
        res = _introspect.Introspection.new(
            connection=self._get_connection(), id=node.id
        )
        kwargs = {}
        if manage_boot is not None:
            kwargs['manage_boot'] = manage_boot
        return res.create(self, **kwargs)

    def get_introspection(self, introspection):
        """Get a specific introspection.

        :param introspection: The value can be the name or ID of an
            introspection (matching bare metal node name or ID) or
            an :class:`~.introspection.Introspection` instance.
        :returns: :class:`~.introspection.Introspection` instance.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            introspection matching the name or ID could be found.
        """
        return self._get(_introspect.Introspection, introspection)

    def get_introspection_data(self, introspection, processed=True):
        """Get introspection data.

        :param introspection: The value can be the name or ID of an
            introspection (matching bare metal node name or ID) or
            an :class:`~.introspection.Introspection` instance.
        :param processed: Whether to fetch the final processed data (the
            default) or the raw unprocessed data as received from the ramdisk.
        :returns: introspection data from the most recent successful run.
        :rtype: dict
        """
        res = self._get_resource(_introspect.Introspection, introspection)
        return res.get_data(self, processed=processed)

    def abort_introspection(self, introspection, ignore_missing=True):
        """Abort an introspection.

        Note that the introspection is not aborted immediately, you may use
        `wait_for_introspection` with `ignore_error=True`.

        :param introspection: The value can be the name or ID of an
            introspection (matching bare metal node name or ID) or
            an :class:`~.introspection.Introspection` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the introspection could not be found. When set to ``True``, no
            exception will be raised when attempting to abort a non-existent
            introspection.
        :returns: nothing
        """
        res = self._get_resource(_introspect.Introspection, introspection)
        try:
            res.abort(self)
        except exceptions.NotFoundException:
            if not ignore_missing:
                raise

    def wait_for_introspection(
        self,
        introspection,
        timeout=None,
        ignore_error=False,
    ):
        """Wait for the introspection to finish.

        :param introspection: The value can be the name or ID of an
            introspection (matching bare metal node name or ID) or
            an :class:`~.introspection.Introspection` instance.
        :param timeout: How much (in seconds) to wait for the introspection.
            The value of ``None`` (the default) means no client-side timeout.
        :param ignore_error: If ``True``, this call will raise an exception
            if the introspection reaches the ``error`` state. Otherwise the
            error state is considered successful and the call returns.
        :returns: :class:`~.introspection.Introspection` instance.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if
            introspection fails and ``ignore_error`` is ``False``.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` on timeout.
        """
        res = self._get_resource(_introspect.Introspection, introspection)
        return res.wait(self, timeout=timeout, ignore_error=ignore_error)

    # ========== Introspection ruless ==========

    def create_introspection_rule(self, **attrs):
        """Create a new introspection rules from attributes.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~.introspection_rule.IntrospectionRule`,
            comprised of the properties on the IntrospectionRule class.

        :returns: :class:`~.introspection_rule.IntrospectionRule` instance.
        """
        return self._create(_introspection_rule.IntrospectionRule, **attrs)

    def delete_introspection_rule(
        self,
        introspection_rule,
        ignore_missing=True,
    ):
        """Delete an introspection rule.

        :param introspection_rule: The value can be either the ID of an
            introspection rule or a
            :class:`~.introspection_rule.IntrospectionRule` instance.
        :param bool ignore_missing: When set to ``False``, an
            exception:class:`~openstack.exceptions.NotFoundException` will be
            raised when the introspection rule could not be found. When set to
            ``True``, no exception will be raised when attempting to delete a
            non-existent introspection rule.

        :returns: ``None``
        """
        self._delete(
            _introspection_rule.IntrospectionRule,
            introspection_rule,
            ignore_missing=ignore_missing,
        )

    def get_introspection_rule(self, introspection_rule):
        """Get a specific introspection rule.

        :param introspection_rule: The value can be the name or ID of an
            introspection rule or a
            :class:`~.introspection_rule.IntrospectionRule` instance.

        :returns: :class:`~.introspection_rule.IntrospectionRule` instance.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            introspection rule matching the name or ID could be found.
        """
        return self._get(
            _introspection_rule.IntrospectionRule,
            introspection_rule,
        )

    def introspection_rules(self, **query):
        """Retrieve a generator of introspection rules.

        :param dict query: Optional query parameters to be sent to restrict
            the records to be returned. Available parameters include:

            * ``uuid``: The UUID of the Ironic Inspector rule.
            * ``limit``: List of a logic statementd or operations in rules,
                         that can be evaluated as True or False.
            * ``actions``: List of operations that will be performed
                           if conditions of this rule are fulfilled.
            * ``description``: Rule human-readable description.
            * ``scope``: Scope of an introspection rule. If set, the rule
                         is only applied to nodes that have
                         matching inspection_scope property.

        :returns: A generator of
            :class:`~.introspection_rule.IntrospectionRule`
            objects
        """
        return self._list(_introspection_rule.IntrospectionRule, **query)

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
