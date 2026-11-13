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

from openstack import exceptions
from openstack.key_manager.v1 import _proxy
from openstack.key_manager.v1 import container
from openstack.key_manager.v1 import container_acl
from openstack.key_manager.v1 import order
from openstack.key_manager.v1 import project_quota
from openstack.key_manager.v1 import quota
from openstack.key_manager.v1 import secret
from openstack.key_manager.v1 import secret_acl
from openstack.key_manager.v1 import secret_consumer
from openstack.key_manager.v1 import secret_store
from openstack.tests.unit import test_proxy_base


class TestKeyManagerProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestKeyManagerContainer(TestKeyManagerProxy):
    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_container, container.Container)

    def test_container_delete(self):
        self.verify_delete(
            self.proxy.delete_container, container.Container, False
        )

    def test_container_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_container, container.Container, True
        )

    def test_container_find(self):
        self.verify_find(self.proxy.find_container, container.Container)

    def test_container_get(self):
        self.verify_get(self.proxy.get_container, container.Container)

    def test_containers(self):
        self.verify_list(self.proxy.containers, container.Container)

    def test_container_update(self):
        self.verify_update(self.proxy.update_container, container.Container)


class TestKeyManagerOrder(TestKeyManagerProxy):
    def test_order_create_attrs(self):
        self.verify_create(self.proxy.create_order, order.Order)

    def test_order_delete(self):
        self.verify_delete(self.proxy.delete_order, order.Order, False)

    def test_order_delete_ignore(self):
        self.verify_delete(self.proxy.delete_order, order.Order, True)

    def test_order_find(self):
        self.verify_find(self.proxy.find_order, order.Order)

    def test_order_get(self):
        self.verify_get(self.proxy.get_order, order.Order)

    def test_orders(self):
        self.verify_list(self.proxy.orders, order.Order)

    def test_order_update(self):
        self.verify_update(self.proxy.update_order, order.Order)


