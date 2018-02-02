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

import mock
from openstack.tests.unit import base

from openstack.compute.v2 import server

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'accessIPv4': '1',
    'accessIPv6': '2',
    'addresses': {'region': '3'},
    'config_drive': True,
    'created': '2015-03-09T12:14:57.233772',
    'flavorRef': '5',
    'flavor': {'id': 'FLAVOR_ID', 'links': {}},
    'hostId': '6',
    'id': IDENTIFIER,
    'imageRef': '8',
    'image': {'id': 'IMAGE_ID', 'links': {}},
    'links': '9',
    'metadata': {'key': '10'},
    'networks': 'auto',
    'name': '11',
    'progress': 12,
    'tenant_id': '13',
    'status': '14',
    'updated': '2015-03-09T12:15:57.233772',
    'user_id': '16',
    'key_name': '17',
    'OS-DCF:diskConfig': '18',
    'OS-EXT-AZ:availability_zone': '19',
    'OS-EXT-STS:power_state': '20',
    'OS-EXT-STS:task_state': '21',
    'OS-EXT-STS:vm_state': '22',
    'os-extended-volumes:volumes_attached': '23',
    'OS-SRV-USG:launched_at': '2015-03-09T12:15:57.233772',
    'OS-SRV-USG:terminated_at': '2015-03-09T12:15:57.233772',
    'security_groups': '26',
    'adminPass': '27',
    'personality': '28',
    'block_device_mapping_v2': {'key': '29'},
    'OS-EXT-SRV-ATTR:hypervisor_hostname': 'hypervisor.example.com',
    'OS-EXT-SRV-ATTR:instance_name': 'instance-00000001',
    'OS-SCH-HNT:scheduler_hints': {'key': '30'},
    'OS-EXT-SRV-ATTR:user_data': '31'
}


