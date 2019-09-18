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
from openstack.baremetal.v1 import node as _node
from openstack.baremetal_introspection.v1 import introspection as _introspect
from openstack import exceptions
from openstack import proxy


_logger = _log.setup_logging('openstack')


class Proxy(proxy.Proxy):

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
        res = _introspect.Introspection.new(connection=self._get_connection(),
                                            id=node.id)
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
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            introspection matching the name or ID could be found.
        """
        return self._get(_introspect.Introspection, introspection)

    def get_introspection_data(self, introspection):
        """Get introspection data.

        :param introspection: The value can be the name or ID of an
            introspection (matching bare metal node name or ID) or
            an :class:`~.introspection.Introspection` instance.
        :returns: introspection data from the most recent successful run.
        :rtype: dict
        """
        res = self._get_resource(_introspect.Introspection, introspection)
        return res.get_data(self)

    def abort_introspection(self, introspection, ignore_missing=True):
        """Abort an introspection.

        Note that the introspection is not aborted immediately, you may use
        `wait_for_introspection` with `ignore_error=True`.

        :param introspection: The value can be the name or ID of an
            introspection (matching bare metal node name or ID) or
            an :class:`~.introspection.Introspection` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the introspection could not be found. When set to ``True``, no
            exception will be raised when attempting to abort a non-existent
            introspection.
        :returns: nothing
        """
        res = self._get_resource(_introspect.Introspection, introspection)
        try:
            res.abort(self)
        except exceptions.ResourceNotFound:
            if not ignore_missing:
                raise

    def wait_for_introspection(self, introspection, timeout=None,
                               ignore_error=False):
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
