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


import munch

import shade
import testtools
from shade.tests.unit import base


cluster_template_obj = munch.Munch(
    apiserver_port=12345,
    cluster_distro='fake-distro',
    coe='fake-coe',
    created_at='fake-date',
    dns_nameserver='8.8.8.8',
    docker_volume_size=1,
    external_network_id='public',
    fixed_network=None,
    flavor_id='fake-flavor',
    https_proxy=None,
    human_id=None,
    image_id='fake-image',
    insecure_registry='https://192.168.0.10',
    keypair_id='fake-key',
    labels={},
    links={},
    master_flavor_id=None,
    name='fake-cluster-template',
    network_driver='fake-driver',
    no_proxy=None,
    public=False,
    registry_enabled=False,
    server_type='vm',
    tls_disabled=False,
    updated_at=None,
    uuid='fake-uuid',
    volume_driver=None,
)


class TestClusterTemplates(base.RequestsMockTestCase):

    def test_list_cluster_templates_without_detail(self):

        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])
        cluster_templates_list = self.cloud.list_cluster_templates()
        self.assertEqual(
            cluster_templates_list[0],
            self.cloud._normalize_cluster_template(cluster_template_obj))
        self.assert_calls()

    def test_list_cluster_templates_with_detail(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])
        cluster_templates_list = self.cloud.list_cluster_templates(detail=True)
        self.assertEqual(
            cluster_templates_list[0],
            self.cloud._normalize_cluster_template(cluster_template_obj))
        self.assert_calls()

    def test_search_cluster_templates_by_name(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])

        cluster_templates = self.cloud.search_cluster_templates(
            name_or_id='fake-cluster-template')

        self.assertEqual(1, len(cluster_templates))
        self.assertEqual('fake-uuid', cluster_templates[0]['uuid'])
        self.assert_calls()

    def test_search_cluster_templates_not_found(self):

        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])

        cluster_templates = self.cloud.search_cluster_templates(
            name_or_id='non-existent')

        self.assertEqual(0, len(cluster_templates))
        self.assert_calls()

    def test_get_cluster_template(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])

        r = self.cloud.get_cluster_template('fake-cluster-template')
        self.assertIsNotNone(r)
        self.assertDictEqual(
            r, self.cloud._normalize_cluster_template(cluster_template_obj))
        self.assert_calls()

    def test_get_cluster_template_not_found(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[]))])
        r = self.cloud.get_cluster_template('doesNotExist')
        self.assertIsNone(r)
        self.assert_calls()

    def test_create_cluster_template(self):
        self.register_uris([dict(
            method='POST',
            uri='https://container-infra.example.com/v1/baymodels',
            json=dict(baymodels=[cluster_template_obj.toDict()]),
            validate=dict(json={
                'coe': 'fake-coe',
                'image_id': 'fake-image',
                'keypair_id': 'fake-key',
                'name': 'fake-cluster-template'}),
        )])
        self.cloud.create_cluster_template(
            name=cluster_template_obj.name,
            image_id=cluster_template_obj.image_id,
            keypair_id=cluster_template_obj.keypair_id,
            coe=cluster_template_obj.coe)
        self.assert_calls()

    def test_create_cluster_template_exception(self):
        self.register_uris([dict(
            method='POST',
            uri='https://container-infra.example.com/v1/baymodels',
            status_code=403)])
        # TODO(mordred) requests here doens't give us a great story
        # for matching the old error message text. Investigate plumbing
        # an error message in to the adapter call so that we can give a
        # more informative error. Also, the test was originally catching
        # OpenStackCloudException - but for some reason testtools will not
        # match the more specific HTTPError, even though it's a subclass
        # of OpenStackCloudException.
        with testtools.ExpectedException(shade.OpenStackCloudHTTPError):
            self.cloud.create_cluster_template('fake-cluster-template')
        self.assert_calls()

    def test_delete_cluster_template(self):
        uri = 'https://container-infra.example.com/v1/baymodels/fake-uuid'
        self.register_uris([
            dict(
                method='GET',
                uri='https://container-infra.example.com/v1/baymodels/detail',
                json=dict(baymodels=[cluster_template_obj.toDict()])),
            dict(
                method='DELETE',
                uri=uri),
        ])
        self.cloud.delete_cluster_template('fake-uuid')
        self.assert_calls()

    def test_update_cluster_template(self):
        uri = 'https://container-infra.example.com/v1/baymodels/fake-uuid'
        self.register_uris([
            dict(
                method='GET',
                uri='https://container-infra.example.com/v1/baymodels/detail',
                json=dict(baymodels=[cluster_template_obj.toDict()])),
            dict(
                method='PATCH',
                uri=uri,
                status_code=200,
                validate=dict(
                    json=[{
                        u'op': u'replace',
                        u'path': u'/name',
                        u'value': u'new-cluster-template'
                    }]
                )),
            dict(
                method='GET',
                uri='https://container-infra.example.com/v1/baymodels/detail',
                # This json value is not meaningful to the test - it just has
                # to be valid.
                json=dict(baymodels=[cluster_template_obj.toDict()])),
        ])
        new_name = 'new-cluster-template'
        self.cloud.update_cluster_template(
            'fake-uuid', 'replace', name=new_name)
        self.assert_calls()
