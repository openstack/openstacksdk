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
import six

from openstack import proxy2
from openstack.volume_backup.v2 import backup as _backup
from openstack.volume_backup.v2 import backup_policy as _backup_policy
from openstack.volume_backup.v2 import backup_task as _backup_task


class Proxy(proxy2.BaseProxy):
    def create_backup(self, **attrs):
        """Create a new CloudBackup from attributes
        :param dict attrs: Keyword arguments which will be used to create
              a :class:`~openstack.volume_backup.v2.backup.CloudBackup`
              comprised of the properties on the CloudBackup class.
        :returns: The results of CloudBackup creation
        :rtype: :class:`~openstack.volume_backup.v2.backup.CloudBackup`
        """
        return self._create(_backup.CloudBackup, **attrs)

    def create_native_backup(self, **attrs):
        """Create a new Backup from attributes with native API
        :param dict attrs: Keyword arguments which will be used to create
              a :class:`~openstack.volume_backup.v2.backup.CloudBackup`
              comprised of the properties on the CloudBackup class.
        :returns: The results of Backup creation
        :rtype: :class:`~openstack.volume_backup.v2.backup.Backup`
        """
        return self._create(_backup.Backup, **attrs)

# def delete_backup(self, backup, ignore_missing=True):
#     """Delete a CloudBackup
#
#     :param backup: The value can be the ID of a backup or a :class:`
#             ~openstack.volume_backup.v2.backup.CloudBackup` instance
#     :param bool ignore_missing: When set to ``False``
#         :class:`~openstack.exceptions.ResourceNotFound` will be raised when
#         the zone does not exist.
#         When set to ``True``, no exception will be set when attempting to
#         delete a nonexistent zone.
#
#     :returns: rsync job
#     :rtype: :class:`~openstack.volume_backup.v2.backup.Backup`
#     """
#     return self._delete(_backup.CloudBackup,
#                         backup,
#                         ignore_missing=ignore_missing)

    def delete_backup(self, backup, ignore_missing=True):
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a :class:`
                ~openstack.volume_backup.v2.backup.Backup` instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: rsync job
        :rtype: :class:`~openstack.volume_backup.v2.backup.Backup`
        """
        return self._delete(_backup.Backup,
                            backup,
                            ignore_missing=ignore_missing)

    def restore_backup(self, backup, volume_id):
        """Restore a CloudBackup to volume

        :param backup: The value can be the ID of a zone or a :class:`
                ~openstack.volume_backup.v2.backup.CloudBackup` instance
        :param volume_id: the volume to restore to
        :returns: A sync Job of restore backup
        :rtype: :class:`~openstack.volume_backup.v2.backup.Backup`
        """
        if isinstance(backup, _backup.Backup):
            backup = backup.id
        backup = self._get_resource(_backup.CloudBackup, backup)
        return backup.restore(self._session, volume_id)

    def backups(self, details=False, **query):
        """Retrieve a generator of backups
        :param bool details: When ``True``, returns
            :class:`~openstack.volume_backup.v2.backup.BackupDetail` objects,
            otherwise :class:`~openstack.volume_backup.v2.backup.Backup`.
            *Default: ``False``*
        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``name``: backup name
            * ``status``: backup status :
                ``available``, ``error``, ``restoring``, ``creating``,
                ``deleting``, ``error_restoring``
            * ``volume_id``: backup of volume
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of backup
            (:class:`~openstack.volume_backup.v2.backup.Backup`) instances
        """
        resource_clazz = _backup.BackupDetail if details else _backup.Backup
        return self._list(resource_clazz, paginated=True, **query)

    def get_backup(self, backup):
        """Get a backup
        :param backup: The value can be the ID of a backup
             or a :class:`~openstack.volume_backup.v2.backup.Backup` instance.
        :returns: Backup instance
        :rtype: :class:`~openstack.volume_backup.v2.backup.Backup`
        """
        return self._get(_backup.Backup, backup)

    def backup_policies(self):
        """Retrieve a generator of backup_policys

        :returns: A generator of backup_policy (:class:`~openstack.
                volume_backup.v2.backup_policy.BackupPolicy`) instances
        """
        return self._list(_backup_policy.BackupPolicy, paginated=False)

    def create_backup_policy(self, name, **attrs):
        """Create a new backup policy from name and scheduled policy attributes
        :param name: Backup Policy name
        :param dict attrs: Keyword arguments which will be used to create a
        :class:`~openstack.volume_backup.v2.backup_policy.ScheduledPolicy`,
            comprised of the properties on the SchedulePolicy class.
        :returns: The results of backup policy creation
        :rtype: :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
        """
        scheduled_policy = _backup_policy.SchedulePolicy.new(**attrs)
        backup_policy = _backup_policy.BackupPolicy(
            name=name, scheduled_policy=scheduled_policy)
        return backup_policy.create(self._session, prepend_key=False)

    def update_backup_policy(self, backup_policy, **attrs):
        """update a backup_policy from backup policy attributes
        :param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        :param dict attrs: Keyword arguments which will be used to create a
        :class:`~openstack.volume_backup.v2.backup_policy.ScheduledPolicy`,
            comprised of the properties on the SchedulePolicy class.
        :returns: The results of backup_policy creation
        :rtype: :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
        """
        return self._update(_backup_policy.BackupPolicy,
                            backup_policy,
                            prepend_key=False,
                            **attrs)

    def delete_backup_policy(self, backup_policy, ignore_missing=True):
        """Delete a backup policy

        :param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the backup_policy does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent backup_policy.

        :returns: backup_policy been deleted
        :rtype: :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
        """
        return self._delete(_backup_policy.BackupPolicy,
                            backup_policy,
                            ignore_missing=ignore_missing)

    def find_backup_policy(self, name_or_id, ignore_missing=True):
        """Find a single backup_policy

        :param name_or_id: The name or ID of a backup_policy
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the backup_policy does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent backup_policy.

        :returns: ``None``
        """
        return self._find(_backup_policy.BackupPolicy, name_or_id,
                          ignore_missing=ignore_missing,
                          name=name_or_id)

    def link_resources_to_policy(self, backup_policy, resources):
        """link resource to backup policy
        :param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        :param resources: resources to bound, should be a list of volume id
        :returns: list of `~openstack.volume_backup.v2.backup_policy
            .BindResource` instance
        :rtype: :class:`~openstack.volume_backup.v2.backup_policy
                    .LindedResource`
        """
        backup_policy = self._get_resource(_backup_policy.BackupPolicy,
                                           backup_policy)
        linked_resource = _backup_policy.LindedResource()
        return linked_resource.link(self._session,
                                    backup_policy.id,
                                    resources)

    def unlink_resources_of_policy(self, backup_policy, resources):
        """Bind resource to backup policy
        :param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        :param resources: resources to bound, should be a list of volume id
        :returns: list of `~openstack.volume_backup.v2.backup_policy
            .BindResource` instance
        :rtype: :class:`~openstack.volume_backup.v2.backup_policy.
                        UnlinkedResource`
        """
        backup_policy = self._get_resource(_backup_policy.BackupPolicy,
                                           backup_policy)
        unlinked_resource = _backup_policy.UnlinkedResource()
        return unlinked_resource.unlink(self._session,
                                        backup_policy.id,
                                        resources)

    def execute_policy(self, backup_policy):
        """Execute policy immediately

        ::param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        """
        backup_policy = self._get_resource(_backup_policy.BackupPolicy,
                                           backup_policy)
        return backup_policy.execute(self._session)

    def enable_policy(self, backup_policy):
        """Enable policy

        ::param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        """
        updated = {
            "scheduled_policy": {
                "status": "ON"
            }
        }
        return self.update_backup_policy(backup_policy, **updated)

    def disable_policy(self, backup_policy):
        """disable policy

        ::param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        """
        updated = {
            "scheduled_policy": {
                "status": "OFF"
            }
        }
        return self.update_backup_policy(backup_policy, **updated)

    def tasks(self, backup_policy, **query):
        """Retrieve a generator of tasks
        :param backup_policy: The value can be the ID of a backup_policy or a
            :class:`~openstack.volume_backup.v2.backup_policy.BackupPolicy`
            instance
        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``id``: task id
            * ``job_id``: alternate to id
            * ``status``: includes:``RUNNING``, ``EXECUTE_TIMEOUT``,
                    ``WAITING``, EXECUTE_FAIL``, ``EXECUTE_SUCCESS``
            * ``sort_dir``: ``desc``, ``asc``
            * ``sort_key``: only ``created_at`` support for now
            * ``marker``:  pagination marker
            * ``limit``: pagination limit
            * ``offset``: pagination offset

        :returns: A generator of backup
            (:class:`~openstack.volume_backup.v2.backup.Backup`) instances
        """
        backup_policy = self._get_resource(_backup_policy.BackupPolicy,
                                           backup_policy)
        query["policy_id"] = backup_policy.id
        return self._list(_backup_task.BackupTask, paginated=True, **query)
