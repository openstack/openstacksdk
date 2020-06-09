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
import hashlib
import io
import operator
import tempfile
from unittest import mock

from keystoneauth1 import adapter
import requests

from openstack import _log
from openstack import exceptions
from openstack.image.v2 import image
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'checksum': '1',
    'container_format': '2',
    'created_at': '2015-03-09T12:14:57.233772',
    'data': 'This is not an image',
    'disk_format': '4',
    'min_disk': 5,
    'name': '6',
    'owner': '7',
    'properties': {'a': 'z', 'b': 'y', },
    'protected': False,
    'status': '8',
    'tags': ['g', 'h', 'i'],
    'updated_at': '2015-03-09T12:15:57.233772',
    'os_hash_algo': 'sha512',
    'os_hash_value': '073b4523583784fbe01daff81eba092a262ec3',
    'os_hidden': False,
    'virtual_size': '10',
    'visibility': '11',
    'location': '12',
    'size': 13,
    'store': '14',
    'file': '15',
    'locations': ['15', '16'],
    'direct_url': '17',
    'url': '20',
    'metadata': {'21': '22'},
    'architecture': '23',
    'hypervisor_type': '24',
    'instance_type_rxtx_factor': 25.1,
    'instance_uuid': '26',
    'img_config_drive': '27',
    'kernel_id': '28',
    'os_distro': '29',
    'os_version': '30',
    'os_secure_boot': '31',
    'ramdisk_id': '32',
    'vm_mode': '33',
    'hw_cpu_sockets': 34,
    'hw_cpu_cores': 35,
    'hw_cpu_threads': 36,
    'hw_disk_bus': '37',
    'hw_rng_model': '38',
    'hw_machine_type': '39',
    'hw_scsi_model': '40',
    'hw_serial_port_count': 41,
    'hw_video_model': '42',
    'hw_video_ram': 43,
    'hw_watchdog_action': '44',
    'os_command_line': '45',
    'hw_vif_model': '46',
    'hw_vif_multiqueue_enabled': True,
    'hw_boot_menu': True,
    'vmware_adaptertype': '47',
    'vmware_ostype': '48',
    'auto_disk_config': True,
    'os_type': '49',
    'os_admin_user': 'ubuntu',
    'hw_qemu_guest_agent': True,
    'os_require_quiesce': True,
}


def calculate_md5_checksum(data):
    checksum = hashlib.md5()
    for chunk in data:
        checksum.update(chunk)
    return checksum.hexdigest()


class FakeResponse:
    def __init__(self, response, status_code=200, headers=None, reason=None):
        self.body = response
        self.content = response
        self.text = response
        self.status_code = status_code
        headers = headers if headers else {'content-type': 'application/json'}
        self.headers = requests.structures.CaseInsensitiveDict(headers)
        if reason:
            self.reason = reason
        # for the sake of "list" response faking
        self.links = []

    def json(self):
        return self.body


