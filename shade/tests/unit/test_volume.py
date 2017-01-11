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


import cinderclient.exceptions as cinder_exc
import mock
import testtools

import shade
from shade.tests.unit import base


class TestVolume(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_attach_volume(self, mock_nova):
        server = dict(id='server001')
        volume = dict(id='volume001', status='available', attachments=[])
        rvol = dict(id='volume001', status='attached',
                    attachments=[
                        {'server_id': server['id'], 'device': 'device001'}
                    ])
        mock_nova.volumes.create_server_volume.return_value = rvol

        ret = self.cloud.attach_volume(server, volume, wait=False)

        self.assertEqual(rvol, ret)
        mock_nova.volumes.create_server_volume.assert_called_once_with(
            volume_id=volume['id'], server_id=server['id'], device=None
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_attach_volume_exception(self, mock_nova):
        server = dict(id='server001')
        volume = dict(id='volume001', status='available', attachments=[])
        mock_nova.volumes.create_server_volume.side_effect = Exception()

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error attaching volume %s to server %s" % (
                volume['id'], server['id'])
        ):
            self.cloud.attach_volume(server, volume, wait=False)

    @mock.patch.object(shade.OpenStackCloud, 'get_volume')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_attach_volume_wait(self, mock_nova, mock_get):
        server = dict(id='server001')
        volume = dict(id='volume001', status='available', attachments=[])
        attached_volume = dict(
            id=volume['id'], status='attached',
            attachments=[{'server_id': server['id'], 'device': 'device001'}]
        )
        mock_get.side_effect = iter([volume, attached_volume])

        # defaults to wait=True
        ret = self.cloud.attach_volume(server, volume)

        mock_nova.volumes.create_server_volume.assert_called_once_with(
            volume_id=volume['id'], server_id=server['id'], device=None
        )
        self.assertEqual(2, mock_get.call_count)
        self.assertEqual(attached_volume, ret)

    @mock.patch.object(shade.OpenStackCloud, 'get_volume')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_attach_volume_wait_error(self, mock_nova, mock_get):
        server = dict(id='server001')
        volume = dict(id='volume001', status='available', attachments=[])
        errored_volume = dict(id=volume['id'], status='error', attachments=[])
        mock_get.side_effect = iter([volume, errored_volume])

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error in attaching volume %s" % errored_volume['id']
        ):
            self.cloud.attach_volume(server, volume)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_attach_volume_not_available(self, mock_nova):
        server = dict(id='server001')
        volume = dict(id='volume001', status='error', attachments=[])

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Volume %s is not available. Status is '%s'" % (
                volume['id'], volume['status'])
        ):
            self.cloud.attach_volume(server, volume)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_attach_volume_already_attached(self, mock_nova):
        device_id = 'device001'
        server = dict(id='server001')
        volume = dict(id='volume001',
                      attachments=[
                          {'server_id': 'server001', 'device': device_id}
                      ])

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Volume %s already attached to server %s on device %s" % (
                volume['id'], server['id'], device_id)
        ):
            self.cloud.attach_volume(server, volume)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_detach_volume(self, mock_nova):
        server = dict(id='server001')
        volume = dict(id='volume001',
                      attachments=[
                          {'server_id': 'server001', 'device': 'device001'}
                      ])
        self.cloud.detach_volume(server, volume, wait=False)
        mock_nova.volumes.delete_server_volume.assert_called_once_with(
            attachment_id=volume['id'], server_id=server['id']
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_detach_volume_exception(self, mock_nova):
        server = dict(id='server001')
        volume = dict(id='volume001',
                      attachments=[
                          {'server_id': 'server001', 'device': 'device001'}
                      ])
        mock_nova.volumes.delete_server_volume.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error detaching volume %s from server %s" % (
                volume['id'], server['id'])
        ):
            self.cloud.detach_volume(server, volume, wait=False)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_detach_volume_not_attached(self, mock_nova):
        server = dict(id='server001')
        volume = dict(id='volume001',
                      attachments=[
                          {'server_id': 'server999', 'device': 'device001'}
                      ])
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Volume %s is not attached to server %s" % (
                volume['id'], server['id'])
        ):
            self.cloud.detach_volume(server, volume, wait=False)

    @mock.patch.object(shade.OpenStackCloud, 'get_volume')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_detach_volume_wait(self, mock_nova, mock_get):
        server = dict(id='server001')
        volume = dict(id='volume001', status='attached',
                      attachments=[
                          {'server_id': 'server001', 'device': 'device001'}
                      ])
        avail_volume = dict(id=volume['id'], status='available',
                            attachments=[])
        mock_get.side_effect = iter([volume, avail_volume])
        self.cloud.detach_volume(server, volume)
        mock_nova.volumes.delete_server_volume.assert_called_once_with(
            attachment_id=volume['id'], server_id=server['id']
        )
        self.assertEqual(2, mock_get.call_count)

    @mock.patch.object(shade.OpenStackCloud, 'get_volume')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_detach_volume_wait_error(self, mock_nova, mock_get):
        server = dict(id='server001')
        volume = dict(id='volume001', status='attached',
                      attachments=[
                          {'server_id': 'server001', 'device': 'device001'}
                      ])
        errored_volume = dict(id=volume['id'], status='error', attachments=[])
        mock_get.side_effect = iter([volume, errored_volume])

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error in detaching volume %s" % errored_volume['id']
        ):
            self.cloud.detach_volume(server, volume)

    @mock.patch.object(shade.OpenStackCloud, 'get_volume')
    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_delete_volume_deletes(self, mock_cinder, mock_get):
        volume = dict(id='volume001', status='attached')
        mock_get.side_effect = iter([volume, None])

        self.assertTrue(self.cloud.delete_volume(volume['id']))

    @mock.patch.object(shade.OpenStackCloud, 'get_volume')
    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_delete_volume_gone_away(self, mock_cinder, mock_get):
        volume = dict(id='volume001', status='attached')
        mock_get.side_effect = iter([volume])
        mock_cinder.volumes.delete.side_effect = cinder_exc.NotFound('N/A')

        self.assertFalse(self.cloud.delete_volume(volume['id']))