class TestKeyManagerSecret(TestKeyManagerProxy):
    def test_secret_create_attrs(self):
        self.verify_create(self.proxy.create_secret, secret.Secret)

    def test_secret_delete(self):
        self.verify_delete(self.proxy.delete_secret, secret.Secret, False)

    def test_secret_delete_ignore(self):
        self.verify_delete(self.proxy.delete_secret, secret.Secret, True)

    def test_secret_find(self):
        self.verify_find(self.proxy.find_secret, secret.Secret)
        with mock.patch.object(self.proxy, '_find') as find:
            result = self.proxy.find_secret('name')
        find.assert_called_once_with(
            secret.Secret, 'name', ignore_missing=True
        )
        find.return_value.fetch_payload.assert_not_called()
        self.assertIs(find.return_value, result)

    def test_secret_find_with_payload(self):
        with mock.patch.object(self.proxy, '_find') as find:
            result = self.proxy.find_secret(
                'name', ignore_missing=False, get_payload=True
            )
        find.assert_called_once_with(
            secret.Secret, 'name', ignore_missing=False
        )
        find.return_value.fetch_payload.assert_called_once_with(self.proxy)
        self.assertIs(find.return_value.fetch_payload.return_value, result)

    def test_secret_find_without_payload(self):
        with mock.patch.object(self.proxy, '_find') as find:
            result = self.proxy.find_secret('name', get_payload=False)
        find.assert_called_once_with(
            secret.Secret, 'name', ignore_missing=True
        )
        find.return_value.fetch_payload.assert_not_called()
        self.assertIs(find.return_value, result)

    def test_secret_find_missing_with_payload(self):
        with mock.patch.object(self.proxy, '_find', return_value=None) as find:
            self.assertIsNone(self.proxy.find_secret('name', get_payload=True))
        find.assert_called_once_with(
            secret.Secret, 'name', ignore_missing=True
        )

    def test_secret_get(self):
        with mock.patch.object(self.proxy, '_get') as get:
            result = self.proxy.get_secret('id')
        get.assert_called_once_with(secret.Secret, 'id')
        get.return_value.fetch_payload.assert_called_once_with(self.proxy)
        self.assertIs(get.return_value.fetch_payload.return_value, result)

    def test_secret_get_metadata(self):
        with mock.patch.object(self.proxy, '_get') as get:
            result = self.proxy.get_secret('id', get_payload=False)
        get.assert_called_once_with(secret.Secret, 'id')
        get.return_value.fetch_payload.assert_not_called()
        self.assertIs(get.return_value, result)

    def test_secret_payload_flags_keyword_only(self):
        self.assertRaises(TypeError, self.proxy.get_secret, 'id', False)
        self.assertRaises(TypeError, self.proxy.find_secret, 'id', True, True)

    def test_secret_fetch_payload(self):
        resource = secret.Secret(
            id='id', content_types={'default': 'application/octet-stream'}
        )
        with mock.patch.object(self.proxy, '_get') as get:
            self._verify(
                'openstack.key_manager.v1.secret.Secret.fetch_payload',
                self.proxy.fetch_secret_payload,
                method_args=[resource],
                expected_args=[self.proxy],
                expected_kwargs={},
            )
        get.assert_not_called()
        self.assertEqual(
            {'default': 'application/octet-stream'}, resource.content_types
        )

    def test_secret_fetch_payload_by_id(self):
        with (
            mock.patch.object(
                secret.Secret, 'fetch_payload', autospec=True
            ) as fetch,
            mock.patch.object(self.proxy, '_get') as get,
        ):
            result = self.proxy.fetch_secret_payload(
                'id', content_type='application/octet-stream'
            )
        get.assert_not_called()
        fetched_secret = fetch.call_args.args[0]
        self.assertEqual('id', fetched_secret.id)
        self.assertEqual(
            'application/octet-stream', fetched_secret.payload_content_type
        )
        fetch.assert_called_once_with(fetched_secret, self.proxy)
        self.assertIs(fetch.return_value, result)

    def test_secret_fetch_payload_by_id_requires_content_type(self):
        for content_type in (None, ''):
            with self.subTest(content_type=content_type):
                self.assertRaises(
                    ValueError,
                    self.proxy.fetch_secret_payload,
                    'id',
                    content_type=content_type,
                )

    def test_secret_fetch_payload_content_type_override(self):
        resource = secret.Secret(
            id='id', payload_content_type='application/octet-stream'
        )
        with mock.patch.object(
            secret.Secret, 'fetch_payload', autospec=True
        ) as fetch:
            result = self.proxy.fetch_secret_payload(
                resource, content_type='text/plain'
            )
        fetch.assert_called_once_with(resource, self.proxy)
        self.assertEqual('text/plain', resource.payload_content_type)
        self.assertIs(fetch.return_value, result)

    def test_secret_fetch_payload_content_type_keyword_only(self):
        self.assertRaises(
            TypeError,
            self.proxy.fetch_secret_payload,
            'id',
            'application/octet-stream',
        )

    def test_secrets(self):
        self.verify_list(self.proxy.secrets, secret.Secret)

    def test_secret_update(self):
        self.verify_update(self.proxy.update_secret, secret.Secret)

    @mock.patch(
        'openstack.key_manager.v1._proxy._microversion.supports_microversion',
        return_value=True,
    )
    def test_migrate_secret_store(self, _mock_mv):
        self._verify(
            "openstack.key_manager.v1.secret.Secret.migrate_store",
            self.proxy.migrate_secret_store,
            method_args=["id", "ss-id"],
            expected_args=[mock.ANY, "ss-id"],
            expected_kwargs={},
        )

    @mock.patch(
        'openstack.key_manager.v1._proxy._microversion.supports_microversion',
        return_value=True,
    )
    def test_migrate_secret_store_href(self, _mock_mv):
        store_id = '11111111-1111-1111-1111-111111111111'
        store_ref = f'http://localhost:9311/v1/secret-stores/{store_id}'
        self._verify(
            "openstack.key_manager.v1.secret.Secret.migrate_store",
            self.proxy.migrate_secret_store,
            method_args=["id", store_ref],
            expected_args=[mock.ANY, store_id],
            expected_kwargs={},
        )

    @mock.patch(
        'openstack.key_manager.v1._proxy._microversion.supports_microversion',
        return_value=True,
    )
    def test_migrate_secret_store_resource(self, _mock_mv):
        store_id = '11111111-1111-1111-1111-111111111111'
        store_ref = f'http://localhost:9311/v1/secret-stores/{store_id}'
        store = secret_store.SecretStore(secret_store_ref=store_ref)
        self._verify(
            "openstack.key_manager.v1.secret.Secret.migrate_store",
            self.proxy.migrate_secret_store,
            method_args=["id", store],
            expected_args=[mock.ANY, store_id],
            expected_kwargs={},
        )

    @mock.patch(
        'openstack.key_manager.v1._proxy._microversion.supports_microversion',
        return_value=False,
    )
    def test_migrate_secret_store_requires_microversion(self, _mock_mv):
        self.assertRaises(
            exceptions.SDKException,
            self.proxy.migrate_secret_store,
            "id",
            "ss-id",
        )


