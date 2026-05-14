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

from collections.abc import Callable, Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    overload,
)

from openstack._utils import renamed_param
from openstack import exceptions
from openstack import proxy
from openstack import resource
from openstack.shared_file_system.v2 import (
    availability_zone as _availability_zone,
)
from openstack.shared_file_system.v2 import limit as _limit
from openstack.shared_file_system.v2 import quota_class_set as _quota_class_set
from openstack.shared_file_system.v2 import resource_locks as _resource_locks
from openstack.shared_file_system.v2 import share as _share
from openstack.shared_file_system.v2 import share_group as _share_group
from openstack.shared_file_system.v2 import (
    share_group_snapshot as _share_group_snapshot,
)
from openstack.shared_file_system.v2 import (
    share_access_rule as _share_access_rule,
)
from openstack.shared_file_system.v2 import (
    share_export_locations as _share_export_locations,
)
from openstack.shared_file_system.v2 import share_instance as _share_instance
from openstack.shared_file_system.v2 import share_network as _share_network
from openstack.shared_file_system.v2 import (
    share_network_subnet as _share_network_subnet,
)
from openstack.shared_file_system.v2 import share_snapshot as _share_snapshot
from openstack.shared_file_system.v2 import (
    share_snapshot_instance as _share_snapshot_instance,
)
from openstack.shared_file_system.v2 import storage_pool as _storage_pool
from openstack.shared_file_system.v2 import user_message as _user_message

if TYPE_CHECKING:
    import requests


