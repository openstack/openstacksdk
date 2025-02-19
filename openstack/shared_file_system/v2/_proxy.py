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


class Proxy(proxy.Proxy):
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
        :rtype:
            :class:`~openstack.shared_file_system.v2.availability_zone.AvailabilityZone`
        """
        return self._list(_availability_zone.AvailabilityZone)

    def shares(self, details=True, **query):
        """Lists all shares with details

        :param kwargs query: Optional query parameters to be sent to limit
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
            * snapshot_id: The UUID of the share’s base snapshot to filter
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
        :rtype: :class:`~openstack.shared_file_system.v2.share.Share`
        """
        base_path = '/shares/detail' if details else None
        return self._list(_share.Share, base_path=base_path, **query)

    def find_share(self, name_or_id, ignore_missing=True, **query):
        """Find a single share

        :param name_or_id: The name or ID of a share.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.

        :returns: One :class:`~openstack.shared_file_system.v2.share.Share`
                  or None
        """

        return self._find(
            _share.Share, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_share(self, share_id):
        """Lists details of a single share

        :param share: The ID of the share to get
        :returns: Details of the identified share
        :rtype: :class:`~openstack.shared_file_system.v2.share.Share`
        """
        return self._get(_share.Share, share_id)

    def delete_share(self, share, ignore_missing=True):
        """Deletes a single share

        :param share: The ID of the share to delete
        :returns: Result of the ``delete``
        :rtype: ``None``
        """
        self._delete(_share.Share, share, ignore_missing=ignore_missing)

    def update_share(self, share_id, **attrs):
        """Updates details of a single share.

        :param share: The ID of the share to update
        :param dict attrs: The attributes to update on the share
        :returns: the updated share
        :rtype: :class:`~openstack.shared_file_system.v2.share.Share`
        """
        return self._update(_share.Share, share_id, **attrs)

    def create_share(self, **attrs):
        """Creates a share from attributes

        :returns: Details of the new share
        :param dict attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.shares.Shares`,
            comprised of the properties on the Shares class. 'size' and 'share'
            are required to create a share.
        :rtype: :class:`~openstack.shared_file_system.v2.share.Share`
        """
        return self._create(_share.Share, **attrs)

    def revert_share_to_snapshot(self, share_id, snapshot_id):
        """Reverts a share to the specified snapshot, which must be
            the most recent one known to manila.

        :param share_id: The ID of the share to revert
        :param snapshot_id: The ID of the snapshot to revert to
        :returns: Result of the ``revert``
        :rtype: ``None``
        """
        res = self._get(_share.Share, share_id)
        res.revert_to_snapshot(self, snapshot_id)

    def manage_share(self, protocol, export_path, service_host, **params):
        """Manage a share.

        :param str protocol: The shared file systems protocol of this share.
        :param str export_path: The export path formatted according to the
            protocol.
        :param str service_host: The manage-share service host.
        :param kwargs params: Optional parameters to be sent. Available
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

    def unmanage_share(self, share_id):
        """Unmanage the share with the given share ID.

        :param share_id: The ID of the share to unmanage.
        :returns: ``None``
        """

        share_to_unmanage = self._get(_share.Share, share_id)
        share_to_unmanage.unmanage(self)

    def resize_share(
        self, share_id, new_size, no_shrink=False, no_extend=False, force=False
    ):
        """Resizes a share, extending/shrinking the share as needed.

        :param share_id: The ID of the share to resize
        :param new_size: The new size of the share in GiBs. If new_size is
            the same as the current size, then nothing is done.
        :param bool no_shrink: If set to True, the given share is not shrunk,
            even if shrinking the share is required to get the share to the
            given size. This could be useful for extending shares to a minimum
            size, while not shrinking shares to the given size. This defaults
            to False.
        :param bool no_extend: If set to True, the given share is not
            extended, even if extending the share is required to get the share
            to the given size. This could be useful for shrinking shares to a
            maximum size, while not extending smaller shares to that maximum
            size. This defaults to False.
        :param bool force: Whether or not force should be used,
            in the case where the share should be extended.
        :returns: ``None``
        """

        res = self._get(_share.Share, share_id)

        if new_size > res.size and no_extend is not True:
            res.extend_share(self, new_size, force)
        elif new_size < res.size and no_shrink is not True:
            res.shrink_share(self, new_size)

    def share_groups(self, **query):
        """Lists all share groups.

        :param kwargs query: Optional query parameters to be sent to limit
            the share groups being returned.  Available parameters include:

            * status: Filters by a share group status.
            * name: The user defined name of the resource to filter resources
                by.
            * description: The user defined description text that can be used
                to filter resources.
            * project_id: The project ID of the user or service.
            * share_server_id: The UUID of the share server.
            * snapshot_id: The UUID of the share’s base snapshot to filter
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
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_group.ShareGroup`
        """
        return self._list(_share_group.ShareGroup, **query)

    def get_share_group(self, share_group_id):
        """Lists details for a share group.

        :param share: The ID of the share group to get
        :returns: Details of the identified share group
        :rtype: :class:`~openstack.shared_file_system.v2.
                                    share_group.ShareGroup`
        """
        return self._get(_share_group.ShareGroup, share_group_id)

    def find_share_group(self, name_or_id, ignore_missing=True):
        """Finds a single share group

        :param name_or_id: The name or ID of a share group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.shared_file_system.v2.
                                        share_group.ShareGroup`
                                        or None
        """
        return self._find(
            _share_group.ShareGroup, name_or_id, ignore_missing=ignore_missing
        )

    def create_share_group(self, **attrs):
        """Creates a share group from attributes

        :returns: Details of the new share group
        :rtype: :class:`~openstack.shared_file_system.v2.
                                    share_group.ShareGroup`
        """
        return self._create(_share_group.ShareGroup, **attrs)

    def update_share_group(self, share_group_id, **kwargs):
        """Updates details of a single share group

        :param share: The ID of the share group
        :returns: Updated details of the identified share group
        :rtype: :class:`~openstack.shared_file_system.v2.
                                    share_group.ShareGroup`
        """
        return self._update(_share_group.ShareGroup, share_group_id, **kwargs)

    def delete_share_group(self, share_group_id, ignore_missing=True):
        """Deletes a single share group

        :param share: The ID of the share group
        :returns: Result of the "delete" on share group
        :rtype: :class:`~openstack.shared_file_system.v2.
                                    share_group.ShareGroup`
        """
        return self._delete(
            _share_group.ShareGroup,
            share_group_id,
            ignore_missing=ignore_missing,
        )

    def storage_pools(self, details=True, **query):
        """Lists all back-end storage pools with details

        :param kwargs query: Optional query parameters to be sent to limit
            the storage pools being returned.  Available parameters include:

            * pool_name: The pool name for the back end.
            * host_name: The host name for the back end.
            * backend_name: The name of the back end.
            * capabilities: The capabilities for the storage back end.
            * share_type: The share type name or UUID.
        :returns: A generator of manila storage pool resources
        :rtype:
            :class:`~openstack.shared_file_system.v2.storage_pool.StoragePool`
        """
        base_path = '/scheduler-stats/pools/detail' if details else None
        return self._list(
            _storage_pool.StoragePool, base_path=base_path, **query
        )

    def user_messages(self, **query):
        """List shared file system user messages

        :param kwargs query: Optional query parameters to be sent to limit
            the messages being returned.  Available parameters include:

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
        :rtype:
            :class:`~openstack.shared_file_system.v2.user_message.UserMessage`
        """
        return self._list(_user_message.UserMessage, **query)

    def get_user_message(self, message_id):
        """List details of a single user message

        :param message_id: The ID of the user message
        :returns: Details of the identified user message
        :rtype:
            :class:`~openstack.shared_file_system.v2.user_message.UserMessage`
        """
        return self._get(_user_message.UserMessage, message_id)

    def delete_user_message(self, message_id, ignore_missing=True):
        """Deletes a single user message

        :param message_id: The ID of the user message
        :returns: Result of the "delete" on the user message
        :rtype:
            :class:`~openstack.shared_file_system.v2.user_message.UserMessage`
        """
        return self._delete(
            _user_message.UserMessage,
            message_id,
            ignore_missing=ignore_missing,
        )

    def limits(self, **query):
        """Lists all share limits.

        :param kwargs query: Optional query parameters to be sent to limit
            the share limits being returned.

        :returns: A generator of manila share limits resources
        :rtype: :class:`~openstack.shared_file_system.v2.limit.Limit`
        """
        return self._list(_limit.Limit, **query)

    def share_snapshots(self, details=True, **query):
        """Lists all share snapshots with details.

        :param kwargs query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * project_id: The ID of the user or service making the API request.

        :returns: A generator of manila share snapshot resources
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_snapshot.ShareSnapshot`
        """
        base_path = '/snapshots/detail' if details else None
        return self._list(
            _share_snapshot.ShareSnapshot, base_path=base_path, **query
        )

    def get_share_snapshot(self, snapshot_id):
        """Lists details of a single share snapshot

        :param snapshot_id: The ID of the snapshot to get
        :returns: Details of the identified share snapshot
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_snapshot.ShareSnapshot`
        """
        return self._get(_share_snapshot.ShareSnapshot, snapshot_id)

    def create_share_snapshot(self, **attrs):
        """Creates a share snapshot from attributes

        :returns: Details of the new share snapshot
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_snapshot.ShareSnapshot`
        """
        return self._create(_share_snapshot.ShareSnapshot, **attrs)

    def update_share_snapshot(self, snapshot_id, **attrs):
        """Updates details of a single share.

        :param snapshot_id: The ID of the snapshot to update
        :pram dict attrs: The attributes to update on the snapshot
        :returns: the updated share snapshot
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_snapshot.ShareSnapshot`
        """
        return self._update(
            _share_snapshot.ShareSnapshot, snapshot_id, **attrs
        )

    def delete_share_snapshot(self, snapshot_id, ignore_missing=True):
        """Deletes a single share snapshot

        :param snapshot_id: The ID of the snapshot to delete
        :returns: Result of the ``delete``
        :rtype: ``None``
        """
        self._delete(
            _share_snapshot.ShareSnapshot,
            snapshot_id,
            ignore_missing=ignore_missing,
        )

    # ========= Network Subnets ==========
    def share_network_subnets(self, share_network_id):
        """Lists all share network subnets with details.

        :param share_network_id: The id of the share network for which
            Share Network Subnets should be listed.
        :returns: A generator of manila share network subnets
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet`
        """
        return self._list(
            _share_network_subnet.ShareNetworkSubnet,
            share_network_id=share_network_id,
        )

    def get_share_network_subnet(
        self,
        share_network_id,
        share_network_subnet_id,
    ):
        """Lists details of a single share network subnet.

        :param share_network_id: The id of the share network associated
            with the Share Network Subnet.
        :param share_network_subnet_id: The id of the Share Network Subnet
            to retrieve.
        :returns: Details of the identified share network subnet
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet`
        """

        return self._get(
            _share_network_subnet.ShareNetworkSubnet,
            share_network_subnet_id,
            share_network_id=share_network_id,
        )

    def create_share_network_subnet(self, share_network_id, **attrs):
        """Creates a share network subnet from attributes

        :param share_network_id: The id of the share network wthin which the
            the Share Network Subnet should be created.
        :param dict attrs: Attributes which will be used to create
            a share network subnet.
        :returns: Details of the new share network subnet.
        :rtype:
            :class:`~openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet`
        """
        return self._create(
            _share_network_subnet.ShareNetworkSubnet,
            **attrs,
            share_network_id=share_network_id,
        )

    def delete_share_network_subnet(
        self, share_network_id, share_network_subnet, ignore_missing=True
    ):
        """Deletes a share network subnet.

        :param share_network_id: The id of the Share Network associated with
            the Share Network Subnet.
        :param share_network_subnet: The id of the Share Network Subnet
            which should be deleted.
        :returns: Result of the ``delete``
        :rtype: None
        """

        self._delete(
            _share_network_subnet.ShareNetworkSubnet,
            share_network_subnet,
            share_network_id=share_network_id,
            ignore_missing=ignore_missing,
        )

    def share_snapshot_instances(self, details=True, **query):
        """Lists all share snapshot instances with details.

        :param bool details: Whether to fetch detailed resource
            descriptions. Defaults to True.
        :param kwargs query: Optional query parameters to be sent to limit
            the share snapshot instance being returned.
            Available parameters include:

            * snapshot_id: The UUID of the share’s base snapshot to filter
                the request based on.
            * project_id: The project ID of the user or service making the
                request.

        :returns: A generator of share snapshot instance resources
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_snapshot_instance.ShareSnapshotInstance`
        """
        base_path = '/snapshot-instances/detail' if details else None
        return self._list(
            _share_snapshot_instance.ShareSnapshotInstance,
            base_path=base_path,
            **query,
        )

    def get_share_snapshot_instance(self, snapshot_instance_id):
        """Lists details of a single share snapshot instance

        :param snapshot_instance_id: The ID of the snapshot instance to get
        :returns: Details of the identified snapshot instance
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_snapshot_instance.ShareSnapshotInstance`
        """
        return self._get(
            _share_snapshot_instance.ShareSnapshotInstance,
            snapshot_instance_id,
        )

    def share_networks(self, details=True, **query):
        """Lists all share networks with details.

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned. Available parameters include:

            * name~: The user defined name of the resource to filter resources
              by.
            * project_id: The ID of the user or service making the request.
            * description~: The description pattern that can be used to filter
              shares, share snapshots, share networks or share groups.
            * all_projects: (Admin only). Defines whether to list the requested
              resources for all projects.

        :returns: Details of shares networks
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_network.ShareNetwork`
        """
        base_path = '/share-networks/detail' if details else None
        return self._list(
            _share_network.ShareNetwork, base_path=base_path, **query
        )

    def get_share_network(self, share_network_id):
        """Lists details of a single share network

        :param share_network: The ID of the share network to get
        :returns: Details of the identified share network
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_network.ShareNetwork`
        """
        return self._get(_share_network.ShareNetwork, share_network_id)

    def delete_share_network(self, share_network_id, ignore_missing=True):
        """Deletes a single share network

        :param share_network_id: The ID of the share network to delete
        :rtype: ``None``
        """
        self._delete(
            _share_network.ShareNetwork,
            share_network_id,
            ignore_missing=ignore_missing,
        )

    def update_share_network(self, share_network_id, **attrs):
        """Updates details of a single share network.

        :param share_network_id: The ID of the share network to update
        :pram dict attrs: The attributes to update on the share network
        :returns: the updated share network
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_network.ShareNetwork`
        """
        return self._update(
            _share_network.ShareNetwork, share_network_id, **attrs
        )

    def create_share_network(self, **attrs):
        """Creates a share network from attributes

        :returns: Details of the new share network
        :param dict attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            share_network.ShareNetwork`,comprised of the properties
            on the ShareNetwork class.
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_network.ShareNetwork`
        """
        return self._create(_share_network.ShareNetwork, **attrs)

    def share_instances(self, **query):
        """Lists all share instances.

        :param kwargs query: Optional query parameters to be sent to limit
            the share instances being returned. Available parameters include:

        * export_location_id: The export location UUID that can be used
          to filter share instances.
        * export_location_path: The export location path that can be used
          to filter share instances.

        :returns: Details of share instances resources
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_instance.ShareInstance`
        """
        return self._list(_share_instance.ShareInstance, **query)

    def get_share_instance(self, share_instance_id):
        """Shows details for a single share instance

        :param share_instance_id: The UUID of the share instance to get

        :returns: Details of the identified share instance
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_instance.ShareInstance`
        """
        return self._get(_share_instance.ShareInstance, share_instance_id)

    def reset_share_instance_status(self, share_instance_id, status):
        """Explicitly updates the state of a share instance.

        :param share_instance_id: The UUID of the share instance to reset.
        :param status: The share or share instance status to be set.

        :returns: ``None``
        """
        res = self._get_resource(
            _share_instance.ShareInstance, share_instance_id
        )
        res.reset_status(self, status)

    def delete_share_instance(self, share_instance_id):
        """Force-deletes a share instance

        :param share_instance: The ID of the share instance to delete

        :returns: ``None``
        """
        res = self._get_resource(
            _share_instance.ShareInstance, share_instance_id
        )
        res.force_delete(self)

    def export_locations(self, share_id):
        """List all export locations with details

        :param share_id: The ID of the share to list export locations from
        :returns: List of export locations
        :rtype: List of :class:`~openstack.shared_filesystem_storage.v2.
            share_export_locations.ShareExportLocations`
        """
        return self._list(
            _share_export_locations.ShareExportLocation, share_id=share_id
        )

    def get_export_location(self, export_location, share_id):
        """List details of export location

        :param export_location: The export location resource to get
        :param share_id: The ID of the share to get export locations from
        :returns: Details of identified export location
        :rtype: :class:`~openstack.shared_filesystem_storage.v2.
            share_export_locations.ShareExportLocations`
        """

        export_location_id = resource.Resource._get_id(export_location)
        return self._get(
            _share_export_locations.ShareExportLocation,
            export_location_id,
            share_id=share_id,
        )

    def access_rules(self, share, **query):
        """Lists the access rules on a share.

        :returns: A generator of the share access rules.
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_access_rules.ShareAccessRules`
        """
        share = self._get_resource(_share.Share, share)
        return self._list(
            _share_access_rule.ShareAccessRule, share_id=share.id, **query
        )

    def get_access_rule(self, access_id):
        """List details of an access rule.

        :param access_id: The id of the access rule to get
        :returns: Details of the identified access rule.
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_access_rules.ShareAccessRules`
        """
        return self._get(_share_access_rule.ShareAccessRule, access_id)

    def create_access_rule(self, share_id, **attrs):
        """Creates an access rule from attributes

        :returns: Details of the new access rule
        :param share_id: The ID of the share
        :param dict attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            share_access_rules.ShareAccessRules`, comprised of the
            properties on the ShareAccessRules class.
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_access_rules.ShareAccessRules`
        """
        base_path = f"/shares/{share_id}/action"
        return self._create(
            _share_access_rule.ShareAccessRule, base_path=base_path, **attrs
        )

    def delete_access_rule(
        self, access_id, share_id, ignore_missing=True, *, unrestrict=False
    ):
        """Deletes an access rule

        :param access_id: The id of the access rule to get
        :param share_id: The ID of the share
        :param unrestrict: If Manila must attempt removing locks while deleting

        :rtype: ``requests.models.Response`` HTTP response from internal
            requests client
        """
        res = self._get_resource(
            _share_access_rule.ShareAccessRule, access_id, share_id=share_id
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

        :param kwargs query: Optional query parameters to be sent
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
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_group_snapshot.ShareGroupSnapshot`
        """
        base_path = '/share-group-snapshots/detail' if details else None
        return self._list(
            _share_group_snapshot.ShareGroupSnapshot,
            base_path=base_path,
            **query,
        )

    def share_group_snapshot_members(self, group_snapshot_id):
        """Lists all share group snapshots members.

        :param group_snapshot_id: The ID of the group snapshot to get
        :returns: List of the share group snapshot members, which are
            share snapshots.
        :rtype: dict containing attributes of the share snapshot members.
        """
        res = self._get(
            _share_group_snapshot.ShareGroupSnapshot,
            group_snapshot_id,
        )
        response = res.get_members(self)
        return response

    def get_share_group_snapshot(self, group_snapshot_id):
        """Show share group snapshot details

        :param group_snapshot_id: The ID of the group snapshot to get
        :returns: Details of the group snapshot
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_group_snapshot.ShareGroupSnapshot`
        """
        return self._get(
            _share_group_snapshot.ShareGroupSnapshot, group_snapshot_id
        )

    def create_share_group_snapshot(self, share_group_id, **attrs):
        """Creates a point-in-time snapshot copy of a share group.

        :returns: Details of the new snapshot
        :param dict attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            share_group_snapshots.ShareGroupSnapshots`,
        :param 'share_group_id': ID of the share group to have the snapshot
            taken.
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_group_snapshot.ShareGroupSnapshot`
        """
        return self._create(
            _share_group_snapshot.ShareGroupSnapshot,
            share_group_id=share_group_id,
            **attrs,
        )

    def reset_share_group_snapshot_status(self, group_snapshot_id, status):
        """Reset share group snapshot state.

        :param group_snapshot_id: The ID of the share group snapshot to reset
        :param status: The state of the share group snapshot to be set, A
            valid value is "creating", "error", "available", "deleting",
            "error_deleting".
        :rtype: ``None``
        """
        res = self._get(
            _share_group_snapshot.ShareGroupSnapshot, group_snapshot_id
        )
        res.reset_status(self, status)

    def update_share_group_snapshot(self, group_snapshot_id, **attrs):
        """Updates a share group snapshot.

        :param group_snapshot_id: The ID of the share group snapshot to update
        :param dict attrs: The attributes to update on the share group snapshot
        :returns: the updated share group snapshot
        :rtype: :class:`~openstack.shared_file_system.v2.
            share_group_snapshot.ShareGroupSnapshot`
        """
        return self._update(
            _share_group_snapshot.ShareGroupSnapshot,
            group_snapshot_id,
            **attrs,
        )

    def delete_share_group_snapshot(
        self, group_snapshot_id, ignore_missing=True
    ):
        """Deletes a share group snapshot.

        :param group_snapshot_id: The ID of the share group snapshot to delete
        :rtype: ``None``
        """
        self._delete(
            _share_group_snapshot.ShareGroupSnapshot,
            group_snapshot_id,
            ignore_missing=ignore_missing,
        )

    # ========= Share Metadata ==========
    def get_share_metadata(self, share_id):
        """Lists all metadata for a share.

        :param share_id: The ID of the share

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's metadata.
        :rtype:
            :class:`~openstack.shared_file_system.v2.share.Share`
        """
        share = self._get_resource(_share.Share, share_id)
        return share.fetch_metadata(self)

    def get_share_metadata_item(self, share_id, key):
        """Retrieves a specific metadata item from a share by its key.

        :param share_id: The ID of the share
        :param key: The key of the share metadata

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's metadata.
        :rtype:
            :class:`~openstack.shared_file_system.v2.share.Share`
        """
        share = self._get_resource(_share.Share, share_id)
        return share.get_metadata_item(self, key)

    def create_share_metadata(self, share_id, **metadata):
        """Creates share metadata as key-value pairs.

        :param share_id: The ID of the share
        :param metadata: The metadata to be created

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's metadata.
        :rtype:
            :class:`~openstack.shared_file_system.v2.share.Share`
        """
        share = self._get_resource(_share.Share, share_id)
        return share.set_metadata(self, metadata=metadata)

    def update_share_metadata(self, share_id, metadata, replace=False):
        """Updates metadata of given share.

        :param share_id: The ID of the share
        :param metadata: The metadata to be created
        :param replace: Boolean for whether the preexisting metadata
            should be replaced

        :returns: A :class:`~openstack.shared_file_system.v2.share.Share`
            with the share's updated metadata.
        :rtype:
            :class:`~openstack.shared_file_system.v2.share.Share`
        """
        share = self._get_resource(_share.Share, share_id)
        return share.set_metadata(self, metadata=metadata, replace=replace)

    def delete_share_metadata(self, share_id, keys, ignore_missing=True):
        """Deletes a single metadata item on a share, idetified by its key.

        :param share_id: The ID of the share
        :param keys: The list of share metadata keys to be deleted
        :param ignore_missing: Boolean indicating if missing keys should be ignored.

        :returns: None
        :rtype: None
        """
        share = self._get_resource(_share.Share, share_id)
        keys_failed_to_delete = []
        for key in keys:
            try:
                share.delete_metadata_item(self, key)
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

        :param kwargs query: Optional query parameters to be sent to limit
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
            * lock_context: The lock creator’s context to filter locks by.
            * lock_reason: The lock reason that can be used to filter resource
                locks. (Inexact search is also available with lock_reason~)
            * created_since: Search for the list of resources that were created
                after the specified date. The date is in ‘yyyy-mm-dd’ format.
            * created_before: Search for the list of resources that were
                created prior to the specified date. The date is in
                ‘yyyy-mm-dd’ format.
            * limit: The maximum number of resource locks to return.
            * offset: The offset to define start point of resource lock
                listing.
            * sort_key: The key to sort a list of shares.
            * sort_dir: The direction to sort a list of shares
            * with_count: Whether to show count in API response or not,
                default is False. This query parameter is useful with
                pagination.

        :returns: A generator of manila resource locks
        :rtype: :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock`
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

    def get_resource_lock(self, resource_lock):
        """Show details of a resource lock.

        :param resource_lock: The ID of a resource lock or a
            :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock` instance.
        :returns: Details of the identified resource lock.
        :rtype: :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock`
        """
        return self._get(_resource_locks.ResourceLock, resource_lock)

    def update_resource_lock(self, resource_lock, **attrs):
        """Updates details of a single resource lock.

        :param resource_lock: The ID of a resource lock or a
            :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock` instance.
        :param dict attrs: The attributes to update on the resource lock
        :returns: the updated resource lock
        :rtype: :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock`
        """
        return self._update(
            _resource_locks.ResourceLock, resource_lock, **attrs
        )

    def delete_resource_lock(self, resource_lock, ignore_missing=True):
        """Deletes a single resource lock

        :param resource_lock: The ID of a resource lock or a
            :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock` instance.
        :returns: Result of the ``delete``
        :rtype: ``None``
        """
        return self._delete(
            _resource_locks.ResourceLock,
            resource_lock,
            ignore_missing=ignore_missing,
        )

    def create_resource_lock(self, **attrs):
        """Locks a resource.

        :param dict attrs: Attributes which will be used to create
            a :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock`, comprised of the properties
            on the ResourceLock class. Available parameters include:

            * ``resource_id``: ID of the resource to be locked.
            * ``resource_type``: type of the resource (share, access_rule).
            * ``resource_action``: action to be locked (delete, show).
            * ``lock_reason``: reason why you're locking the resource
                (Optional).
        :returns: Details of the lock
        :rtype: :class:`~openstack.shared_file_system.v2.
            resource_locks.ResourceLock`
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

    def get_quota_class_set(self, quota_class_name):
        """Get quota class set.

        :param quota_class_name: The name of the quota class
        :returns: A :class:`~openstack.shared_file_system.v2
            .quota_class_set.QuotaClassSet`
        """
        return self._get(_quota_class_set.QuotaClassSet, quota_class_name)

    def update_quota_class_set(self, quota_class_name, **attrs):
        """Update quota class set.

        :param quota_class_name: The name of the quota class
        :param attrs: The attributes to update on the quota class set
        :returns: the updated quota class set
        :rtype: :class:`~openstack.shared_file_system.v2
            .quota_class_set.QuotaClassSet`
        """

        return self._update(
            _quota_class_set.QuotaClassSet, quota_class_name, **attrs
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
