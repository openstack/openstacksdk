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

from unittest import mock

from openstack.network.v2 import agent
from openstack.network.v2 import bgp_speaker
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'name': 'bgp-speaker',
    'peers': [],
    'ip_version': 4,
    'advertise_floating_ip_host_routes': 'true',
    'advertise_tenant_networks': 'true',
    'local_as': 1000,
    'networks': [],
    'project_id': '42',
}


class TestBgpSpeaker(base.TestCase):
    def test_basic(self):
        sot = bgp_speaker.BgpSpeaker()
        self.assertEqual('bgp_speaker', sot.resource_key)
        self.assertEqual('bgp_speakers', sot.resources_key)
        self.assertEqual('/bgp-speakers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertEqual(
            EXAMPLE['advertise_floating_ip_host_routes'],
            sot.advertise_floating_ip_host_routes,
        )
        self.assertEqual(EXAMPLE['local_as'], sot.local_as)
        self.assertEqual(EXAMPLE['networks'], sot.networks)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_add_bgp_peer(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        response = mock.Mock()
        response.body = {'bgp_peer_id': '101'}
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        ret = sot.add_bgp_peer(sess, '101')
        self.assertIsInstance(ret, dict)
        self.assertEqual(ret, {'bgp_peer_id': '101'})

        body = {'bgp_peer_id': '101'}
        url = 'bgp-speakers/IDENTIFIER/add_bgp_peer'
        sess.put.assert_called_with(url, json=body)

    def test_remove_bgp_peer(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        response = mock.Mock()
        response.body = {'bgp_peer_id': '102'}
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        ret = sot.remove_bgp_peer(sess, '102')
        self.assertIsNone(ret)

        body = {'bgp_peer_id': '102'}
        url = 'bgp-speakers/IDENTIFIER/remove_bgp_peer'
        sess.put.assert_called_with(url, json=body)

    def test_add_gateway_network(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        response = mock.Mock()
        response.body = {'network_id': 'net_id'}
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        ret = sot.add_gateway_network(sess, 'net_id')
        self.assertIsInstance(ret, dict)
        self.assertEqual(ret, {'network_id': 'net_id'})

        body = {'network_id': 'net_id'}
        url = 'bgp-speakers/IDENTIFIER/add_gateway_network'
        sess.put.assert_called_with(url, json=body)

    def test_remove_gateway_network(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        response = mock.Mock()
        response.body = {'network_id': 'net_id42'}
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        ret = sot.remove_gateway_network(sess, 'net_id42')
        self.assertIsNone(ret)

        body = {'network_id': 'net_id42'}
        url = 'bgp-speakers/IDENTIFIER/remove_gateway_network'
        sess.put.assert_called_with(url, json=body)

    def test_get_advertised_routes(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        response = mock.Mock()
        response.body = {
            'advertised_routes': [
                {'cidr': '192.168.10.0/24', 'nexthop': '10.0.0.1'}
            ]
        }
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.get = mock.Mock(return_value=response)
        ret = sot.get_advertised_routes(sess)

        url = 'bgp-speakers/IDENTIFIER/get_advertised_routes'
        sess.get.assert_called_with(url)
        self.assertEqual(ret, response.body)

    @mock.patch.object(agent.Agent, 'list')
    def test_get_bgp_dragents(self, mock_list):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        response = mock.Mock()
        agent_body = {
            'agents': [
                {
                    'binary': 'neutron-bgp-dragent',
                    'alive': True,
                    'id': IDENTIFIER,
                }
            ]
        }
        response.body = agent_body
        mock_list.return_value = [agent.Agent(**agent_body['agents'][0])]
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.get = mock.Mock(return_value=response)
        ret = sot.get_bgp_dragents(sess)

        url = 'bgp-speakers/IDENTIFIER/bgp-dragents'
        sess.get.assert_called_with(url)
        self.assertEqual(ret, [agent.Agent(**response.body['agents'][0])])

    def test_add_bgp_speaker_to_dragent(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        agent_id = '123-42'
        response = mock.Mock()
        response.status_code = 201
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)
        self.assertIsNone(sot.add_bgp_speaker_to_dragent(sess, agent_id))

        body = {'bgp_speaker_id': sot.id}
        url = f'agents/{agent_id}/bgp-drinstances'
        sess.post.assert_called_with(url, json=body)

    def test_remove_bgp_speaker_from_dragent(self):
        sot = bgp_speaker.BgpSpeaker(**EXAMPLE)
        agent_id = '123-42'
        response = mock.Mock()
        response.status_code = 204
        sess = mock.Mock()
        sess.delete = mock.Mock(return_value=response)
        self.assertIsNone(sot.remove_bgp_speaker_from_dragent(sess, agent_id))

        url = f'agents/{agent_id}/bgp-drinstances/{IDENTIFIER}'
        sess.delete.assert_called_with(url)