class TestServer(base.TestCase):

    def setUp(self):
        super(TestServer, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = server.Server()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"image": "image",
                              "flavor": "flavor",
                              "name": "name",
                              "status": "status",
                              "host": "host",
                              "all_tenants": "all_tenants",
                              "changes_since": "changes-since",
                              "limit": "limit",
                              "marker": "marker",
                              "sort_key": "sort_key",
                              "sort_dir": "sort_dir",
                              "reservation_id": "reservation_id",
                              "project_id": "project_id",
                              "tags": "tags",
                              "tags_any": "tags-any",
                              "not_tags": "not-tags",
                              "not_tags_any": "not-tags-any",
                              "is_deleted": "deleted",
                              "ipv4_address": "ip",
                              "ipv6_address": "ip6",
                              },
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = server.Server(**EXAMPLE)
        self.assertEqual(EXAMPLE['accessIPv4'], sot.access_ipv4)
        self.assertEqual(EXAMPLE['accessIPv6'], sot.access_ipv6)
        self.assertEqual(EXAMPLE['addresses'], sot.addresses)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['config_drive'], sot.has_config_drive)
        self.assertEqual(EXAMPLE['flavorRef'], sot.flavor_id)
        self.assertEqual(EXAMPLE['flavor'], sot.flavor)
        self.assertEqual(EXAMPLE['hostId'], sot.host_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['imageRef'], sot.image_id)
        self.assertEqual(EXAMPLE['image'], sot.image)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['networks'], sot.networks)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['progress'], sot.progress)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
        self.assertEqual(EXAMPLE['key_name'], sot.key_name)
        self.assertEqual(EXAMPLE['OS-DCF:diskConfig'], sot.disk_config)
        self.assertEqual(EXAMPLE['OS-EXT-AZ:availability_zone'],
                         sot.availability_zone)
        self.assertEqual(EXAMPLE['OS-EXT-STS:power_state'], sot.power_state)
        self.assertEqual(EXAMPLE['OS-EXT-STS:task_state'], sot.task_state)
        self.assertEqual(EXAMPLE['OS-EXT-STS:vm_state'], sot.vm_state)
        self.assertEqual(EXAMPLE['os-extended-volumes:volumes_attached'],
                         sot.attached_volumes)
        self.assertEqual(EXAMPLE['OS-SRV-USG:launched_at'], sot.launched_at)
        self.assertEqual(EXAMPLE['OS-SRV-USG:terminated_at'],
                         sot.terminated_at)
        self.assertEqual(EXAMPLE['security_groups'], sot.security_groups)
        self.assertEqual(EXAMPLE['adminPass'], sot.admin_password)
        self.assertEqual(EXAMPLE['personality'], sot.personality)
        self.assertEqual(EXAMPLE['block_device_mapping_v2'],
                         sot.block_device_mapping)
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:hypervisor_hostname'],
                         sot.hypervisor_hostname)
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:instance_name'],
                         sot.instance_name)
        self.assertEqual(EXAMPLE['OS-SCH-HNT:scheduler_hints'],
                         sot.scheduler_hints)
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:user_data'], sot.user_data)

    def test_detail(self):
        sot = server.ServerDetail()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers/detail', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test__prepare_server(self):
        zone = 1
        data = 2
        hints = {"hint": 3}

        sot = server.Server(id=1, availability_zone=zone, user_data=data,
                            scheduler_hints=hints)
        request = sot._prepare_request()

        self.assertNotIn("OS-EXT-AZ:availability_zone",
                         request.body[sot.resource_key])
        self.assertEqual(request.body[sot.resource_key]["availability_zone"],
                         zone)

        self.assertNotIn("OS-EXT-SRV-ATTR:user_data",
                         request.body[sot.resource_key])
        self.assertEqual(request.body[sot.resource_key]["user_data"],
                         data)

        self.assertNotIn("OS-SCH-HNT:scheduler_hints",
                         request.body[sot.resource_key])
        self.assertEqual(request.body["OS-SCH-HNT:scheduler_hints"], hints)

    def test_change_password(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.change_password(self.sess, 'a'))

        url = 'servers/IDENTIFIER/action'
        body = {"changePassword": {"adminPass": "a"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_reboot(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.reboot(self.sess, 'HARD'))

        url = 'servers/IDENTIFIER/action'
        body = {"reboot": {"type": "HARD"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_force_delete(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.force_delete(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {'forceDelete': None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_rebuild(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(self.sess, name='noo', admin_password='seekr3t',
                             image='http://image/1', access_ipv4="12.34.56.78",
                             access_ipv6="fe80::100",
                             metadata={"meta var": "meta val"},
                             personality=[{"path": "/etc/motd",
                                           "contents": "foo"}])

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "noo",
                "imageRef": "http://image/1",
                "adminPass": "seekr3t",
                "accessIPv4": "12.34.56.78",
                "accessIPv6": "fe80::100",
                "metadata": {"meta var": "meta val"},
                "personality": [{"path": "/etc/motd", "contents": "foo"}],
                "preserve_ephemeral": False
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_rebuild_minimal(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(self.sess, name='nootoo',
                             admin_password='seekr3two',
                             image='http://image/2')

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "nootoo",
                "imageRef": "http://image/2",
                "adminPass": "seekr3two",
                "preserve_ephemeral": False
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.resize(self.sess, '2'))

        url = 'servers/IDENTIFIER/action'
        body = {"resize": {"flavorRef": "2"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_confirm_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.confirm_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"confirmResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_revert_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.revert_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"revertResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_create_image(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'
        metadata = {'nu': 'image', 'created': 'today'}

        self.assertIsNone(sot.create_image(self.sess, name, metadata))

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name, 'metadata': metadata}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_create_image_minimal(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'

        self.assertIsNone(self.resp.body, sot.create_image(self.sess, name))

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_add_security_group(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.add_security_group(self.sess, "group"))

        url = 'servers/IDENTIFIER/action'
        body = {"addSecurityGroup": {"name": "group"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_remove_security_group(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.remove_security_group(self.sess, "group"))

        url = 'servers/IDENTIFIER/action'
        body = {"removeSecurityGroup": {"name": "group"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_reset_state(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.reset_state(self.sess, 'active'))

        url = 'servers/IDENTIFIER/action'
        body = {"os-resetState": {"state": 'active'}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_add_fixed_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.add_fixed_ip(self.sess, "NETWORK-ID")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"addFixedIp": {"networkId": "NETWORK-ID"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_remove_fixed_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.remove_fixed_ip(self.sess, "ADDRESS")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"removeFixedIp": {"address": "ADDRESS"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_add_floating_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.add_floating_ip(self.sess, "FLOATING-IP")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"addFloatingIp": {"address": "FLOATING-IP"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_add_floating_ip_with_fixed_addr(self):
        sot = server.Server(**EXAMPLE)

        res = sot.add_floating_ip(self.sess, "FLOATING-IP", "FIXED-ADDR")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"addFloatingIp": {"address": "FLOATING-IP",
                                  "fixed_address": "FIXED-ADDR"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_remove_floating_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.remove_floating_ip(self.sess, "I-AM-FLOATING")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"removeFloatingIp": {"address": "I-AM-FLOATING"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_backup(self):
        sot = server.Server(**EXAMPLE)

        res = sot.backup(self.sess, "name", "daily", 1)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"createBackup": {"name": "name", "backup_type": "daily",
                                 "rotation": 1}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_pause(self):
        sot = server.Server(**EXAMPLE)

        res = sot.pause(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"pause": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_unpause(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unpause(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unpause": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_suspend(self):
        sot = server.Server(**EXAMPLE)

        res = sot.suspend(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"suspend": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_resume(self):
        sot = server.Server(**EXAMPLE)

        res = sot.resume(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"resume": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_lock(self):
        sot = server.Server(**EXAMPLE)

        res = sot.lock(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"lock": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_unlock(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unlock(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unlock": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_rescue(self):
        sot = server.Server(**EXAMPLE)

        res = sot.rescue(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"rescue": {}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_rescue_with_options(self):
        sot = server.Server(**EXAMPLE)

        res = sot.rescue(self.sess, admin_pass='SECRET', image_ref='IMG-ID')

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"rescue": {'adminPass': 'SECRET',
                           'rescue_image_ref': 'IMG-ID'}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_unrescue(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unrescue(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unrescue": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_evacuate(self):
        sot = server.Server(**EXAMPLE)

        res = sot.evacuate(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"evacuate": {}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_evacuate_with_options(self):
        sot = server.Server(**EXAMPLE)

        res = sot.evacuate(self.sess, host='HOST2', admin_pass='NEW_PASS',
                           force=True)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"evacuate": {'host': 'HOST2', 'adminPass': 'NEW_PASS',
                             'force': True}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_start(self):
        sot = server.Server(**EXAMPLE)

        res = sot.start(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"os-start": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_stop(self):
        sot = server.Server(**EXAMPLE)

        res = sot.stop(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"os-stop": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_shelve(self):
        sot = server.Server(**EXAMPLE)

        res = sot.shelve(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"shelve": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_unshelve(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unshelve(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unshelve": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_migrate(self):
        sot = server.Server(**EXAMPLE)

        res = sot.migrate(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"migrate": None}

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_get_console_output(self):
        sot = server.Server(**EXAMPLE)

        res = sot.get_console_output(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'os-getConsoleOutput': {}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

        res = sot.get_console_output(self.sess, length=1)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'os-getConsoleOutput': {'length': 1}}

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)

    def test_live_migrate(self):
        sot = server.Server(**EXAMPLE)

        res = sot.live_migrate(self.sess, host='HOST2', force=False)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "os-migrateLive": {
                "host": 'HOST2',
                "block_migration": "auto",
                "force": False
            }
        }

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers)
