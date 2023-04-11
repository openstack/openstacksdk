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
from openstack.compute.v2 import server as server_
from openstack.compute.v2 import server_share as server_share_
from openstack.shared_file_system.v2 import share as share_
from openstack.tests.functional import base as ft_base
from openstack import utils


LOG = _log.setup_logging(__name__)


class TestServerShare(ft_base.BaseFunctionalTest):
    """This test allows testing the functionality through the Shares API
    which enables associating an instance with a share from Manila.
    This test uses a particular Zuul job to meet the prerequisites for
    using this feature. The job will install Devstack:
    1- With the Jammy distribution which contains the appropriate versions
       of Qemu and libvirt.
    2- Install the Manila and Nova services.
    3- Enable the file-backed memory.
    4- Create a test instance and then stop it.

    The association between this test and the job is done through the
    compute_shared_file_system directory which contains this test.
    """

    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_COMPUTE'

    def setUp(self):
        super().setUp()
        self._set_user_cloud(compute_api_version='2')

        if not self.user_cloud.has_service('compute', '2'):
            self.skipTest('compute service not supported by cloud')

        if not self.user_cloud.has_service('shared-file-system'):
            self.skipTest('shared-file-system service not supported by cloud')

        self.server_name = self.getUniqueString()
        self.share_name = self.getUniqueString()

    def _create_server_and_share(self):
        LOG.debug("Create test server")
        server = self.user_cloud.compute.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks='none',
        )
        self.addCleanup(self._delete_server, server)
        self.user_cloud.compute.wait_for_server(
            server,
            wait=self._wait_for_timeout,
        )
        self.assertIsInstance(server, server_.Server)
        self.assertEqual(self.server_name, server.name)

        protocol_supported = (
            "CEPHFS"
            if any(
                "CEPHFS" in p.capabilities["storage_protocol"]
                for p in self.operator_cloud.share.storage_pools()
            )
            else "NFS"
        )

        LOG.debug("Create test share with protocol %s", protocol_supported)
        share = self.user_cloud.share.create_share(
            name=self.share_name,
            size=1,
            share_type="dhss_false",
            share_protocol=protocol_supported,
            description=None,
        )
        self.addCleanup(self._delete_share, share)
        self.user_cloud.share.wait_for_status(
            share,
            status='available',
            wait=self._wait_for_timeout,
        )
        self.assertIsInstance(share, share_.Share)
        self.assertEqual(self.share_name, share.name)

        self.server = server
        self.share = share

    def _delete_server(self, server):
        try:
            LOG.debug("Delete test server")
            # Detach any shares before deleting the server
            try:
                for share in self.user_cloud.compute.share_attachments(server):
                    LOG.debug(
                        "Detaching share %s before server delete",
                        share.share_id,
                    )
                    self.user_cloud.compute.delete_share_attachment(
                        server, share.share_id
                    )
            except Exception:
                LOG.exception(
                    "Failed to detach shares from server %s",
                    server.id,
                )
            self.user_cloud.compute.delete_server(server.id)
            self.user_cloud.compute.wait_for_delete(
                server,
                wait=self._wait_for_timeout,
            )
        except Exception:
            LOG.exception("Failed to delete test server %s", server.id)

    def _delete_share(self, share):
        try:
            LOG.debug("Delete test share")
            self.user_cloud.share.delete_share(share.id)
            self.user_cloud.share.wait_for_delete(
                share,
                wait=self._wait_for_timeout,
            )
        except Exception:
            LOG.exception("Failed to delete test share %s", share.id)

    def _wait_for_share_status(self, server, expected_status, count=None):
        """Wait for share attachments to reach the expected status."""
        for _ in utils.iterate_timeout(
            self._wait_for_timeout,
            message=f"Wait for share attachment to be {expected_status}",
        ):
            server_shares = list(
                self.user_cloud.compute.share_attachments(server)
            )
            self.assertEqual(1, len(server_shares))
            self.assertIsInstance(
                server_shares[0],
                server_share_.ShareMapping,
            )

            if server_shares[0].status == expected_status:
                return server_shares[0]

    def _wait_for_no_shares(self, server):
        """Wait until all share attachments are removed."""
        for _ in utils.iterate_timeout(
            self._wait_for_timeout,
            message="Wait for deletion of share attachment",
        ):
            server_shares = list(
                self.user_cloud.compute.share_attachments(server)
            )
            if len(server_shares) == 0:
                return

    def test_server_share(self):
        self._create_server_and_share()

        # Stop server
        LOG.debug("Stop test server to attach share")
        self.user_cloud.compute.stop_server(self.server.id)
        self.user_cloud.compute.wait_for_server(
            self.server,
            status='SHUTOFF',
            wait=self._wait_for_timeout,
        )

        # Create the server attachment
        LOG.debug("Attach share to test server")
        server_share = self.user_cloud.compute.create_share_attachment(
            self.server.id,
            self.share.id,
        )
        self.assertIsInstance(
            server_share,
            server_share_.ShareMapping,
        )

        # List all attached server shares (there should only be one)
        share_mapping = self._wait_for_share_status(
            self.server,
            'inactive',
        )
        self.assertEqual(share_mapping.status, 'inactive')

        # Retrieve details of the server share
        server_share = self.user_cloud.compute.get_share_attachment(
            self.server,
            self.share.id,
        )
        self.assertIsInstance(
            server_share,
            server_share_.ShareMapping,
        )
        self.assertEqual(server_share.status, 'inactive')

        # Detach the server share
        LOG.debug("Detach server share")
        result = self.user_cloud.compute.delete_share_attachment(
            self.server,
            self.share.id,
        )
        self.assertIsNone(result)
        self._wait_for_no_shares(self.server)

        # Create the server share with a tag
        LOG.debug("Attach server share with a tag")
        server_share = self.user_cloud.compute.create_share_attachment(
            self.server.id, self.share.id, tag='mytag'
        )
        self.assertIsInstance(
            server_share,
            server_share_.ShareMapping,
        )

        # Retrieve details of the server share and check tag
        share_mapping = self._wait_for_share_status(
            self.server,
            'inactive',
        )
        self.assertEqual(share_mapping.status, 'inactive')
        self.assertEqual(share_mapping.tag, 'mytag')

        # Start server
        LOG.debug("Start test server")
        self.user_cloud.compute.start_server(self.server.id)
        try:
            self.user_cloud.compute.wait_for_server(
                self.server,
                status='ACTIVE',
                wait=self._wait_for_timeout,
            )
        except Exception:
            # Fetch server details to capture fault information
            srv = self.user_cloud.compute.get_server(self.server.id)
            LOG.error(
                "Server failed to reach ACTIVE. Status: %s, Fault: %s",
                srv.status,
                srv.fault,
            )
            raise

        # Retrieve details of the server share after power on
        share_mapping = self._wait_for_share_status(
            self.server,
            'active',
        )
        self.assertEqual(share_mapping.status, 'active')
        self.assertEqual(share_mapping.tag, 'mytag')

        # Stop server
        LOG.debug("Stop test server")
        self.user_cloud.compute.stop_server(self.server.id)
        self.user_cloud.compute.wait_for_server(
            self.server,
            status='SHUTOFF',
            wait=self._wait_for_timeout,
        )

        # Detach the server share
        LOG.debug("Detach server share")
        result = self.user_cloud.compute.delete_share_attachment(
            self.server,
            self.share.id,
        )
        self.assertIsNone(result)
        self._wait_for_no_shares(self.server)