class TestImage(base.TestCase):

    def setUp(self):
        super(TestImage, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.put = mock.Mock(return_value=FakeResponse({}))
        self.sess.delete = mock.Mock(return_value=FakeResponse({}))
        self.sess.get = mock.Mock(return_value=FakeResponse({}))
        self.sess.default_microversion = None
        self.sess.retriable_status_codes = None
        self.sess.log = _log.setup_logging('openstack')

    def test_basic(self):
        sot = image.Image()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('images', sot.resources_key)
        self.assertEqual('/images', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({'created_at': 'created_at',
                              'is_hidden': 'os_hidden',
                              'limit': 'limit',
                              'marker': 'marker',
                              'member_status': 'member_status',
                              'name': 'name',
                              'owner': 'owner',
                              'protected': 'protected',
                              'size_max': 'size_max',
                              'size_min': 'size_min',
                              'sort': 'sort',
                              'sort_dir': 'sort_dir',
                              'sort_key': 'sort_key',
                              'status': 'status',
                              'tag': 'tag',
                              'updated_at': 'updated_at',
                              'visibility': 'visibility'
                              },
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = image.Image(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['checksum'], sot.checksum)
        self.assertEqual(EXAMPLE['container_format'], sot.container_format)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['disk_format'], sot.disk_format)
        self.assertEqual(EXAMPLE['min_disk'], sot.min_disk)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['owner'], sot.owner)
        self.assertEqual(EXAMPLE['owner'], sot.owner_id)
        self.assertEqual(EXAMPLE['properties'], sot.properties)
        self.assertFalse(sot.is_protected)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tags'], sot.tags)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['os_hash_algo'], sot.hash_algo)
        self.assertEqual(EXAMPLE['os_hash_value'], sot.hash_value)
        self.assertEqual(EXAMPLE['os_hidden'], sot.is_hidden)
        self.assertEqual(EXAMPLE['virtual_size'], sot.virtual_size)
        self.assertEqual(EXAMPLE['visibility'], sot.visibility)
        self.assertEqual(EXAMPLE['size'], sot.size)
        self.assertEqual(EXAMPLE['store'], sot.store)
        self.assertEqual(EXAMPLE['file'], sot.file)
        self.assertEqual(EXAMPLE['locations'], sot.locations)
        self.assertEqual(EXAMPLE['direct_url'], sot.direct_url)
        self.assertEqual(EXAMPLE['url'], sot.url)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['architecture'], sot.architecture)
        self.assertEqual(EXAMPLE['hypervisor_type'], sot.hypervisor_type)
        self.assertEqual(EXAMPLE['instance_type_rxtx_factor'],
                         sot.instance_type_rxtx_factor)
        self.assertEqual(EXAMPLE['instance_uuid'], sot.instance_uuid)
        self.assertEqual(EXAMPLE['img_config_drive'], sot.needs_config_drive)
        self.assertEqual(EXAMPLE['kernel_id'], sot.kernel_id)
        self.assertEqual(EXAMPLE['os_distro'], sot.os_distro)
        self.assertEqual(EXAMPLE['os_version'], sot.os_version)
        self.assertEqual(EXAMPLE['os_secure_boot'], sot.needs_secure_boot)
        self.assertEqual(EXAMPLE['ramdisk_id'], sot.ramdisk_id)
        self.assertEqual(EXAMPLE['vm_mode'], sot.vm_mode)
        self.assertEqual(EXAMPLE['hw_cpu_sockets'], sot.hw_cpu_sockets)
        self.assertEqual(EXAMPLE['hw_cpu_cores'], sot.hw_cpu_cores)
        self.assertEqual(EXAMPLE['hw_cpu_threads'], sot.hw_cpu_threads)
        self.assertEqual(EXAMPLE['hw_disk_bus'], sot.hw_disk_bus)
        self.assertEqual(EXAMPLE['hw_rng_model'], sot.hw_rng_model)
        self.assertEqual(EXAMPLE['hw_machine_type'], sot.hw_machine_type)
        self.assertEqual(EXAMPLE['hw_scsi_model'], sot.hw_scsi_model)
        self.assertEqual(EXAMPLE['hw_serial_port_count'],
                         sot.hw_serial_port_count)
        self.assertEqual(EXAMPLE['hw_video_model'], sot.hw_video_model)
        self.assertEqual(EXAMPLE['hw_video_ram'], sot.hw_video_ram)
        self.assertEqual(EXAMPLE['hw_watchdog_action'], sot.hw_watchdog_action)
        self.assertEqual(EXAMPLE['os_command_line'], sot.os_command_line)
        self.assertEqual(EXAMPLE['hw_vif_model'], sot.hw_vif_model)
        self.assertEqual(EXAMPLE['hw_vif_multiqueue_enabled'],
                         sot.is_hw_vif_multiqueue_enabled)
        self.assertEqual(EXAMPLE['hw_boot_menu'], sot.is_hw_boot_menu_enabled)
        self.assertEqual(EXAMPLE['vmware_adaptertype'], sot.vmware_adaptertype)
        self.assertEqual(EXAMPLE['vmware_ostype'], sot.vmware_ostype)
        self.assertEqual(EXAMPLE['auto_disk_config'], sot.has_auto_disk_config)
        self.assertEqual(EXAMPLE['os_type'], sot.os_type)
        self.assertEqual(EXAMPLE['os_admin_user'], sot.os_admin_user)
        self.assertEqual(EXAMPLE['hw_qemu_guest_agent'],
                         sot.hw_qemu_guest_agent)
        self.assertEqual(EXAMPLE['os_require_quiesce'], sot.os_require_quiesce)

    def test_deactivate(self):
        sot = image.Image(**EXAMPLE)
        self.assertIsNone(sot.deactivate(self.sess))
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/actions/deactivate',
        )

    def test_reactivate(self):
        sot = image.Image(**EXAMPLE)
        self.assertIsNone(sot.reactivate(self.sess))
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/actions/reactivate',
        )

    def test_add_tag(self):
        sot = image.Image(**EXAMPLE)
        tag = "lol"

        sot.add_tag(self.sess, tag)
        self.sess.put.assert_called_with(
            'images/IDENTIFIER/tags/%s' % tag,
        )

    def test_remove_tag(self):
        sot = image.Image(**EXAMPLE)
        tag = "lol"

        sot.remove_tag(self.sess, tag)
        self.sess.delete.assert_called_with(
            'images/IDENTIFIER/tags/%s' % tag,
        )

    def test_import_image(self):
        sot = image.Image(**EXAMPLE)
        json = {"method": {"name": "web-download", "uri": "such-a-good-uri"}}
        sot.import_image(self.sess, "web-download", "such-a-good-uri")
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/import',
            headers={},
            json=json
        )

    def test_import_image_with_uri_not_web_download(self):
        sot = image.Image(**EXAMPLE)

        sot.import_image(self.sess, "glance-direct")
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/import',
            headers={},
            json={"method": {"name": "glance-direct"}}
        )

    def test_import_image_with_store(self):
        sot = image.Image(**EXAMPLE)
        json = {
            "method": {
                "name": "web-download",
                "uri": "such-a-good-uri",
            },
            "stores": ["ceph_1"],
        }
        store = mock.MagicMock()
        store.id = "ceph_1"
        sot.import_image(self.sess, "web-download", "such-a-good-uri", store)
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/import',
            headers={'X-Image-Meta-Store': 'ceph_1'},
            json=json
        )

    def test_import_image_with_stores(self):
        sot = image.Image(**EXAMPLE)
        json = {
            "method": {
                "name": "web-download",
                "uri": "such-a-good-uri",
            },
            "stores": ["ceph_1"],
        }
        store = mock.MagicMock()
        store.id = "ceph_1"
        sot.import_image(
            self.sess,
            "web-download",
            "such-a-good-uri",
            stores=[store],
        )
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/import',
            headers={},
            json=json,
        )

    def test_import_image_with_all_stores(self):
        sot = image.Image(**EXAMPLE)
        json = {
            "method": {
                "name": "web-download",
                "uri": "such-a-good-uri",
            },
            "all_stores": True,
        }
        sot.import_image(
            self.sess,
            "web-download",
            "such-a-good-uri",
            all_stores=True,
        )
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/import',
            headers={},
            json=json,
        )

    def test_upload(self):
        sot = image.Image(**EXAMPLE)

        self.assertIsNotNone(sot.upload(self.sess))
        self.sess.put.assert_called_with('images/IDENTIFIER/file',
                                         data=sot.data,
                                         headers={"Content-Type":
                                                  "application/octet-stream",
                                                  "Accept": ""})

    def test_stage(self):
        sot = image.Image(**EXAMPLE)

        self.assertIsNotNone(sot.stage(self.sess))
        self.sess.put.assert_called_with('images/IDENTIFIER/stage',
                                         data=sot.data,
                                         headers={"Content-Type":
                                                  "application/octet-stream",
                                                  "Accept": ""})

    def test_stage_error(self):
        sot = image.Image(**EXAMPLE)

        self.sess.put.return_value = FakeResponse("dummy", status_code=400)
        self.assertRaises(exceptions.SDKException, sot.stage, self.sess)

    def test_download_checksum_match(self):
        sot = image.Image(**EXAMPLE)

        resp = FakeResponse(
            b"abc",
            headers={"Content-MD5": "900150983cd24fb0d6963f7d28e17f72",
                     "Content-Type": "application/octet-stream"})
        self.sess.get.return_value = resp

        rv = sot.download(self.sess)
        self.sess.get.assert_called_with('images/IDENTIFIER/file',
                                         stream=False)

        self.assertEqual(rv, resp)

    def test_download_checksum_mismatch(self):
        sot = image.Image(**EXAMPLE)

        resp = FakeResponse(
            b"abc",
            headers={"Content-MD5": "the wrong checksum",
                     "Content-Type": "application/octet-stream"})
        self.sess.get.return_value = resp

        self.assertRaises(exceptions.InvalidResponse, sot.download, self.sess)

    def test_download_no_checksum_header(self):
        sot = image.Image(**EXAMPLE)

        resp1 = FakeResponse(
            b"abc", headers={"Content-Type": "application/octet-stream"})

        resp2 = FakeResponse(
            {"checksum": "900150983cd24fb0d6963f7d28e17f72"})

        self.sess.get.side_effect = [resp1, resp2]

        rv = sot.download(self.sess)
        self.sess.get.assert_has_calls(
            [mock.call('images/IDENTIFIER/file',
                       stream=False),
             mock.call('images/IDENTIFIER', microversion=None, params={})])

        self.assertEqual(rv, resp1)

    def test_download_no_checksum_at_all2(self):
        sot = image.Image(**EXAMPLE)

        resp1 = FakeResponse(
            b"abc", headers={"Content-Type": "application/octet-stream"})

        resp2 = FakeResponse({"checksum": None})

        self.sess.get.side_effect = [resp1, resp2]

        with self.assertLogs(logger='openstack', level="WARNING") as log:
            rv = sot.download(self.sess)

            self.assertEqual(len(log.records), 1,
                             "Too many warnings were logged")
            self.assertEqual(
                "Unable to verify the integrity of image %s",
                log.records[0].msg)
            self.assertEqual(
                (sot.id,),
                log.records[0].args)

        self.sess.get.assert_has_calls(
            [mock.call('images/IDENTIFIER/file',
                       stream=False),
             mock.call('images/IDENTIFIER', microversion=None, params={})])

        self.assertEqual(rv, resp1)

    def test_download_stream(self):
        sot = image.Image(**EXAMPLE)

        resp = FakeResponse(
            b"abc",
            headers={"Content-MD5": "900150983cd24fb0d6963f7d28e17f72",
                     "Content-Type": "application/octet-stream"})
        self.sess.get.return_value = resp

        rv = sot.download(self.sess, stream=True)
        self.sess.get.assert_called_with('images/IDENTIFIER/file', stream=True)

        self.assertEqual(rv, resp)

    def test_image_download_output_fd(self):
        output_file = io.BytesIO()
        sot = image.Image(**EXAMPLE)
        response = mock.Mock()
        response.status_code = 200
        response.iter_content.return_value = [b'01', b'02']
        response.headers = {
            'Content-MD5':
            calculate_md5_checksum(response.iter_content.return_value)
        }
        self.sess.get = mock.Mock(return_value=response)
        sot.download(self.sess, output=output_file)
        output_file.seek(0)
        self.assertEqual(b'0102', output_file.read())

    def test_image_download_output_file(self):
        sot = image.Image(**EXAMPLE)
        response = mock.Mock()
        response.status_code = 200
        response.iter_content.return_value = [b'01', b'02']
        response.headers = {
            'Content-MD5':
            calculate_md5_checksum(response.iter_content.return_value)
        }
        self.sess.get = mock.Mock(return_value=response)

        output_file = tempfile.NamedTemporaryFile()
        sot.download(self.sess, output=output_file.name)
        output_file.seek(0)
        self.assertEqual(b'0102', output_file.read())

    def test_image_update(self):
        values = EXAMPLE.copy()
        del values['instance_uuid']
        sot = image.Image.existing(**values)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = mock.Mock()

        resp = mock.Mock()
        resp.content = b"abc"
        headers = {
            'Content-Type': 'application/openstack-images-v2.1-json-patch',
            'Accept': '',
        }
        resp.headers = headers
        resp.status_code = 200
        self.sess.patch.return_value = resp

        value = [{"value": "fake_name", "op": "replace", "path": "/name"},
                 {"value": "fake_value", "op": "add",
                  "path": "/instance_uuid"}]

        sot.name = 'fake_name'
        sot.instance_uuid = 'fake_value'
        sot.commit(self.sess)
        url = 'images/' + IDENTIFIER
        self.sess.patch.assert_called_once()
        call = self.sess.patch.call_args
        call_args, call_kwargs = call
        self.assertEqual(url, call_args[0])
        self.assertEqual(
            sorted(value, key=operator.itemgetter('value')),
            sorted(call_kwargs['json'], key=operator.itemgetter('value')))

    def test_image_find(self):
        sot = image.Image()

        self.sess._get_connection = mock.Mock(return_value=self.cloud)
        self.sess.get.side_effect = [
            # First fetch by name
            FakeResponse(None, 404, headers={}, reason='dummy'),
            # Then list with no results
            FakeResponse({'images': []}),
            # And finally new list of hidden images with one searched
            FakeResponse({'images': [EXAMPLE]})

        ]

        result = sot.find(self.sess, EXAMPLE['name'])

        self.sess.get.assert_has_calls([
            mock.call('images/' + EXAMPLE['name'], microversion=None,
                      params={}),
            mock.call('/images', headers={'Accept': 'application/json'},
                      microversion=None, params={'name': EXAMPLE['name']}),
            mock.call('/images', headers={'Accept': 'application/json'},
                      microversion=None, params={'os_hidden': True})
        ])

        self.assertIsInstance(result, image.Image)
        self.assertEqual(IDENTIFIER, result.id)
