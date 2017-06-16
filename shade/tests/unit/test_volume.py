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

import shade
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestVolume(base.RequestsMockTestCase):

    def test_attach_volume(self):
        server = dict(id='server001')
        vol = {'id': 'volume001', 'status': 'available',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        rattach = {'server_id': server['id'], 'device': 'device001',
                   'volumeId': volume['id'], 'id': 'attachmentId'}
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments']),
                 json={'volumeAttachment': rattach},
                 validate=dict(json={
                     'volumeAttachment': {
                         'volumeId': vol['id']}})
                 )])
        ret = self.cloud.attach_volume(server, volume, wait=False)
        self.assertEqual(rattach, ret)
        self.assert_calls()

    def test_attach_volume_exception(self):
        server = dict(id='server001')
        vol = {'id': 'volume001', 'status': 'available',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments']),
                 status_code=404,
                 validate=dict(json={
                     'volumeAttachment': {
                         'volumeId': vol['id']}})
                 )])
        with testtools.ExpectedException(
            shade.OpenStackCloudURINotFound,
            "Error attaching volume %s to server %s" % (
                volume['id'], server['id'])
        ):
            self.cloud.attach_volume(server, volume, wait=False)
        self.assert_calls()

    def test_attach_volume_wait(self):
        server = dict(id='server001')
        vol = {'id': 'volume001', 'status': 'available',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['attachments'] = [{'server_id': server['id'],
                               'device': 'device001'}]
        vol['status'] = 'attached'
        attached_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        rattach = {'server_id': server['id'], 'device': 'device001',
                   'volumeId': volume['id'], 'id': 'attachmentId'}
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments']),
                 json={'volumeAttachment': rattach},
                 validate=dict(json={
                     'volumeAttachment': {
                         'volumeId': vol['id']}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [volume]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [attached_volume]})])
        # defaults to wait=True
        ret = self.cloud.attach_volume(server, volume)
        self.assertEqual(rattach, ret)
        self.assert_calls()

    def test_attach_volume_wait_error(self):
        server = dict(id='server001')
        vol = {'id': 'volume001', 'status': 'available',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['status'] = 'error'
        errored_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        rattach = {'server_id': server['id'], 'device': 'device001',
                   'volumeId': volume['id'], 'id': 'attachmentId'}
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments']),
                 json={'volumeAttachment': rattach},
                 validate=dict(json={
                     'volumeAttachment': {
                         'volumeId': vol['id']}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [errored_volume]})])

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error in attaching volume %s" % errored_volume['id']
        ):
            self.cloud.attach_volume(server, volume)
        self.assert_calls()

    def test_attach_volume_not_available(self):
        server = dict(id='server001')
        volume = dict(id='volume001', status='error', attachments=[])

        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Volume %s is not available. Status is '%s'" % (
                volume['id'], volume['status'])
        ):
            self.cloud.attach_volume(server, volume)
        self.assertEqual(0, len(self.adapter.request_history))

    def test_attach_volume_already_attached(self):
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
        self.assertEqual(0, len(self.adapter.request_history))

    def test_detach_volume(self):
        server = dict(id='server001')
        volume = dict(id='volume001',
                      attachments=[
                          {'server_id': 'server001', 'device': 'device001'}
                      ])
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments', volume['id']]))])
        self.cloud.detach_volume(server, volume, wait=False)
        self.assert_calls()

    def test_detach_volume_exception(self):
        server = dict(id='server001')
        volume = dict(id='volume001',
                      attachments=[
                          {'server_id': 'server001', 'device': 'device001'}
                      ])
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments', volume['id']]),
                 status_code=404)])
        with testtools.ExpectedException(
            shade.OpenStackCloudURINotFound,
            "Error detaching volume %s from server %s" % (
                volume['id'], server['id'])
        ):
            self.cloud.detach_volume(server, volume, wait=False)
        self.assert_calls()

    def test_detach_volume_wait(self):
        server = dict(id='server001')
        attachments = [{'server_id': 'server001', 'device': 'device001'}]
        vol = {'id': 'volume001', 'status': 'attached', 'name': '',
               'attachments': attachments}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['status'] = 'available'
        vol['attachments'] = []
        avail_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments', volume.id])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [avail_volume]})])
        self.cloud.detach_volume(server, volume)
        self.assert_calls()

    def test_detach_volume_wait_error(self):
        server = dict(id='server001')
        attachments = [{'server_id': 'server001', 'device': 'device001'}]
        vol = {'id': 'volume001', 'status': 'attached', 'name': '',
               'attachments': attachments}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        vol['status'] = 'error'
        vol['attachments'] = []
        errored_volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', server['id'],
                             'os-volume_attachments', volume.id])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [errored_volume]})])
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error in detaching volume %s" % errored_volume['id']
        ):
            self.cloud.detach_volume(server, volume)
        self.assert_calls()

    def test_delete_volume_deletes(self):
        vol = {'id': 'volume001', 'status': 'attached',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [volume]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', volume.id])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': []})])
        self.assertTrue(self.cloud.delete_volume(volume['id']))
        self.assert_calls()

    def test_delete_volume_gone_away(self):
        vol = {'id': 'volume001', 'status': 'attached',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', 'detail']),
                 json={'volumes': [volume]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['volumes', volume.id]),
                 status_code=404)])
        self.assertFalse(self.cloud.delete_volume(volume['id']))
        self.assert_calls()

    def test_list_volumes_with_pagination(self):
        vol1 = meta.obj_to_munch(fakes.FakeVolume('01', 'available', 'vol1'))
        vol2 = meta.obj_to_munch(fakes.FakeVolume('02', 'available', 'vol2'))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail']),
                 json={
                     'volumes': [vol1],
                     'volumes_links': [
                         {'href': self.get_mock_url(
                             'volumev2', 'public',
                             append=['volumes', 'detail'],
                             qs_elements=['marker=01']),
                          'rel': 'next'}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail'],
                     qs_elements=['marker=01']),
                 json={
                     'volumes': [vol2],
                     'volumes_links': [
                         {'href': self.get_mock_url(
                             'volumev2', 'public',
                             append=['volumes', 'detail'],
                             qs_elements=['marker=02']),
                          'rel': 'next'}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail'],
                     qs_elements=['marker=02']),
                 json={'volumes': []})])
        self.assertEqual(
            [self.cloud._normalize_volume(vol1),
             self.cloud._normalize_volume(vol2)],
            self.cloud.list_volumes())
        self.assert_calls()

    def test_list_volumes_with_pagination_next_link_fails_once(self):
        vol1 = meta.obj_to_munch(fakes.FakeVolume('01', 'available', 'vol1'))
        vol2 = meta.obj_to_munch(fakes.FakeVolume('02', 'available', 'vol2'))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail']),
                 json={
                     'volumes': [vol1],
                     'volumes_links': [
                         {'href': self.get_mock_url(
                             'volumev2', 'public',
                             append=['volumes', 'detail'],
                             qs_elements=['marker=01']),
                          'rel': 'next'}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail'],
                     qs_elements=['marker=01']),
                 status_code=404),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail']),
                 json={
                     'volumes': [vol1],
                     'volumes_links': [
                         {'href': self.get_mock_url(
                             'volumev2', 'public',
                             append=['volumes', 'detail'],
                             qs_elements=['marker=01']),
                          'rel': 'next'}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail'],
                     qs_elements=['marker=01']),
                 json={
                     'volumes': [vol2],
                     'volumes_links': [
                         {'href': self.get_mock_url(
                             'volumev2', 'public',
                             append=['volumes', 'detail'],
                             qs_elements=['marker=02']),
                          'rel': 'next'}]}),

            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['volumes', 'detail'],
                     qs_elements=['marker=02']),
                 json={'volumes': []})])
        self.assertEqual(
            [self.cloud._normalize_volume(vol1),
             self.cloud._normalize_volume(vol2)],
            self.cloud.list_volumes())
        self.assert_calls()

    def test_list_volumes_with_pagination_next_link_fails_all_attempts(self):
        vol1 = meta.obj_to_munch(fakes.FakeVolume('01', 'available', 'vol1'))
        uris = []
        attempts = 5
        for i in range(attempts):
            uris.extend([
                dict(method='GET',
                     uri=self.get_mock_url(
                         'volumev2', 'public',
                         append=['volumes', 'detail']),
                     json={
                         'volumes': [vol1],
                         'volumes_links': [
                             {'href': self.get_mock_url(
                                 'volumev2', 'public',
                                 append=['volumes', 'detail'],
                                 qs_elements=['marker=01']),
                              'rel': 'next'}]}),
                dict(method='GET',
                     uri=self.get_mock_url(
                         'volumev2', 'public',
                         append=['volumes', 'detail'],
                         qs_elements=['marker=01']),
                     status_code=404)])
        self.register_uris(uris)
        # Check that found volumes are returned even if pagination didn't
        # complete because call to get next link 404'ed for all the allowed
        # attempts
        self.assertEqual(
            [self.cloud._normalize_volume(vol1)],
            self.cloud.list_volumes())
        self.assert_calls()