class Proxy(proxy.Proxy):
    api_version: ClassVar[Literal['2']] = '2'

    _resource_registry = {
        "availability_zone": _availability_zone.AvailabilityZone,
        "share_snapshot": _share_snapshot.ShareSnapshot,
        "storage_pool": _storage_pool.StoragePool,
        "user_message": _user_message.UserMessage,
        "limit": _limit.Limit,
        "share": _share.Share,
        "share_network": _share_network.ShareNetwork,
        "share_network_subnet": _share_network_subnet.ShareNetworkSubnet,
        "share_snapshot_instance": _share_snapshot_instance.ShareSnapshotInstance,  # noqa: E501
        "share_instance": _share_instance.ShareInstance,
        "share_export_locations": _share_export_locations.ShareExportLocation,
        "share_access_rule": _share_access_rule.ShareAccessRule,
        "share_group": _share_group.ShareGroup,
        "share_group_snapshot": _share_group_snapshot.ShareGroupSnapshot,
        "resource_locks": _resource_locks.ResourceLock,
        "quota_class_set": _quota_class_set.QuotaClassSet,
    }

    def availability_zones(self):
        """Retrieve shared file system availability zones

        :returns: A generator of availability zone resources
        """
        return self._list(_availability_zone.AvailabilityZone)

    def shares(self, details=True, **query):
        """Lists all shares with details

        :param query: Optional query parameters to be sent to limit
            the shares being returned.  Available parameters include:

            * status: Filters by a share status
            * share_server_id: The UUID of the share server.
            * metadata: One or more metadata key and value pairs as a url
              encoded dictionary of strings.
            * extra_specs: The extra specifications as a set of one or more
              key-value pairs.
            * share_type_id: The UUID of a share type to query resources by.
            * name: The user defined name of the resource to filter resources
              by.
            * snapshot_id: The UUID of the share's base snapshot to filter
              the request based on.
            * host: The host name of the resource to query with.
            * share_network_id: The UUID of the share network to filter
              resources by.
            * project_id: The ID of the project that owns the resource.
            * is_public: A boolean query parameter that, when set to true,
              allows retrieving public resources that belong to
              all projects.
            * share_group_id: The UUID of a share group to filter resource.
            * export_location_id: The export location UUID that can be used
              to filter shares or share instances.
            * export_location_path: The export location path that can be used
              to filter shares or share instances.
            * name~: The name pattern that can be used to filter shares, share
              snapshots, share networks or share groups.
            * description~: The description pattern that can be used to filter
              shares, share snapshots, share networks or share groups.
            * with_count: Whether to show count in API response or not,
              default is False.
            * limit: The maximum number of shares to return.
            * offset: The offset to define start point of share or share group
              listing.
            * sort_key: The key to sort a list of shares.
            * sort_dir: The direction to sort a list of shares. A valid value
              is asc, or desc.

        :returns: Details of shares resources
        """
        base_path = '/shares/detail' if details else None
        return self._list(_share.Share, base_path=base_path, **query)

    @overload
    def find_share(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        **query: Any,
    ) -> _share.Share: ...

    @overload
    def find_share(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _share.Share | None: ...

    def find_share(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _share.Share | None:
        """Find a single share

        :param name_or_id: The name or ID of a share.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param query: Any additional parameters to be passed into
            underlying methods. such as query filters.

        :returns: One :class:`~openstack.shared_file_system.v2.share.Share`
                  or None
        """

        return self._find(
            _share.Share, name_or_id, ignore_missing=ignore_missing, **query
        )

    @renamed_param('share_id', 'share')
    def get_share(self, share: str | _share.Share) -> _share.Share:
        """Lists details of a single share

        :param share: The value can be the ID of a share or a
            :class:`~openstack.shared_file_system.v2.share.Share` instance.
        :returns: Details of the identified share
        """
        return self._get(_share.Share, share)

    def delete_share(
        self, share: str | _share.Share, ignore_missing: bool = True
    ) -> None:
        """Deletes a single share

        :param share: The value can be either the ID of a share or a
            :class:`~openstack.shared_file_system.v2.share.Share` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent share.

        :returns: ``None``
        """
        self._delete(_share.Share, share, ignore_missing=ignore_missing)

    @renamed_param('share_id', 'share')
    def update_share(self, share, **attrs):
        """Updates details of a single share.

        :param share: The ID of the share to update
        :param attrs: The attributes to update on the share
        :returns: the updated share
        """
        return self._update(_share.Share, share, **attrs)

    def create_share(self, **attrs: Any) -> _share.Share:
        """Creates a share from attributes

        :param attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.shares.Shares`,
            comprised of the properties on the Shares class. 'size' and 'share'
            are required to create a share.
        :returns: Details of the new share
        """
        return self._create(_share.Share, **attrs)

    @renamed_param('snapshot_id', 'snapshot')
    @renamed_param('share_id', 'share')
    def revert_share_to_snapshot(self, share, snapshot):
        """Reverts a share to the specified snapshot, which must be
            the most recent one known to manila.

        :param share: The ID of the share to revert
        :param snapshot: The ID of the snapshot to revert to
        :returns: Result of the ``revert``
        """
        res = self._get(_share.Share, share)
        snapshot_id = resource.Resource._get_id(snapshot)
        res.revert_to_snapshot(self, snapshot_id)

    def manage_share(self, protocol, export_path, service_host, **params):
        """Manage a share.

        :param protocol: The shared file systems protocol of this share.
        :param export_path: The export path formatted according to the
            protocol.
        :param service_host: The manage-share service host.
        :param params: Optional parameters to be sent. Available
            parameters include:

            * name: The user defined name of the resource.
            * share_type: The name or ID of the share type to be used to create
              the resource.
            * driver_options: A set of one or more key and value pairs, as a
              dictionary of strings, that describe driver options.
            * is_public: The level of visibility for the share.
            * description: The user defiend description of the resource.
            * share_server_id: The UUID of the share server.

        :returns: The share that was managed.
        """

        share = _share.Share()
        return share.manage(
            self, protocol, export_path, service_host, **params
        )

    @renamed_param('share_id', 'share')
    def unmanage_share(self, share):
        """Unmanage the share with the given share ID.

        :param share: The ID of the share to unmanage.
        :returns: ``None``
        """
        res = self._get(_share.Share, share)
        res.unmanage(self)

    @renamed_param('share_id', 'share')
    def resize_share(
        self, share, new_size, no_shrink=False, no_extend=False, force=False
    ):
        """Resizes a share, extending/shrinking the share as needed.

        :param share: The ID of the share to resize
        :param new_size: The new size of the share in GiBs. If new_size is
            the same as the current size, then nothing is done.
        :param no_shrink: If set to True, the given share is not shrunk,
            even if shrinking the share is required to get the share to the
            given size. This could be useful for extending shares to a minimum
            size, while not shrinking shares to the given size. This defaults
            to False.
        :param no_extend: If set to True, the given share is not
            extended, even if extending the share is required to get the share
            to the given size. This could be useful for shrinking shares to a
            maximum size, while not extending smaller shares to that maximum
            size. This defaults to False.
        :param force: Whether or not force should be used,
            in the case where the share should be extended.
        :returns: ``None``
        """

        res = self._get(_share.Share, share)

        if new_size > res.size and no_extend is not True:
            res.extend_share(self, new_size, force)
        elif new_size < res.size and no_shrink is not True:
            res.shrink_share(self, new_size)

    def share_groups(self, **query):
        """Lists all share groups.

        :param query: Optional query parameters to be sent to limit
            the share groups being returned.  Available parameters include:

            * status: Filters by a share group status.
            * name: The user defined name of the resource to filter resources
              by.
            * description: The user defined description text that can be used
              to filter resources.
            * project_id: The project ID of the user or service.
            * share_server_id: The UUID of the share server.
            * snapshot_id: The UUID of the share's base snapshot to filter
              the request based on.
            * host: The host name for the back end.
            * share_network_id: The UUID of the share network to filter
              resources by.
            * share_group_type_id: The share group type ID to filter
              share groups.
            * share_group_snapshot_id: The source share group snapshot ID to
              list the share group.
            * share_types: A list of one or more share type IDs. Allows
              filtering share groups.
            * limit: The maximum number of share groups members to return.
            * offset: The offset to define start point of share or share
              group listing.
            * sort_key: The key to sort a list of shares.
            * sort_dir: The direction to sort a list of shares
            * name~: The name pattern that can be used to filter shares,
              share snapshots, share networks or share groups.
            * description~: The description pattern that can be used to
              filter shares, share snapshots, share networks or share groups.

        :returns: A generator of manila share group resources
        """
        return self._list(_share_group.ShareGroup, **query)

    @renamed_param('share_group_id', 'share_group')
    def get_share_group(
        self, share_group: str | _share_group.ShareGroup
    ) -> _share_group.ShareGroup:
        """Lists details for a share group.

        :param share_group: The value can be the ID of a share group or a
            :class:`~openstack.shared_file_system.v2.share_group.ShareGroup`
            instance.
        :returns: Details of the identified share group
        """
        return self._get(_share_group.ShareGroup, share_group)

    @overload
    def find_share_group(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _share_group.ShareGroup: ...

    @overload
    def find_share_group(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _share_group.ShareGroup | None: ...

    def find_share_group(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _share_group.ShareGroup | None:
        """Finds a single share group

        :param name_or_id: The name or ID of a share group.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One
            :class:`~openstack.shared_file_system.v2.share_group.ShareGroup` or
            None
        """
        return self._find(
            _share_group.ShareGroup, name_or_id, ignore_missing=ignore_missing
        )

    def create_share_group(self, **attrs: Any) -> _share_group.ShareGroup:
        """Creates a share group from attributes

        :returns: Details of the new share group
        """
        return self._create(_share_group.ShareGroup, **attrs)

    @renamed_param('share_group_id', 'share_group')
    def update_share_group(self, share_group, **attrs):
        """Updates details of a single share group

        :param share_group: The ID of the share group
        :returns: Updated details of the identified share group
        """
        return self._update(_share_group.ShareGroup, share_group, **attrs)

    @renamed_param('share_group_id', 'share_group')
    def delete_share_group(
        self,
        share_group: str | _share_group.ShareGroup,
        ignore_missing: bool = True,
    ) -> _share_group.ShareGroup | None:
        """Deletes a single share group

        :param share_group: The value can be either the ID of a share group or
            a :class:`~openstack.shared_file_system.v2.share_group.ShareGroup`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share group does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            share group.

        :returns: The deleted share group.
        """
        return self._delete(
            _share_group.ShareGroup,
            share_group,
            ignore_missing=ignore_missing,
        )

    def storage_pools(self, details=True, **query):
        """Lists all back-end storage pools with details

        :param query: Optional query parameters to be sent to limit
            the storage pools being returned. Available parameters include:

            * pool_name: The pool name for the back end.
            * host_name: The host name for the back end.
            * backend_name: The name of the back end.
            * capabilities: The capabilities for the storage back end.
            * share_type: The share type name or UUID.
        :returns: A generator of manila storage pool resources
        """
        base_path = '/scheduler-stats/pools/detail' if details else None
        return self._list(
            _storage_pool.StoragePool, base_path=base_path, **query
        )

    def user_messages(self, **query):
        """List shared file system user messages

        :param query: Optional query parameters to be sent to limit
            the messages being returned. Available parameters include:

            * action_id: The ID of the action during which the message
              was created.
            * detail_id: The ID of the message detail.
            * limit: The maximum number of shares to return.
            * message_level: The message level.
            * offset: The offset to define start point of share or share
              group listing.
            * sort_key: The key to sort a list of messages.
            * sort_dir: The direction to sort a list of shares.
            * project_id: The ID of the project for which the message
              was created.
            * request_id: The ID of the request during which the message
              was created.
            * resource_id: The UUID of the resource for which the message
              was created.
            * resource_type: The type of the resource for which the message
              was created.

        :returns: A generator of user message resources
        """
        return self._list(_user_message.UserMessage, **query)

    @renamed_param('message_id', 'message')
    def get_user_message(
        self, message: str | _user_message.UserMessage
    ) -> _user_message.UserMessage:
        """List details of a single user message

        :param message: The value can be the ID of a user message or a
            :class:`~openstack.shared_file_system.v2.user_message.UserMessage`
            instance.
        :returns: Details of the identified user message
        """
        return self._get(_user_message.UserMessage, message)

    # TODO(stephenfin): This method should return None
    @renamed_param('message_id', 'message')
    def delete_user_message(
        self,
        message: str | _user_message.UserMessage,
        ignore_missing: bool = True,
    ) -> _user_message.UserMessage | None:
        """Deletes a single user message

        :param message: The value can be either the ID of a user message or a
            :class:`~openstack.shared_file_system.v2.user_message.UserMessage`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the user message does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent user
            message.

        :returns: The deleted user message.
        """
        return self._delete(
            _user_message.UserMessage,
            message,
            ignore_missing=ignore_missing,
        )

    def limits(self, **query):
        """Lists all share limits.

        :param query: Optional query parameters to be sent to limit
            the share limits being returned.

        :returns: A generator of manila share limits resources
        """
        return self._list(_limit.Limit, **query)

    def share_snapshots(self, details=True, **query):
        """Lists all share snapshots with details.

        :param query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * project_id: The ID of the user or service making the API request.

        :returns: A generator of manila share snapshot resources
        """
        base_path = '/snapshots/detail' if details else None
        return self._list(
            _share_snapshot.ShareSnapshot, base_path=base_path, **query
        )

    @renamed_param('snapshot_id', 'snapshot')
    def get_share_snapshot(
        self, snapshot: str | _share_snapshot.ShareSnapshot
    ) -> _share_snapshot.ShareSnapshot:
        """Lists details of a single share snapshot

        :param snapshot: The value can be the ID of a share snapshot or a
            :class:`~openstack.shared_file_system.v2.share_snapshot.ShareSnapshot`
            instance.
        :returns: Details of the identified share snapshot
        """
        return self._get(_share_snapshot.ShareSnapshot, snapshot)

    def create_share_snapshot(
        self, **attrs: Any
    ) -> _share_snapshot.ShareSnapshot:
        """Creates a share snapshot from attributes

        :returns: Details of the new share snapshot
        """
        return self._create(_share_snapshot.ShareSnapshot, **attrs)

    @renamed_param('snapshot_id', 'snapshot')
    def update_share_snapshot(self, snapshot, **attrs):
        """Updates details of a single share.

        :param snapshot: The ID of the snapshot to update
        :param attrs: The attributes to update on the snapshot
        :returns: the updated share snapshot
        """
        return self._update(_share_snapshot.ShareSnapshot, snapshot, **attrs)

    @renamed_param('snapshot_id', 'snapshot')
    def delete_share_snapshot(
        self,
        snapshot: str | _share_snapshot.ShareSnapshot,
        ignore_missing: bool = True,
    ) -> None:
        """Deletes a single share snapshot

        :param snapshot: The value can be either the ID of a share snapshot or
            a
            :class:`~openstack.shared_file_system.v2.share_snapshot.ShareSnapshot`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share snapshot does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent share
            snapshot.

        :returns: ``None``
        """
        self._delete(
            _share_snapshot.ShareSnapshot,
            snapshot,
            ignore_missing=ignore_missing,
        )

    # ========= Network Subnets ==========
    @renamed_param('share_network_id', 'share_network')
    def share_network_subnets(self, share_network):
        """Lists all share network subnets with details.

        :param share_network: The id of the share network for which
            Share Network Subnets should be listed.
        :returns: A generator of manila share network subnets
        """
        share_network_id = resource.Resource._get_id(share_network)
        return self._list(
            _share_network_subnet.ShareNetworkSubnet,
            share_network_id=share_network_id,
        )

    @renamed_param('share_network_id', 'share_network')
    @renamed_param('share_network_subnet_id', 'share_network_subnet')
    def get_share_network_subnet(
        self,
        share_network: str | _share_network.ShareNetwork,
        share_network_subnet: (str | _share_network_subnet.ShareNetworkSubnet),
    ) -> _share_network_subnet.ShareNetworkSubnet:
        """Lists details of a single share network subnet.

        :param share_network: The value can be the ID of a share network or a
            :class:`~openstack.shared_file_system.v2.share_network.ShareNetwork`
            instance.
        :param share_network_subnet: The value can be the ID of a share network
            subnet or a
            :class:`~openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet`
            instance.
        :returns: Details of the identified share network subnet
        """
        share_network_id = resource.Resource._get_id(share_network)
        return self._get(
            _share_network_subnet.ShareNetworkSubnet,
            share_network_subnet,
            share_network_id=share_network_id,
        )

    @renamed_param('share_network_id', 'share_network')
    def create_share_network_subnet(
        self, share_network: str | _share_network.ShareNetwork, **attrs: Any
    ) -> _share_network_subnet.ShareNetworkSubnet:
        """Creates a share network subnet from attributes

        :param share_network: The id of the share network wthin which the
            the Share Network Subnet should be created.
        :param attrs: Attributes which will be used to create
            a share network subnet.
        :returns: Details of the new share network subnet.
        """
        share_network_id = resource.Resource._get_id(share_network)
        return self._create(
            _share_network_subnet.ShareNetworkSubnet,
            **attrs,
            share_network_id=share_network_id,
        )

    @renamed_param('share_network_id', 'share_network')
    def delete_share_network_subnet(
        self,
        share_network: str | _share_network.ShareNetwork,
        share_network_subnet: str | _share_network_subnet.ShareNetworkSubnet,
        ignore_missing: bool = True,
    ) -> None:
        """Deletes a share network subnet.

        :param share_network: The value can be either the ID of a share network
            or a
            :class:`~openstack.shared_file_system.v2.share_network.ShareNetwork`
            instance.
        :param share_network_subnet: The value can be either the ID of a share
            network subnet or a
            :class:`~openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share network subnet does not exist. When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            share network subnet.

        :returns: ``None``
        """
        share_network_id = resource.Resource._get_id(share_network)
        self._delete(
            _share_network_subnet.ShareNetworkSubnet,
            share_network_subnet,
            share_network_id=share_network_id,
            ignore_missing=ignore_missing,
        )

    def share_snapshot_instances(self, details=True, **query):
        """Lists all share snapshot instances with details.

        :param details: Whether to fetch detailed resource
            descriptions. Defaults to True.
        :param query: Optional query parameters to be sent to limit
            the share snapshot instance being returned. Available parameters
            include:

            * snapshot_id: The UUID of the share's base snapshot to filter
                the request based on.
            * project_id: The project ID of the user or service making the
                request.

        :returns: A generator of share snapshot instance resources
        """
        base_path = '/snapshot-instances/detail' if details else None
        return self._list(
            _share_snapshot_instance.ShareSnapshotInstance,
            base_path=base_path,
            **query,
        )

    @renamed_param('snapshot_instance_id', 'snapshot_instance')
    def get_share_snapshot_instance(
        self,
        share_snapshot_instance: (
            str | _share_snapshot_instance.ShareSnapshotInstance
        ),
    ) -> _share_snapshot_instance.ShareSnapshotInstance:
        """Lists details of a single share snapshot instance

        :param share_snapshot_instance: The value can be the ID of a share
            snapshot instance or a
            :class:`~openstack.shared_file_system.v2.share_snapshot_instance.ShareSnapshotInstance`
            instance.
        :returns: Details of the identified snapshot instance
        """
        return self._get(
            _share_snapshot_instance.ShareSnapshotInstance,
            share_snapshot_instance,
        )

    def share_networks(self, details=True, **query):
        """Lists all share networks with details.

        :param query: Optional query parameters to be sent to limit the
            resources being returned. Available parameters include:

            * name~: The user defined name of the resource to filter resources
              by.
            * project_id: The ID of the user or service making the request.
            * description~: The description pattern that can be used to filter
              shares, share snapshots, share networks or share groups.
            * all_projects: (Admin only). Defines whether to list the requested
              resources for all projects.

        :returns: Details of shares networks
        """
        base_path = '/share-networks/detail' if details else None
        return self._list(
            _share_network.ShareNetwork, base_path=base_path, **query
        )

    @renamed_param('share_network_id', 'share_network')
    def get_share_network(
        self, share_network: str | _share_network.ShareNetwork
    ) -> _share_network.ShareNetwork:
        """Lists details of a single share network

        :param share_network: The value can be the ID of a share network or a
            :class:`~openstack.shared_file_system.v2.share_network.ShareNetwork`
            instance.
        :returns: Details of the identified share network
        """
        return self._get(_share_network.ShareNetwork, share_network)

    @renamed_param('share_network_id', 'share_network')
    def delete_share_network(
        self,
        share_network: str | _share_network.ShareNetwork,
        ignore_missing: bool = True,
    ) -> None:
        """Deletes a single share network

        :param share_network: The value can be either the ID of a share network
            or a
            :class:`~openstack.shared_file_system.v2.share_network.ShareNetwork`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share network does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent share
            network.

        :returns: ``None``
        """
        self._delete(
            _share_network.ShareNetwork,
            share_network,
            ignore_missing=ignore_missing,
        )

    @renamed_param('share_network_id', 'share_network')
    def update_share_network(self, share_network, **attrs):
        """Updates details of a single share network.

        :param share_network: The ID of the share network to update
        :param attrs: The attributes to update on the share network
        :returns: the updated share network
        """
        return self._update(
            _share_network.ShareNetwork, share_network, **attrs
        )

    def create_share_network(
        self, **attrs: Any
    ) -> _share_network.ShareNetwork:
        """Creates a share network from attributes

        :returns: Details of the new share network
        :param attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            share_network.ShareNetwork`,comprised of the properties
            on the ShareNetwork class.
        """
        return self._create(_share_network.ShareNetwork, **attrs)

    def share_instances(self, **query):
        """Lists all share instances.

        :param query: Optional query parameters to be sent to limit
            the share instances being returned. Available parameters include:

            * export_location_id: The export location UUID that can be used
              to filter share instances.
            * export_location_path: The export location path that can be used
              to filter share instances.

        :returns: Details of share instances resources
        """
        return self._list(_share_instance.ShareInstance, **query)

    @renamed_param('share_instance_id', 'share_instance')
    def get_share_instance(
        self, share_instance: str | _share_instance.ShareInstance
    ) -> _share_instance.ShareInstance:
        """Shows details for a single share instance

        :param share_instance: The value can be the UUID of a share instance
            or a
            :class:`~openstack.shared_file_system.v2.share_instance.ShareInstance`
            instance.

        :returns: Details of the identified share instance
        """
        return self._get(_share_instance.ShareInstance, share_instance)

    @renamed_param('share_instance_id', 'share_instance')
    def reset_share_instance_status(self, share_instance, status):
        """Explicitly updates the state of a share instance.

        :param share_instance: The UUID of the share instance to reset.
        :param status: The share or share instance status to be set.

        :returns: ``None``
        """
        res = self._get_resource(_share_instance.ShareInstance, share_instance)
        res.reset_status(self, status)

    @renamed_param('share_instance_id', 'share_instance')
    def delete_share_instance(
        self,
        share_instance: str | _share_instance.ShareInstance,
        ignore_missing: bool = True,
    ) -> None:
        """Force-deletes a share instance

        :param share_instance: The value can be either the ID of a share
            instance or a
            :class:`~openstack.shared_file_system.v2.share_instance.ShareInstance`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share instance does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent share
            instance.

        :returns: ``None``
        """
        res = self._get_resource(_share_instance.ShareInstance, share_instance)
        try:
            res.force_delete(self)
        except exceptions.NotFoundException:
            if not ignore_missing:
                raise

    @renamed_param('share_id', 'share')
    def export_locations(self, share):
        """List all export locations with details

        :param share: The ID of the share to list export locations from
        :returns: List of export locations
        """
        share_id = resource.Resource._get_id(share)
        return self._list(
            _share_export_locations.ShareExportLocation, share_id=share_id
        )

    @renamed_param('share_id', 'share')
    def get_export_location(
        self,
        export_location: str | _share_export_locations.ShareExportLocation,
        share: str | _share.Share,
    ) -> _share_export_locations.ShareExportLocation:
        """List details of export location

        :param export_location: The export location resource to get
        :param share: The ID of the share to get export locations from
        :returns: Details of identified export location
        """
        export_location_id = resource.Resource._get_id(export_location)
        share_id = resource.Resource._get_id(share)
        return self._get(
            _share_export_locations.ShareExportLocation,
            export_location_id,
            share_id=share_id,
        )

    def access_rules(self, share, **query):
        """Lists the access rules on a share.

        :returns: A generator of the share access rules.
        """
        share = self._get_resource(_share.Share, share)
        return self._list(
            _share_access_rule.ShareAccessRule, share_id=share.id, **query
        )

    @renamed_param('access_id', 'access')
    def get_access_rule(
        self, access_rule: str | _share_access_rule.ShareAccessRule
    ) -> _share_access_rule.ShareAccessRule:
        """List details of an access rule.

        :param access_rule: The value can be the ID of an access rule or a
            :class:`~openstack.shared_file_system.v2.share_access_rule.ShareAccessRule`
            instance.
        :returns: Details of the identified access rule.
        """
        return self._get(_share_access_rule.ShareAccessRule, access_rule)

    @renamed_param('share_id', 'share')
    def create_access_rule(
        self, share: str | _share.Share, **attrs: Any
    ) -> _share_access_rule.ShareAccessRule:
        """Creates an access rule from attributes

        :param share: The ID of the share
        :param attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            share_access_rules.ShareAccessRules`, comprised of the
            properties on the ShareAccessRules class.
        :returns: Details of the new access rule
        """
        # TODO(stephenfin): This should be handled via ShareAccessRule.create
        share_id = resource.Resource._get_id(share)
        base_path = f"/shares/{share_id}/action"
        return self._create(
            _share_access_rule.ShareAccessRule, base_path=base_path, **attrs
        )

    # TODO(stephenfin): This method should return None
    @renamed_param('access_id', 'access')
    @renamed_param('share_id', 'share')
    def delete_access_rule(
        self,
        access_rule: str | _share_access_rule.ShareAccessRule,
        share: str | _share.Share,
        ignore_missing: bool = True,
        *,
        unrestrict: bool = False,
    ) -> 'requests.Response | None':
        """Deletes an access rule

        :param access_rule: The value can be either the ID of an access rule
            or a
            :class:`~openstack.shared_file_system.v2.share_access_rule.ShareAccessRule`
            instance.
        :param share: The ID of the share.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the access rule does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            access rule.
        :param unrestrict: If Manila must attempt removing locks while
            deleting.

        :returns: ``requests.models.Response`` HTTP response from internal
            requests client
        """
        share_id = resource.Resource._get_id(share)
        res = self._get_resource(
            _share_access_rule.ShareAccessRule,
            access_rule,
            share_id=share_id,
        )
        try:
            return res.delete(
                self,
                unrestrict=unrestrict,
            )
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

    def share_group_snapshots(self, details=True, **query):
        """Lists all share group snapshots.

        :param query: Optional query parameters to be sent
            to limit the share group snapshots being returned.
            Available parameters include:

            * project_id: The ID of the project that owns the resource.
            * name: The user defined name of the resource to filter resources.
            * description: The user defined description text that can be used
              to filter resources.
            * status: Filters by a share status
            * share_group_id: The UUID of a share group to filter resource.
            * limit: The maximum number of share group snapshot members
              to return.
            * offset: The offset to define start point of share or
              share group listing.
            * sort_key: The key to sort a list of shares.
            * sort_dir: The direction to sort a list of shares. A valid
              value is asc, or desc.

        :returns: Details of share group snapshots resources
        """
        base_path = '/share-group-snapshots/detail' if details else None
        return self._list(
            _share_group_snapshot.ShareGroupSnapshot,
            base_path=base_path,
            **query,
        )

    @renamed_param('group_snapshot_id', 'group_snapshot')
    def share_group_snapshot_members(self, group_snapshot):
        """Lists all share group snapshots members.

        :param group_snapshot: The ID of the group snapshot to get
        :returns: List of the share group snapshot members, which are
            share snapshots.
        """
        res = self._get(
            _share_group_snapshot.ShareGroupSnapshot,
            group_snapshot,
        )
        response = res.get_members(self)
        return response

    @renamed_param('group_snapshot_id', 'group_snapshot')
    def get_share_group_snapshot(
        self,
        group_snapshot: str | _share_group_snapshot.ShareGroupSnapshot,
    ) -> _share_group_snapshot.ShareGroupSnapshot:
        """Show share group snapshot details

        :param group_snapshot: The value can be the ID of a share group
            snapshot or a
            :class:`~openstack.shared_file_system.v2.share_group_snapshot.ShareGroupSnapshot`
            instance.
        :returns: Details of the group snapshot
        """
        return self._get(
            _share_group_snapshot.ShareGroupSnapshot, group_snapshot
        )

    @renamed_param('share_group_id', 'share_group')
    def create_share_group_snapshot(
        self, share_group: str | _share_group.ShareGroup, **attrs: Any
    ) -> _share_group_snapshot.ShareGroupSnapshot:
        """Creates a point-in-time snapshot copy of a share group.

        :param share_group: ID of the share group to have the snapshot
            taken.
        :param attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            share_group_snapshots.ShareGroupSnapshots`,
        :returns: Details of the new snapshot
        """
        share_group_id = resource.Resource._get_id(share_group)
        return self._create(
            _share_group_snapshot.ShareGroupSnapshot,
            share_group_id=share_group_id,
            **attrs,
        )

    @renamed_param('group_snapshot_id', 'group_snapshot')
    def reset_share_group_snapshot_status(self, group_snapshot, status):
        """Reset share group snapshot state.

        :param group_snapshot: The ID of the share group snapshot to reset
        :param status: The state of the share group snapshot to be set, A
            valid value is "creating", "error", "available", "deleting",
            "error_deleting".
        """
        res = self._get(
            _share_group_snapshot.ShareGroupSnapshot, group_snapshot
        )
        res.reset_status(self, status)

    @renamed_param('group_snapshot_id', 'group_snapshot')
    def update_share_group_snapshot(self, group_snapshot, **attrs):
        """Updates a share group snapshot.

        :param group_snapshot: The ID of the share group snapshot to update
        :param attrs: The attributes to update on the share group snapshot
        :returns: the updated share group snapshot
        """
        return self._update(
            _share_group_snapshot.ShareGroupSnapshot,
            group_snapshot,
            **attrs,
        )

    @renamed_param('group_snapshot_id', 'group_snapshot')
    def delete_share_group_snapshot(
        self,
        group_snapshot: str | _share_group_snapshot.ShareGroupSnapshot,
        ignore_missing: bool = True,
    ) -> None:
        """Deletes a share group snapshot.

        :param group_snapshot: The value can be either the ID of a share group
            snapshot or a
            :class:`~openstack.shared_file_system.v2.share_group_snapshot.ShareGroupSnapshot`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the share group snapshot does not exist. When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            share group snapshot.

        :returns: ``None``
        """
        self._delete(
            _share_group_snapshot.ShareGroupSnapshot,
            group_snapshot,
            ignore_missing=ignore_missing,
        )

    # ========= Share Metadata ==========

    # TODO(stephenfin): Rename to fetch_share_metadata
    @renamed_param('share_id', 'share')
    def get_share_metadata(self, share: str | _share.Share) -> _share.Share:
        """Lists all metadata for a share.

        :param share: The value can be the ID of a share or a
            :class:`~openstack.shared_file_system.v2.share.Share` instance.

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's metadata.
        """
        res = self._get_resource(_share.Share, share)
        return res.fetch_metadata(self)

    # TODO(stephenfin): Rename to fetch_share_metadata_item
    @renamed_param('share_id', 'share')
    def get_share_metadata_item(
        self, share: str | _share.Share, key: str
    ) -> _share.Share:
        """Retrieves a specific metadata item from a share by its key.

        :param share: The value can be the ID of a share or a
            :class:`~openstack.shared_file_system.v2.share.Share` instance.
        :param key: The key of the share metadata

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's metadata.
        """
        res = self._get_resource(_share.Share, share)
        return res.get_metadata_item(self, key)

    @renamed_param('share_id', 'share')
    def create_share_metadata(
        self, share: str | _share.Share, **metadata: Any
    ) -> _share.Share:
        """Creates share metadata as key-value pairs.

        :param share: The ID of the share
        :param metadata: The metadata to be created

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's metadata.
        """
        res = self._get_resource(_share.Share, share)
        return res.set_metadata(self, metadata=metadata)

    @renamed_param('share_id', 'share')
    def update_share_metadata(self, share, metadata, replace=False):
        """Updates metadata of given share.

        :param share: The ID of the share
        :param metadata: The metadata to be created
        :param replace: Boolean for whether the preexisting metadata
            should be replaced

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's updated metadata.
        """
        res = self._get_resource(_share.Share, share)
        return res.set_metadata(self, metadata=metadata, replace=replace)

    @renamed_param('share_id', 'share')
    def delete_share_metadata(
        self,
        share: str | _share.Share,
        keys: Iterable[str],
        ignore_missing: bool = True,
    ) -> None:
        """Deletes metadata for a share.

        :param share: The value can be either the ID of a share or a
            :class:`~openstack.shared_file_system.v2.share.Share` instance.
        :param keys: The list of share metadata keys to be deleted.
        :param ignore_missing: When set to ``True``, missing keys will be
            logged but not cause a failure. When set to ``False``, missing keys
            will be included in the failure list.

        :returns: None
        """
        res = self._get_resource(_share.Share, share)
        keys_failed_to_delete = []
        for key in keys:
            try:
                res.delete_metadata_item(self, key)
            except exceptions.NotFoundException:
                if not ignore_missing:
                    self._connection.log.info("Key %s not found.", key)
                    keys_failed_to_delete.append(key)
            except exceptions.ForbiddenException:
                self._connection.log.info("Key %s cannot be deleted.", key)
                keys_failed_to_delete.append(key)
            except exceptions.SDKException:
                self._connection.log.info("Failed to delete key %s.", key)
                keys_failed_to_delete.append(key)
        if keys_failed_to_delete:
            raise exceptions.SDKException(
                f"Some keys failed to be deleted {keys_failed_to_delete}"
            )

    def resource_locks(self, **query):
        """Lists all resource locks.

        :param query: Optional query parameters to be sent to limit
            the resource locks being returned.  Available parameters include:

            * project_id: The project ID of the user that the lock is
                created for.
            * user_id: The ID of a user to filter resource locks by.
            * all_projects: list locks from all projects (Admin Only)
            * resource_id: The ID of the resource that the locks pertain to
                filter resource locks by.
            * resource_action: The action prevented by the filtered resource
                locks.
            * resource_type: The type of the resource that the locks pertain
                to filter resource locks by.
            * lock_context: The lock creator's context to filter locks by.
            * lock_reason: The lock reason that can be used to filter resource
                locks. (Inexact search is also available with lock_reason~)
            * created_since: Search for the list of resources that were created
                after the specified date. The date is in 'yyyy-mm-dd' format.
            * created_before: Search for the list of resources that were
                created prior to the specified date. The date is in
                'yyyy-mm-dd' format.
            * limit: The maximum number of resource locks to return.
            * offset: The offset to define start point of resource lock
                listing.
            * sort_key: The key to sort a list of shares.
            * sort_dir: The direction to sort a list of shares
            * with_count: Whether to show count in API response or not,
                default is False. This query parameter is useful with
                pagination.

        :returns: A generator of manila resource locks
        """

        if query.get('resource_type'):
            # The _create method has a parameter named resource_type, which
            # refers to the type of resource to be created, so we need to avoid
            # a conflict of parameters we are sending to the method.
            query['__conflicting_attrs'] = {
                'resource_type': query.get('resource_type')
            }
            query.pop('resource_type')
        return self._list(_resource_locks.ResourceLock, **query)

    def get_resource_lock(
        self, resource_lock: str | _resource_locks.ResourceLock
    ) -> _resource_locks.ResourceLock:
        """Show details of a resource lock.

        :param resource_lock: The ID of a resource lock or a
            :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock` instance.
        :returns: Details of the identified resource lock.
        """
        return self._get(_resource_locks.ResourceLock, resource_lock)

    def update_resource_lock(self, resource_lock, **attrs):
        """Updates details of a single resource lock.

        :param resource_lock: The ID of a resource lock or a
            :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock` instance.
        :param attrs: The attributes to update on the resource lock
        :returns: the updated resource lock
        """
        return self._update(
            _resource_locks.ResourceLock, resource_lock, **attrs
        )

    # TODO(stephenfin): This method should return None
    def delete_resource_lock(
        self,
        resource_lock: str | _resource_locks.ResourceLock,
        ignore_missing: bool = True,
    ) -> _resource_locks.ResourceLock | None:
        """Deletes a single resource lock

        :param resource_lock: The ID of a resource lock or a
            :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource lock does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            resource lock.

        :returns: The deleted resource lock.
        """
        return self._delete(
            _resource_locks.ResourceLock,
            resource_lock,
            ignore_missing=ignore_missing,
        )

    def create_resource_lock(
        self, **attrs: Any
    ) -> _resource_locks.ResourceLock:
        """Locks a resource.

        :param attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock`, comprised of the properties
            on the ResourceLock class. Available parameters include:

            * ``resource_id``: ID of the resource to be locked.
            * ``resource_type``: type of the resource (share, access_rule).
            * ``resource_action``: action to be locked (delete, show).
            * ``lock_reason``: reason why you're locking the resource
                (Optional).
        :returns: Details of the lock
        """

        if attrs.get('resource_type'):
            # The _create method has a parameter named resource_type, which
            # refers to the type of resource to be created, so we need to avoid
            # a conflict of parameters we are sending to the method.
            attrs['__conflicting_attrs'] = {
                'resource_type': attrs.get('resource_type')
            }
            attrs.pop('resource_type')
        return self._create(_resource_locks.ResourceLock, **attrs)

    @renamed_param('quota_class_name', 'quota_class_set')
    def get_quota_class_set(
        self, quota_class_set: str | _quota_class_set.QuotaClassSet
    ) -> _quota_class_set.QuotaClassSet:
        """Get quota class set.

        :param quota_class_set: The name of the quota class or a
            :class:`~openstack.shared_file_system.v2.quota_class_set.QuotaClassSet`
            instance.
        :returns: A :class:`~openstack.shared_file_system.v2
            .quota_class_set.QuotaClassSet`
        """
        return self._get(_quota_class_set.QuotaClassSet, quota_class_set)

    @renamed_param('quota_class_name', 'quota_class_set')
    def update_quota_class_set(self, quota_class_set, **attrs):
        """Update quota class set.

        :param quota_class_set: The name of the quota class
        :param attrs: The attributes to update on the quota class set
        :returns: the updated quota class set
        """

        return self._update(
            _quota_class_set.QuotaClassSet, quota_class_set, **attrs
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: Callable[[int], None] | None = None,
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
        interval: int | float | None = 2,
        wait: int | None = 120,
        callback: Callable[[int], None] | None = None,
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