class TestKeyManagerQuota(TestKeyManagerProxy):
    def test_quota_get(self):
        self.verify_get(
            self.proxy.get_quota,
            quota.Quota,
            requires_id=False,
            method_args=[],
            expected_kwargs={'requires_id': False},
        )


class TestKeyManagerSecretStore(TestKeyManagerProxy):
    def test_secret_stores(self):
        self.verify_list(self.proxy.secret_stores, secret_store.SecretStore)


class TestKeyManagerProjectQuota(TestKeyManagerProxy):
    def test_project_quota_delete(self):
        self.verify_delete(
            self.proxy.delete_project_quota, project_quota.ProjectQuota, False
        )

    def test_project_quota_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_project_quota, project_quota.ProjectQuota, True
        )

    def test_project_quota_get(self):
        self.verify_get(
            self.proxy.get_project_quota, project_quota.ProjectQuota
        )

    def test_project_quota_update(self):
        self.verify_update(
            self.proxy.update_project_quota, project_quota.ProjectQuota
        )


class TestKeyManagerSecretACL(TestKeyManagerProxy):
    def test_get_secret_acl(self):
        self.verify_get(
            self.proxy.get_secret_acl,
            secret_acl.SecretACL,
            expected_args=[None],
            expected_kwargs={
                "requires_id": False,
                "secret_id": "resource_id",
            },
        )

    def test_set_secret_acl(self):
        self.verify_update(
            self.proxy.set_secret_acl,
            secret_acl.SecretACL,
            expected_args=[None],
            expected_kwargs={
                "secret_id": "resource_id",
                "x": 1,
                "y": 2,
                "z": 3,
            },
        )

    def test_update_secret_acl(self):
        self.verify_update(
            self.proxy.update_secret_acl,
            secret_acl.SecretACL,
            expected_args=[None],
            expected_kwargs={
                "secret_id": "resource_id",
                "x": 1,
                "y": 2,
                "z": 3,
            },
        )

    def test_delete_secret_acl(self):
        self.verify_delete(
            self.proxy.delete_secret_acl,
            secret_acl.SecretACL,
            False,
            expected_args=[None],
            expected_kwargs={
                "secret_id": "resource_id",
            },
        )


class TestKeyManagerContainerACL(TestKeyManagerProxy):
    def test_get_container_acl(self):
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_container_acl,
            method_args=['container-id'],
            expected_args=[container_acl.ContainerACL, None],
            expected_kwargs={
                'requires_id': False,
                'container_id': 'container-id',
            },
        )

    def test_create_container_acl(self):
        self._verify(
            'openstack.proxy.Proxy._create',
            self.proxy.create_container_acl,
            method_args=['container-id'],
            method_kwargs={
                'read': {'users': ['user1'], 'project-access': False},
            },
            expected_args=[container_acl.ContainerACL],
            expected_kwargs={
                'container_id': 'container-id',
                'read': {'users': ['user1'], 'project-access': False},
            },
        )

    def test_update_container_acl(self):
        self._verify(
            'openstack.proxy.Proxy._update',
            self.proxy.update_container_acl,
            method_args=['container-id'],
            method_kwargs={'read': {'project-access': True}},
            expected_args=[container_acl.ContainerACL, None],
            expected_kwargs={
                'container_id': 'container-id',
                'read': {'project-access': True},
            },
        )

    def test_delete_container_acl(self):
        self._verify(
            'openstack.proxy.Proxy._delete',
            self.proxy.delete_container_acl,
            method_args=['container-id'],
            method_kwargs={'ignore_missing': False},
            expected_args=[container_acl.ContainerACL, None],
            expected_kwargs={
                'container_id': 'container-id',
                'ignore_missing': False,
            },
        )

    def test_delete_container_acl_ignore(self):
        self._verify(
            'openstack.proxy.Proxy._delete',
            self.proxy.delete_container_acl,
            method_args=['container-id'],
            method_kwargs={'ignore_missing': True},
            expected_args=[container_acl.ContainerACL, None],
            expected_kwargs={
                'container_id': 'container-id',
                'ignore_missing': True,
            },
        )


