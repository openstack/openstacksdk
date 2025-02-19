# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing as ty

from openstack import exceptions
from openstack.instance_ha.v1 import host as _host
from openstack.instance_ha.v1 import notification as _notification
from openstack.instance_ha.v1 import segment as _segment
from openstack.instance_ha.v1 import vmove as _vmove
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    """Proxy class for ha resource handling.

    Create method for each action of each API.
    """

    _resource_registry = {
        "host": _host.Host,
        "notification": _notification.Notification,
        "segment": _segment.Segment,
        "vmove": _vmove.VMove,
    }

    def notifications(self, **query):
        """Return a generator of notifications.

        :param kwargs query: Optional query parameters to be sent to
            limit the notifications being returned.
        :returns: A generator of notifications
        """
        return self._list(_notification.Notification, **query)

    def get_notification(self, notification):
        """Get a single notification.

        :param notification: The value can be the ID of a notification or a
            :class:`~masakariclient.sdk.ha.v1.notification.Notification`
            instance.
        :returns: One
            :class:`~masakariclient.sdk.ha.v1.notification.Notification`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_notification.Notification, notification)

    def create_notification(self, **attrs):
        """Create a new notification.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`masakariclient.sdk.ha.v1.notification.Notification`,
            comprised of the propoerties on the Notification class.
        :returns: The result of notification creation
        :rtype: :class:`masakariclient.sdk.ha.v1.notification.Notification`
        """
        return self._create(_notification.Notification, **attrs)

    def segments(self, **query):
        """Return a generator of segments.

        :param kwargs query: Optional query parameters to be sent to
            limit the segments being returned.
        :returns: A generator of segments
        """
        return self._list(_segment.Segment, **query)

    def get_segment(self, segment):
        """Get a single segment.

        :param segment: The value can be the ID of a segment or a
            :class:`~masakariclient.sdk.ha.v1.segment.Segment` instance.
        :returns: One :class:`~masakariclient.sdk.ha.v1.segment.Segment`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_segment.Segment, segment)

    def create_segment(self, **attrs):
        """Create a new segment.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`masakariclient.sdk.ha.v1.segment.Segment`,
            comprised of the propoerties on the Segment class.
        :returns: The result of segment creation
        :rtype: :class:`masakariclient.sdk.ha.v1.segment.Segment`
        """
        return self._create(_segment.Segment, **attrs)

    def update_segment(self, segment, **attrs):
        """Update a segment.

        :param segment: The value can be the ID of a segment or a
            :class:`~masakariclient.sdk.ha.v1.segment.Segment` instance.
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`masakariclient.sdk.ha.v1.segment.Segment`,
            comprised of the propoerties on the Segment class.
        :returns: The updated segment.
        :rtype: :class:`masakariclient.sdk.ha.v1.segment.Segment`
        """
        return self._update(_segment.Segment, segment, **attrs)

    def delete_segment(self, segment, ignore_missing=True):
        """Delete a segment.

        :param segment:
            The value can be either the ID of a segment or a
            :class:`~masakariclient.sdk.ha.v1.segment.Segment` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the segment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent segment.
        :returns: ``None``
        """
        return self._delete(
            _segment.Segment, segment, ignore_missing=ignore_missing
        )

    def hosts(self, segment_id, **query):
        """Return a generator of hosts.

        :param segment_id: The ID of a failover segment.
        :param kwargs query: Optional query parameters to be sent to
            limit the hosts being returned.

        :returns: A generator of hosts
        """
        return self._list(_host.Host, segment_id=segment_id, **query)

    def create_host(self, segment_id, **attrs):
        """Create a new host.

        :param segment_id: The ID of a failover segment.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`masakariclient.sdk.ha.v1.host.Host`,
            comprised of the propoerties on the Host class.

        :returns: The results of host creation
        """
        return self._create(_host.Host, segment_id=segment_id, **attrs)

    def get_host(self, host, segment_id=None):
        """Get a single host.

        :param segment_id: The ID of a failover segment.
        :param host: The value can be the ID of a host or a :class:
            `~masakariclient.sdk.ha.v1.host.Host` instance.

        :returns: One :class:`~masakariclient.sdk.ha.v1.host.Host`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.InvalidRequest`
            when segment_id is None.
        """
        if segment_id is None:
            raise exceptions.InvalidRequest("'segment_id' must be specified.")

        host_id = resource.Resource._get_id(host)
        return self._get(_host.Host, host_id, segment_id=segment_id)

    def update_host(self, host, segment_id, **attrs):
        """Update the host.

        :param segment_id: The ID of a failover segment.
        :param host: The value can be the ID of a host or a :class:
            `~masakariclient.sdk.ha.v1.host.Host` instance.
        :param dict attrs: The attributes to update on the host represented.

        :returns: The updated host
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.InvalidRequest`
            when segment_id is None.
        """
        host_id = resource.Resource._get_id(host)
        return self._update(
            _host.Host, host_id, segment_id=segment_id, **attrs
        )

    def delete_host(self, host, segment_id=None, ignore_missing=True):
        """Delete the host.

        :param segment_id: The ID of a failover segment.
        :param host: The value can be the ID of a host or a :class:
            `~masakariclient.sdk.ha.v1.host.Host` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the host does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent host.

        :returns: ``None``
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.InvalidRequest`
            when segment_id is None.

        """
        if segment_id is None:
            raise exceptions.InvalidRequest("'segment_id' must be specified.")

        host_id = resource.Resource._get_id(host)
        return self._delete(
            _host.Host,
            host_id,
            segment_id=segment_id,
            ignore_missing=ignore_missing,
        )

    def vmoves(self, notification, **query):
        """Return a generator of vmoves.

        :param notification: The value can be the UUID of a notification or
            a :class: `~masakariclient.sdk.ha.v1.notification.Notification`
            instance.
        :param kwargs query: Optional query parameters to be sent to
            limit the vmoves being returned.

        :returns: A generator of vmoves
        """
        notification_id = resource.Resource._get_id(notification)
        return self._list(
            _vmove.VMove,
            notification_id=notification_id,
            **query,
        )

    def get_vmove(self, vmove, notification):
        """Get a single vmove.

        :param vmove: The value can be the UUID of one vmove or
            a :class: `~masakariclient.sdk.ha.v1.vmove.VMove` instance.
        :param notification: The value can be the UUID of a notification or
            a :class: `~masakariclient.sdk.ha.v1.notification.Notification`
            instance.
        :returns: one 'VMove' resource class.
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.InvalidRequest`
            when notification_id is None.
        """
        notification_id = resource.Resource._get_id(notification)
        vmove_id = resource.Resource._get_id(vmove)
        return self._get(
            _vmove.VMove,
            vmove_id,
            notification_id=notification_id,
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
