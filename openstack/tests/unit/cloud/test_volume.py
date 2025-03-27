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


import testtools

from openstack.block_storage.v3 import volume
from openstack.cloud import meta
from openstack.compute.v2 import volume_attachment
from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestVolume(base.TestCase):
    def _compare_volumes(self, exp, real):
        self.assertDictEqual(
            volume.Volume(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def _compare_volume_attachments(self, exp, real):
        self.assertDictEqual(
            volume_attachment.VolumeAttachment(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def test_attach_volume(self):
        server = dict(id='server001')
        vol = {
            'id': 'volume001',
            'status': 'available',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        rattach = {
            'server_id': server['id'],
            'device': 'device001',
            'volumeId': volume['id'],
            'id': 'attachmentId',
        }
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                        ],
                    ),
                    json={'volumeAttachment': rattach},
                    validate=dict(
                        json={'volumeAttachment': {'volumeId': vol['id']}}
                    ),
                ),
            ]
        )
        ret = self.cloud.attach_volume(server, volume, wait=False)
        self._compare_volume_attachments(rattach, ret)
        self.assert_calls()

    def test_attach_volume_exception(self):
        server = dict(id='server001')
        vol = {
            'id': 'volume001',
            'status': 'available',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                        ],
                    ),
                    status_code=404,
                    validate=dict(
                        json={'volumeAttachment': {'volumeId': vol['id']}}
                    ),
                ),
            ]
        )
        with testtools.ExpectedException(
            exceptions.NotFoundException,
        ):
            self.cloud.attach_volume(server, volume, wait=False)
        self.assert_calls()

    def test_attach_volume_wait(self):
        server = dict(id='server001')
        vol = {
            'id': 'volume001',
            'status': 'available',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['attachments'] = [
            {'server_id': server['id'], 'device': 'device001'}
        ]
        vol['status'] = 'in-use'
        attached_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        rattach = {
            'server_id': server['id'],
            'device': 'device001',
            'volumeId': volume['id'],
            'id': 'attachmentId',
        }
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                        ],
                    ),
                    json={'volumeAttachment': rattach},
                    validate=dict(
                        json={'volumeAttachment': {'volumeId': vol['id']}}
                    ),
                ),
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', vol['id']]
                    ),
                    json={'volume': volume},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', vol['id']]
                    ),
                    json={'volume': attached_volume},
                ),
            ]
        )
        # defaults to wait=True
        ret = self.cloud.attach_volume(server, volume)
        self._compare_volume_attachments(rattach, ret)
        self.assert_calls()

    def test_attach_volume_wait_error(self):
        server = dict(id='server001')
        vol = {
            'id': 'volume001',
            'status': 'available',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['status'] = 'error'
        errored_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        rattach = {
            'server_id': server['id'],
            'device': 'device001',
            'volumeId': volume['id'],
            'id': 'attachmentId',
        }
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                        ],
                    ),
                    json={'volumeAttachment': rattach},
                    validate=dict(
                        json={'volumeAttachment': {'volumeId': vol['id']}}
                    ),
                ),
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume['id']]
                    ),
                    json={'volume': errored_volume},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume['id']]
                    ),
                    json={'volume': errored_volume},
                ),
            ]
        )

        with testtools.ExpectedException(exceptions.ResourceFailure):
            self.cloud.attach_volume(server, volume)
        self.assert_calls()

    def test_attach_volume_not_available(self):
        server = dict(id='server001')
        volume = dict(id='volume001', status='error', attachments=[])

        with testtools.ExpectedException(
            exceptions.SDKException,
            "Volume {} is not available. Status is '{}'".format(
                volume['id'], volume['status']
            ),
        ):
            self.cloud.attach_volume(server, volume)
        self.assertEqual(0, len(self.adapter.request_history))

    def test_attach_volume_already_attached(self):
        device_id = 'device001'
        server = dict(id='server001')
        volume = dict(
            id='volume001',
            attachments=[{'server_id': 'server001', 'device': device_id}],
        )

        with testtools.ExpectedException(
            exceptions.SDKException,
            "Volume {} already attached to server {} on device {}".format(
                volume['id'], server['id'], device_id
            ),
        ):
            self.cloud.attach_volume(server, volume)
        self.assertEqual(0, len(self.adapter.request_history))

    def test_detach_volume(self):
        server = dict(id='server001')
        volume = dict(
            id='volume001',
            attachments=[{'server_id': 'server001', 'device': 'device001'}],
        )
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', server['id']]
                    ),
                    json={'server': server},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                            volume['id'],
                        ],
                    ),
                ),
            ]
        )
        self.cloud.detach_volume(server, volume, wait=False)
        self.assert_calls()

    def test_detach_volume_exception(self):
        server = dict(id='server001')
        volume = dict(
            id='volume001',
            attachments=[{'server_id': 'server001', 'device': 'device001'}],
        )
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', server['id']]
                    ),
                    json={'server': server},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                            volume['id'],
                        ],
                    ),
                    status_code=404,
                ),
            ]
        )
        with testtools.ExpectedException(
            exceptions.NotFoundException,
        ):
            self.cloud.detach_volume(server, volume, wait=False)
        self.assert_calls()

    def test_detach_volume_wait(self):
        server = dict(id='server001')
        attachments = [{'server_id': 'server001', 'device': 'device001'}]
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': attachments,
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['status'] = 'available'
        vol['attachments'] = []
        avail_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', server['id']]
                    ),
                    json={'server': server},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                            volume.id,
                        ],
                    ),
                ),
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    json={'volume': avail_volume},
                ),
            ]
        )
        self.cloud.detach_volume(server, volume)
        self.assert_calls()

    def test_detach_volume_wait_error(self):
        server = dict(id='server001')
        attachments = [{'server_id': 'server001', 'device': 'device001'}]
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': attachments,
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['status'] = 'error'
        vol['attachments'] = []
        errored_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', server['id']]
                    ),
                    json={'server': server},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=[
                            'servers',
                            server['id'],
                            'os-volume_attachments',
                            volume.id,
                        ],
                    ),
                ),
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    json={'volume': errored_volume},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', errored_volume['id']],
                    ),
                    json={'volume': errored_volume},
                ),
            ]
        )
        with testtools.ExpectedException(exceptions.ResourceFailure):
            self.cloud.detach_volume(server, volume)
        self.assert_calls()

    def test_delete_volume_deletes(self):
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    json={'volumes': [volume]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', volume.id],
                        qs_elements=['cascade=False'],
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    status_code=404,
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_volume(volume['id']))
        self.assert_calls()

    def test_delete_volume_gone_away(self):
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    json=volume,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', volume.id],
                        qs_elements=['cascade=False'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    status_code=404,
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_volume(volume['id']))
        self.assert_calls()

    def test_delete_volume_force(self):
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume['id']]
                    ),
                    json={'volumes': [volume]},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', volume.id, 'action'],
                    ),
                    validate=dict(json={'os-force_delete': None}),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume['id']]
                    ),
                    status_code=404,
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_volume(volume['id'], force=True))
        self.assert_calls()

    def test_set_volume_bootable(self):
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    json={'volume': volume},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', volume.id, 'action'],
                    ),
                    json={'os-set_bootable': {'bootable': True}},
                ),
            ]
        )
        self.cloud.set_volume_bootable(volume['id'])
        self.assert_calls()

    def test_set_volume_bootable_false(self):
        vol = {
            'id': 'volume001',
            'status': 'attached',
            'name': '',
            'attachments': [],
        }
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume.id]
                    ),
                    json={'volume': volume},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', volume.id, 'action'],
                    ),
                    json={'os-set_bootable': {'bootable': False}},
                ),
            ]
        )
        self.cloud.set_volume_bootable(volume['id'])
        self.assert_calls()

    def test_get_volume_by_id(self):
        vol1 = meta.obj_to_munch(fakes.FakeVolume('01', 'available', 'vol1'))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', '01']
                    ),
                    json={'volume': vol1},
                ),
            ]
        )
        self._compare_volumes(vol1, self.cloud.get_volume_by_id('01'))
        self.assert_calls()

    def test_create_volume(self):
        vol1 = meta.obj_to_munch(fakes.FakeVolume('01', 'available', 'vol1'))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes']
                    ),
                    json={'volume': vol1},
                    validate=dict(
                        json={
                            'volume': {
                                'size': 50,
                                'name': 'vol1',
                            }
                        }
                    ),
                ),
            ]
        )

        self.cloud.create_volume(50, name='vol1')
        self.assert_calls()

    def test_create_bootable_volume(self):
        vol1 = meta.obj_to_munch(fakes.FakeVolume('01', 'available', 'vol1'))
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes']
                    ),
                    json={'volume': vol1},
                    validate=dict(
                        json={
                            'volume': {
                                'size': 50,
                                'name': 'vol1',
                            }
                        }
                    ),
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['volumes', '01', 'action'],
                    ),
                    validate=dict(
                        json={'os-set_bootable': {'bootable': True}}
                    ),
                ),
            ]
        )

        self.cloud.create_volume(50, name='vol1', bootable=True)
        self.assert_calls()
