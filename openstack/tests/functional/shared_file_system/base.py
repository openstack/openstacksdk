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

from openstack import resource
from openstack.tests.functional import base


class BaseSharedFileSystemTest(base.BaseFunctionalTest):
    min_microversion: ty.Optional[str] = None

    def setUp(self):
        super().setUp()
        self.require_service(
            'shared-file-system', min_microversion=self.min_microversion
        )
        self._set_operator_cloud(shared_file_system_api_version='2.82')
        self._set_user_cloud(shared_file_system_api_version='2.82')

    def create_share(self, **kwargs):
        share = self.user_cloud.share.create_share(**kwargs)
        self.addCleanup(
            self.user_cloud.share.delete_share, share.id, ignore_missing=True
        )
        self.user_cloud.share.wait_for_status(
            share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(share.id)
        return share

    def create_share_snapshot(self, share_id, **kwargs):
        share_snapshot = self.user_cloud.share.create_share_snapshot(
            share_id=share_id, force=True
        )
        self.addCleanup(
            resource.wait_for_delete,
            self.user_cloud.share,
            share_snapshot,
            wait=self._wait_for_timeout,
            interval=2,
        )
        self.addCleanup(
            self.user_cloud.share.delete_share_snapshot,
            share_snapshot.id,
            ignore_missing=False,
        )
        self.user_cloud.share.wait_for_status(
            share_snapshot,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(share_snapshot.id)
        return share_snapshot

    def create_share_group(self, **kwargs):
        share_group = self.user_cloud.share.create_share_group(**kwargs)
        self.addCleanup(
            self.operator_cloud.share.delete_share_group,
            share_group.id,
            ignore_missing=True,
        )
        self.assertIsNotNone(share_group.id)
        return share_group

    def create_resource_lock(self, **kwargs):
        resource_lock = self.user_cloud.share.create_resource_lock(**kwargs)
        self.addCleanup(
            self.user_cloud.share.delete_resource_lock,
            resource_lock.id,
            ignore_missing=True,
        )
        self.assertIsNotNone(resource_lock.id)
        return resource_lock
