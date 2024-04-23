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

from openstack.container_infrastructure_management.v1 import cluster_template
from openstack import exceptions
from openstack.tests.unit import base


cluster_template_obj = dict(
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


class TestClusterTemplates(base.TestCase):
    def _compare_clustertemplates(self, exp, real):
        self.assertDictEqual(
            cluster_template.ClusterTemplate(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def get_mock_url(
        self,
        service_type='container-infrastructure-management',
        base_url_append=None,
        append=None,
        resource=None,
    ):
        return super().get_mock_url(
            service_type=service_type,
            resource=resource,
            append=append,
            base_url_append=base_url_append,
        )

    def test_list_cluster_templates_without_detail(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                )
            ]
        )
        cluster_templates_list = self.cloud.list_cluster_templates()
        self._compare_clustertemplates(
            cluster_template_obj,
            cluster_templates_list[0],
        )
        self.assert_calls()

    def test_list_cluster_templates_with_detail(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                )
            ]
        )
        cluster_templates_list = self.cloud.list_cluster_templates(detail=True)
        self._compare_clustertemplates(
            cluster_template_obj,
            cluster_templates_list[0],
        )
        self.assert_calls()

    def test_search_cluster_templates_by_name(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                )
            ]
        )

        cluster_templates = self.cloud.search_cluster_templates(
            name_or_id='fake-cluster-template'
        )

        self.assertEqual(1, len(cluster_templates))
        self.assertEqual('fake-uuid', cluster_templates[0]['uuid'])
        self.assert_calls()

    def test_search_cluster_templates_not_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                )
            ]
        )

        cluster_templates = self.cloud.search_cluster_templates(
            name_or_id='non-existent'
        )

        self.assertEqual(0, len(cluster_templates))
        self.assert_calls()

    def test_get_cluster_template(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                )
            ]
        )

        r = self.cloud.get_cluster_template('fake-cluster-template')
        self.assertIsNotNone(r)
        self._compare_clustertemplates(
            cluster_template_obj,
            r,
        )
        self.assert_calls()

    def test_get_cluster_template_not_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[]),
                )
            ]
        )
        r = self.cloud.get_cluster_template('doesNotExist')
        self.assertIsNone(r)
        self.assert_calls()

    def test_create_cluster_template(self):
        json_response = cluster_template_obj.copy()
        kwargs = dict(
            name=cluster_template_obj['name'],
            image_id=cluster_template_obj['image_id'],
            keypair_id=cluster_template_obj['keypair_id'],
            coe=cluster_template_obj['coe'],
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=json_response,
                    validate=dict(json=kwargs),
                )
            ]
        )
        response = self.cloud.create_cluster_template(**kwargs)
        self._compare_clustertemplates(json_response, response)

        self.assert_calls()

    def test_create_cluster_template_exception(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    status_code=403,
                )
            ]
        )
        # TODO(mordred) requests here doens't give us a great story
        # for matching the old error message text. Investigate plumbing
        # an error message in to the adapter call so that we can give a
        # more informative error. Also, the test was originally catching
        # SDKException - but for some reason testtools will not
        # match the more specific HTTPError, even though it's a subclass
        # of SDKException.
        with testtools.ExpectedException(exceptions.ForbiddenException):
            self.cloud.create_cluster_template('fake-cluster-template')
        self.assert_calls()

    def test_delete_cluster_template(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='clustertemplates/fake-uuid'
                    ),
                ),
            ]
        )
        self.cloud.delete_cluster_template('fake-uuid')
        self.assert_calls()

    def test_update_cluster_template(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                ),
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(
                        resource='clustertemplates/fake-uuid'
                    ),
                    status_code=200,
                    validate=dict(
                        json=[
                            {
                                'op': 'replace',
                                'path': '/name',
                                'value': 'new-cluster-template',
                            }
                        ]
                    ),
                ),
            ]
        )
        new_name = 'new-cluster-template'
        updated = self.cloud.update_cluster_template(
            'fake-uuid', name=new_name
        )
        self.assertEqual(new_name, updated.name)
        self.assert_calls()

    def test_coe_get_cluster_template(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='clustertemplates'),
                    json=dict(clustertemplates=[cluster_template_obj]),
                )
            ]
        )

        r = self.cloud.get_cluster_template('fake-cluster-template')
        self.assertIsNotNone(r)
        self._compare_clustertemplates(
            cluster_template_obj,
            r,
        )
        self.assert_calls()