class TestKeyManagerSecretConsumer(TestKeyManagerProxy):
    def test_secret_consumer_create(self):
        self.verify_create(
            self.proxy.create_secret_consumer,
            secret_consumer.SecretConsumer,
            method_args=["secret-id"],
            method_kwargs={
                "service": "svc",
                "resource_type": "type",
                "resource_id": "rid",
            },
            expected_args=[],
            expected_kwargs={
                "secret_id": "secret-id",
                "service": "svc",
                "__conflicting_attrs": {"resource_type": "type"},
                "resource_id": "rid",
            },
        )

    def test_secret_consumers(self):
        self.verify_list(
            self.proxy.secret_consumers,
            secret_consumer.SecretConsumer,
            method_args=["secret-id"],
            expected_args=[],
            expected_kwargs={"secret_id": "secret-id"},
        )

    def test_secret_consumer_delete(self):
        self._verify(
            "openstack.key_manager.v1.secret_consumer.SecretConsumer.delete",
            self.proxy.delete_secret_consumer,
            method_args=["secret-id"],
            method_kwargs={
                "service": "svc",
                "resource_type": "type",
                "resource_id": "rid",
            },
            expected_args=[self.proxy],
        )


class TestProjectCleanup(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session, service_type='key-manager')

    def test_get_cleanup_dependencies(self):
        deps = self.proxy._get_cleanup_dependencies()
        self.assertIn('key_manager', deps)
        self.assertEqual([], deps['key_manager']['before'])

    @mock.patch.object(_proxy.Proxy, 'containers', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'delete_container', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'secrets', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'delete_secret', autospec=True)
    def test_service_cleanup(
        self,
        mock_del_secret,
        mock_secrets,
        mock_del_container,
        mock_containers,
    ):
        c = container.Container(id='c-1', name='test-container')
        s = secret.Secret(id='s-1', name='test-secret')
        mock_containers.return_value = [c]
        mock_secrets.return_value = [s]

        self.proxy._service_cleanup(
            dry_run=False,
            client_status_queue=None,
            identified_resources=None,
            filters=None,
            resource_evaluation_fn=None,
            skip_resources=None,
        )

        mock_del_container.assert_called_once_with(self.proxy, c)
        mock_del_secret.assert_called_once_with(self.proxy, s)

    @mock.patch.object(_proxy.Proxy, 'containers', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'delete_container', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'secrets', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'delete_secret', autospec=True)
    def test_service_cleanup_dry_run(
        self,
        mock_del_secret,
        mock_secrets,
        mock_del_container,
        mock_containers,
    ):
        c = container.Container(id='c-1', name='test-container')
        s = secret.Secret(id='s-1', name='test-secret')
        mock_containers.return_value = [c]
        mock_secrets.return_value = [s]

        self.proxy._service_cleanup(
            dry_run=True,
            client_status_queue=None,
            identified_resources=None,
            filters=None,
            resource_evaluation_fn=None,
            skip_resources=None,
        )

        mock_del_container.assert_not_called()
        mock_del_secret.assert_not_called()

    @mock.patch.object(_proxy.Proxy, 'containers', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'secrets', autospec=True)
    def test_service_cleanup_skip_secret(self, mock_secrets, mock_containers):
        mock_containers.return_value = []

        self.proxy._service_cleanup(
            dry_run=False,
            client_status_queue=None,
            identified_resources=None,
            filters=None,
            resource_evaluation_fn=None,
            skip_resources=['key_manager.secret'],
        )

        mock_secrets.assert_not_called()
        mock_containers.assert_called_once_with(self.proxy)

    @mock.patch.object(_proxy.Proxy, 'containers', autospec=True)
    @mock.patch.object(_proxy.Proxy, 'secrets', autospec=True)
    def test_service_cleanup_skip_container(
        self, mock_secrets, mock_containers
    ):
        mock_secrets.return_value = []

        self.proxy._service_cleanup(
            dry_run=False,
            client_status_queue=None,
            identified_resources=None,
            filters=None,
            resource_evaluation_fn=None,
            skip_resources=['key_manager.container'],
        )

        mock_containers.assert_not_called()
        mock_secrets.assert_called_once_with(self.proxy)
