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

from openstack.common import metadata
from openstack import exceptions
from openstack import resource
from openstack import utils


class Share(resource.Resource, metadata.MetadataMixin):
    resource_key = "share"
    resources_key = "shares"
    base_path = "/shares"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_list = True
    allow_head = False
    allow_delete = True

    #: Properties
    #: The share instance access rules status. A valid value is active,
    #: error, or syncing.
    access_rules_status = resource.Body("access_rules_status", type=str)
    #: The availability zone.
    availability_zone = resource.Body("availability_zone", type=str)
    #: The date and time stamp when the resource was created within the
    #: service’s database.
    created_at = resource.Body("created_at", type=str)
    #: The user defined description of the resource.
    description = resource.Body("description", type=str)
    #: The share host name.
    host = resource.Body("host", type=str)
    #: The level of visibility for the share.
    is_public = resource.Body("is_public", type=bool)
    #: Whether or not this share supports snapshots that can be
    #: cloned into new shares.
    is_creating_new_share_from_snapshot_supported = resource.Body(
        "create_share_from_snapshot_support", type=bool
    )
    #: Whether the share's snapshots can be mounted directly and access
    #: controlled independently or not.
    is_mounting_snapshot_supported = resource.Body(
        "mount_snapshot_support", type=bool
    )
    #: Whether the share can be reverted to its latest snapshot or not.
    is_reverting_to_snapshot_supported = resource.Body(
        "revert_to_snapshot_support", type=bool
    )
    #: An extra specification that filters back ends by whether the share
    #: supports snapshots or not.
    is_snapshot_supported = resource.Body("snapshot_support", type=bool)
    #: Indicates whether the share has replicas or not.
    is_replicated = resource.Body("has_replicas", type=bool)
    #: One or more metadata key and value pairs as a dictionary of strings.
    metadata = resource.Body("metadata", type=dict)
    #: The progress of the share creation.
    progress = resource.Body("progress", type=str)
    #: The ID of the project that owns the resource.
    project_id = resource.Body("project_id", type=str)
    #: The share replication type. Valid values are none, readable,
    #: writable and dr.
    replication_type = resource.Body("replication_type", type=str)
    #: The UUID of the share group that this shares belongs to.
    share_group_id = resource.Body("share_group_id", type=str)
    #: The share network ID.
    share_network_id = resource.Body("share_network_id", type=str)
    #: The Shared File Systems protocol. A valid value is NFS,
    #: CIFS, GlusterFS, HDFS, CephFS, MAPRFS
    share_protocol = resource.Body("share_proto", type=str)
    #: The UUID of the share server.
    share_server_id = resource.Body("share_server_id", type=str)
    #: The UUID of the share type. In minor versions, this parameter is a
    #: share type name, as a string.
    share_type = resource.Body("share_type", type=str)
    #: Name of the share type.
    share_type_name = resource.Body("share_type_name", type=str)
    #: The share size, in GiBs.
    size = resource.Body("size", type=int)
    #: The UUID of the snapshot that was used to create the
    #: share.
    snapshot_id = resource.Body("snapshot_id", type=str)
    #: The ID of the group snapshot instance that was used to create
    #: this share.
    source_share_group_snapshot_member_id = resource.Body(
        "source_share_group_snapshot_member_id", type=str
    )
    #: The share status
    status = resource.Body("status", type=str)
    #: For the share migration, the migration task state.
    task_state = resource.Body("task_state", type=str)
    #: ID of the user that the share was created by.
    user_id = resource.Body("user_id", type=str)
    #: Display name for updating name
    display_name = resource.Body("display_name", type=str)
    #: Display description for updating description
    display_description = resource.Body("display_description", type=str)

    def _action(self, session, body, microversion=None):
        """Perform share instance actions given the message body"""
        url = utils.urljoin(self.base_path, self.id, 'action')
        headers = {'Accept': ''}

        if microversion is None:
            microversion = self._get_microversion(session)

        response = session.post(
            url, json=body, headers=headers, microversion=microversion
        )

        exceptions.raise_from_response(response)
        return response

    def extend_share(self, session, new_size, force=False):
        """Extend the share size.

        :param float new_size: The new size of the share
            in GiB.
        :param bool force: Whether or not to use force, bypassing
            the scheduler. Requires admin privileges. Defaults to False.
        :returns: The result of the action.
        :rtype: ``None``
        """

        extend_body = {"new_size": new_size}

        if force is True:
            extend_body['force'] = True

        body = {"extend": extend_body}
        self._action(session, body)

    def shrink_share(self, session, new_size):
        """Shrink the share size.

        :param float new_size: The new size of the share
            in GiB.
        :returns: ``None``
        """

        body = {"shrink": {'new_size': new_size}}
        self._action(session, body)

    def revert_to_snapshot(self, session, snapshot_id):
        """Revert the share to the given snapshot.

        :param str snapshot_id: The id of the snapshot to revert to.
        :returns: ``None``
        """
        body = {"revert": {"snapshot_id": snapshot_id}}
        self._action(session, body)

    def manage(self, session, protocol, export_path, service_host, **params):
        """Manage a share.

        :param session: A session object used for sending request.
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

        path = 'manage'
        attrs = {
            'share': {
                'protocol': protocol,
                'export_path': export_path,
                'service_host': service_host,
            }
        }

        attrs['share'].update(params)

        url = utils.urljoin(self.base_path, path)
        resp = session.post(url, json=attrs)

        self._translate_response(resp)
        return self

    def unmanage(self, session):
        """Unmanage a share.

        :param session: A session object used for sending request.
        :returns: ``None``
        """

        body = {'unmanage': None}

        self._action(session, body)
