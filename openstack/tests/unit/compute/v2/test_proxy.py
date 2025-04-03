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

import contextlib
import datetime
import fixtures
from unittest import mock
import uuid
import warnings

from openstack.block_storage.v3 import volume
from openstack.compute.v2 import _proxy
from openstack.compute.v2 import aggregate
from openstack.compute.v2 import availability_zone as az
from openstack.compute.v2 import console_auth_token
from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor
from openstack.compute.v2 import hypervisor
from openstack.compute.v2 import image
from openstack.compute.v2 import keypair
from openstack.compute.v2 import migration
from openstack.compute.v2 import quota_class_set
from openstack.compute.v2 import quota_set
from openstack.compute.v2 import server
from openstack.compute.v2 import server_action
from openstack.compute.v2 import server_group
from openstack.compute.v2 import server_interface
from openstack.compute.v2 import server_ip
from openstack.compute.v2 import server_migration
from openstack.compute.v2 import server_remote_console
from openstack.compute.v2 import service
from openstack.compute.v2 import usage
from openstack.compute.v2 import volume_attachment
from openstack.identity.v3 import project
from openstack import proxy as proxy_base
from openstack.tests.unit import base
from openstack.tests.unit import test_proxy_base
from openstack import warnings as os_warnings


class TestComputeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestFlavor(TestComputeProxy):
    def test_flavor_create(self):
        self.verify_create(self.proxy.create_flavor, flavor.Flavor)

    def test_flavor_delete(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, False)

    def test_flavor_update(self):
        self.verify_update(self.proxy.update_flavor, flavor.Flavor, False)

    def test_flavor_delete_ignore(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, True)

    def test_flavor_find(self):
        self.verify_find(self.proxy.find_flavor, flavor.Flavor)

    def test_flavor_find_query(self):
        self.verify_find(
            self.proxy.find_flavor,
            flavor.Flavor,
            method_kwargs={"a": "b"},
            expected_kwargs={"a": "b", "ignore_missing": True},
        )

    def test_flavor_find_fetch_extra(self):
        """fetch extra_specs is triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor()
            mocked.return_value = res
            self._verify(
                'openstack.proxy.Proxy._find',
                self.proxy.find_flavor,
                method_args=['res', True],
                method_kwargs={'get_extra_specs': True},
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
                expected_kwargs={'ignore_missing': True},
            )
            mocked.assert_called_once()

    def test_flavor_find_skip_fetch_extra(self):
        """fetch extra_specs not triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor(extra_specs={'a': 'b'})
            mocked.return_value = res
            self._verify(
                'openstack.proxy.Proxy._find',
                self.proxy.find_flavor,
                method_args=['res', True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
                expected_kwargs={'ignore_missing': True},
            )
            mocked.assert_not_called()

    def test_flavor_get_no_extra(self):
        """fetch extra_specs not triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor()
            mocked.return_value = res
            self._verify(
                'openstack.proxy.Proxy._get',
                self.proxy.get_flavor,
                method_args=['res'],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
            )
            mocked.assert_not_called()

    def test_flavor_get_fetch_extra(self):
        """fetch extra_specs is triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor()
            mocked.return_value = res
            self._verify(
                'openstack.proxy.Proxy._get',
                self.proxy.get_flavor,
                method_args=['res', True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
            )
            mocked.assert_called_once()

    def test_flavor_get_skip_fetch_extra(self):
        """fetch extra_specs not triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor(extra_specs={'a': 'b'})
            mocked.return_value = res
            self._verify(
                'openstack.proxy.Proxy._get',
                self.proxy.get_flavor,
                method_args=['res', True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
            )
            mocked.assert_not_called()

    @mock.patch("openstack.proxy.Proxy._list")
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs")
    def test_flavors_detailed(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=True)
        for r in res:
            self.assertIsNotNone(r)
        fetch_mock.assert_not_called()
        list_mock.assert_called_with(
            flavor.Flavor, base_path="/flavors/detail"
        )

    @mock.patch("openstack.proxy.Proxy._list")
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs")
    def test_flavors_not_detailed(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=False)
        for r in res:
            self.assertIsNotNone(r)
        fetch_mock.assert_not_called()
        list_mock.assert_called_with(flavor.Flavor, base_path="/flavors")

    @mock.patch("openstack.proxy.Proxy._list")
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs")
    def test_flavors_query(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=False, get_extra_specs=True, a="b")
        for r in res:
            fetch_mock.assert_called_with(self.proxy)
        list_mock.assert_called_with(
            flavor.Flavor, base_path="/flavors", a="b"
        )

    @mock.patch("openstack.proxy.Proxy._list")
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs")
    def test_flavors_get_extra(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=False, get_extra_specs=True)
        for r in res:
            fetch_mock.assert_called_with(self.proxy)
        list_mock.assert_called_with(flavor.Flavor, base_path="/flavors")

    def test_flavor_get_access(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.get_access",
            self.proxy.get_flavor_access,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_flavor_add_tenant_access(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.add_tenant_access",
            self.proxy.flavor_add_tenant_access,
            method_args=["value", "fake-tenant"],
            expected_args=[self.proxy, "fake-tenant"],
        )

    def test_flavor_remove_tenant_access(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.remove_tenant_access",
            self.proxy.flavor_remove_tenant_access,
            method_args=["value", "fake-tenant"],
            expected_args=[self.proxy, "fake-tenant"],
        )

    def test_flavor_fetch_extra_specs(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.fetch_extra_specs",
            self.proxy.fetch_flavor_extra_specs,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_create_flavor_extra_specs(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.create_extra_specs",
            self.proxy.create_flavor_extra_specs,
            method_args=["value", {'a': 'b'}],
            expected_args=[self.proxy],
            expected_kwargs={"specs": {'a': 'b'}},
        )

    def test_get_flavor_extra_specs_prop(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.get_extra_specs_property",
            self.proxy.get_flavor_extra_specs_property,
            method_args=["value", "prop"],
            expected_args=[self.proxy, "prop"],
        )

    def test_update_flavor_extra_specs_prop(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.update_extra_specs_property",
            self.proxy.update_flavor_extra_specs_property,
            method_args=["value", "prop", "val"],
            expected_args=[self.proxy, "prop", "val"],
        )

    def test_delete_flavor_extra_specs_prop(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.delete_extra_specs_property",
            self.proxy.delete_flavor_extra_specs_property,
            method_args=["value", "prop"],
            expected_args=[self.proxy, "prop"],
        )


class TestKeyPair(TestComputeProxy):
    def test_keypair_create(self):
        self.verify_create(self.proxy.create_keypair, keypair.Keypair)

    def test_keypair_delete(self):
        self._verify(
            "openstack.compute.v2.keypair.Keypair.delete",
            self.proxy.delete_keypair,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={"params": {}},
        )

    def test_keypair_delete_ignore(self):
        self._verify(
            "openstack.compute.v2.keypair.Keypair.delete",
            self.proxy.delete_keypair,
            method_args=["value", True],
            method_kwargs={"user_id": "fake_user"},
            expected_args=[self.proxy],
            expected_kwargs={"params": {"user_id": "fake_user"}},
        )

    def test_keypair_delete_user_id(self):
        self._verify(
            "openstack.compute.v2.keypair.Keypair.delete",
            self.proxy.delete_keypair,
            method_args=["value"],
            method_kwargs={"user_id": "fake_user"},
            expected_args=[self.proxy],
            expected_kwargs={"params": {"user_id": "fake_user"}},
        )

    def test_keypair_find(self):
        self.verify_find(self.proxy.find_keypair, keypair.Keypair)

    def test_keypair_find_user_id(self):
        self.verify_find(
            self.proxy.find_keypair,
            keypair.Keypair,
            method_kwargs={'user_id': 'fake_user'},
            expected_kwargs={'user_id': 'fake_user'},
        )

    def test_keypair_get(self):
        self._verify(
            "openstack.compute.v2.keypair.Keypair.fetch",
            self.proxy.get_keypair,
            method_args=["value"],
            method_kwargs={},
            expected_args=[self.proxy],
            expected_kwargs={
                "error_message": "No Keypair found for value",
            },
        )

    def test_keypair_get_user_id(self):
        self._verify(
            "openstack.compute.v2.keypair.Keypair.fetch",
            self.proxy.get_keypair,
            method_args=["value"],
            method_kwargs={"user_id": "fake_user"},
            expected_args=[self.proxy],
            expected_kwargs={
                "error_message": "No Keypair found for value",
                "user_id": "fake_user",
            },
        )

    def test_keypairs(self):
        self.verify_list(self.proxy.keypairs, keypair.Keypair)

    def test_keypairs_user_id(self):
        self.verify_list(
            self.proxy.keypairs,
            keypair.Keypair,
            method_kwargs={'user_id': 'fake_user'},
            expected_kwargs={'user_id': 'fake_user'},
        )


class TestKeyPairUrl(base.TestCase):
    def setUp(self):
        super().setUp()
        self.useFixture(
            fixtures.MonkeyPatch(
                "openstack.utils.maximum_supported_microversion",
                lambda *args, **kwargs: "2.10",
            )
        )

    def test_keypair_find_user_id(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(
                        "compute",
                        "public",
                        append=["os-keypairs", "fake_keypair"],
                        qs_elements=["user_id=fake_user"],
                    ),
                ),
            ]
        )

        self.cloud.compute.find_keypair("fake_keypair", user_id="fake_user")

    def test_keypair_get_user_id(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(
                        "compute",
                        "public",
                        append=["os-keypairs", "fake_keypair"],
                        qs_elements=["user_id=fake_user"],
                    ),
                ),
            ]
        )

        self.cloud.compute.get_keypair("fake_keypair", user_id="fake_user")

    def test_keypair_delete_user_id(self):
        self.register_uris(
            [
                dict(
                    method="DELETE",
                    uri=self.get_mock_url(
                        "compute",
                        "public",
                        append=["os-keypairs", "fake_keypair"],
                        qs_elements=["user_id=fake_user"],
                    ),
                ),
            ]
        )

        self.cloud.compute.delete_keypair("fake_keypair", user_id="fake_user")


class TestAggregate(TestComputeProxy):
    def test_aggregate_create(self):
        self.verify_create(self.proxy.create_aggregate, aggregate.Aggregate)

    def test_aggregate_delete(self):
        self.verify_delete(
            self.proxy.delete_aggregate, aggregate.Aggregate, False
        )

    def test_aggregate_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_aggregate, aggregate.Aggregate, True
        )

    def test_aggregate_find(self):
        self.verify_find(self.proxy.find_aggregate, aggregate.Aggregate)

    def test_aggregates(self):
        self.verify_list(self.proxy.aggregates, aggregate.Aggregate)

    def test_aggregate_get(self):
        self.verify_get(self.proxy.get_aggregate, aggregate.Aggregate)

    def test_aggregate_update(self):
        self.verify_update(self.proxy.update_aggregate, aggregate.Aggregate)

    def test_aggregate_add_host(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.add_host",
            self.proxy.add_host_to_aggregate,
            method_args=["value", "host"],
            expected_args=[self.proxy, "host"],
        )

    def test_aggregate_remove_host(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.remove_host",
            self.proxy.remove_host_from_aggregate,
            method_args=["value", "host"],
            expected_args=[self.proxy, "host"],
        )

    def test_aggregate_set_metadata(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.set_metadata",
            self.proxy.set_aggregate_metadata,
            method_args=["value", {'a': 'b'}],
            expected_args=[self.proxy, {'a': 'b'}],
        )

    def test_aggregate_precache_image(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.precache_images",
            self.proxy.aggregate_precache_images,
            method_args=["value", '1'],
            expected_args=[self.proxy, [{'id': '1'}]],
        )

    def test_aggregate_precache_images(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.precache_images",
            self.proxy.aggregate_precache_images,
            method_args=["value", ['1', '2']],
            expected_args=[self.proxy, [{'id': '1'}, {'id': '2'}]],
        )


class TestService(TestComputeProxy):
    def test_services(self):
        self.verify_list(self.proxy.services, service.Service)

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_enable_service_252(self, mv_mock):
        self._verify(
            'openstack.compute.v2.service.Service.enable',
            self.proxy.enable_service,
            method_args=["value", "host1", "nova-compute"],
            expected_args=[self.proxy, "host1", "nova-compute"],
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    def test_enable_service_253(self, mv_mock):
        self._verify(
            'openstack.proxy.Proxy._update',
            self.proxy.enable_service,
            method_args=["value"],
            method_kwargs={},
            expected_args=[service.Service, "value"],
            expected_kwargs={'status': 'enabled'},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_disable_service_252(self, mv_mock):
        self._verify(
            'openstack.compute.v2.service.Service.disable',
            self.proxy.disable_service,
            method_args=["value", "host1", "nova-compute"],
            expected_args=[self.proxy, "host1", "nova-compute", None],
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    def test_disable_service_253(self, mv_mock):
        self._verify(
            'openstack.proxy.Proxy._update',
            self.proxy.disable_service,
            method_args=["value"],
            method_kwargs={'disabled_reason': 'some_reason'},
            expected_args=[service.Service, "value"],
            expected_kwargs={
                'status': 'disabled',
                'disabled_reason': 'some_reason',
            },
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_force_service_down_252(self, mv_mock):
        self._verify(
            'openstack.compute.v2.service.Service.set_forced_down',
            self.proxy.update_service_forced_down,
            method_args=["value", "host1", "nova-compute"],
            expected_args=[self.proxy, "host1", "nova-compute", True],
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_force_service_down_252_empty_vals(self, mv_mock):
        self.assertRaises(
            ValueError,
            self.proxy.update_service_forced_down,
            "value",
            None,
            None,
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_force_service_down_252_empty_vals_svc(self, mv_mock):
        self._verify(
            'openstack.compute.v2.service.Service.set_forced_down',
            self.proxy.update_service_forced_down,
            method_args=[{'host': 'a', 'binary': 'b'}, None, None],
            expected_args=[self.proxy, None, None, True],
        )

    def test_find_service(self):
        self.verify_find(
            self.proxy.find_service,
            service.Service,
        )

    def test_find_service_args(self):
        self.verify_find(
            self.proxy.find_service,
            service.Service,
            method_kwargs={'host': 'h1'},
            expected_kwargs={'host': 'h1'},
        )


class TestVolumeAttachment(TestComputeProxy):
    def test_volume_attachment_create(self):
        self.verify_create(
            self.proxy.create_volume_attachment,
            volume_attachment.VolumeAttachment,
            method_kwargs={'server': 'server_id', 'volume': 'volume_id'},
            expected_kwargs={
                'server_id': 'server_id',
                'volume_id': 'volume_id',
            },
        )

    def test_volume_attachment_create__legacy_parameters(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            self.verify_create(
                self.proxy.create_volume_attachment,
                volume_attachment.VolumeAttachment,
                method_kwargs={'server': 'server_id', 'volumeId': 'volume_id'},
                expected_kwargs={
                    'server_id': 'server_id',
                    'volume_id': 'volume_id',
                },
            )

            self.assertEqual(1, len(w))
            self.assertEqual(
                os_warnings.RemovedInSDK50Warning,
                w[-1].category,
            )
            self.assertIn(
                'This method was called with a volume_id or volumeId argument',
                str(w[-1]),
            )

    def test_volume_attachment_create__missing_parameters(self):
        exc = self.assertRaises(
            TypeError,
            self.proxy.create_volume_attachment,
            'server_id',
        )
        self.assertIn(
            'create_volume_attachment() missing 1 required positional argument: volume',  # noqa: E501
            str(exc),
        )

    def test_volume_attachment_update(self):
        self.verify_update(
            self.proxy.update_volume_attachment,
            volume_attachment.VolumeAttachment,
            method_args=[],
            method_kwargs={'server': 'server_id', 'volume': 'volume_id'},
            expected_args=[None],
            expected_kwargs={
                'id': 'volume_id',
                'server_id': 'server_id',
                'volume_id': 'volume_id',
            },
        )

    def test_volume_attachment_delete(self):
        # We pass objects to avoid the lookup that's done as part of the
        # handling of legacy option order. We test that legacy path separately.
        fake_server = server.Server(id=str(uuid.uuid4()))
        fake_volume = volume.Volume(id=str(uuid.uuid4()))

        self.verify_delete(
            self.proxy.delete_volume_attachment,
            volume_attachment.VolumeAttachment,
            ignore_missing=False,
            method_args=[fake_server, fake_volume],
            method_kwargs={},
            expected_args=[None],
            expected_kwargs={
                'id': fake_volume.id,
                'server_id': fake_server.id,
            },
        )

    def test_volume_attachment_delete__ignore(self):
        # We pass objects to avoid the lookup that's done as part of the
        # handling of legacy option order. We test that legacy path separately.
        fake_server = server.Server(id=str(uuid.uuid4()))
        fake_volume = volume.Volume(id=str(uuid.uuid4()))

        self.verify_delete(
            self.proxy.delete_volume_attachment,
            volume_attachment.VolumeAttachment,
            ignore_missing=True,
            method_args=[fake_server, fake_volume],
            method_kwargs={},
            expected_args=[None],
            expected_kwargs={
                'id': fake_volume.id,
                'server_id': fake_server.id,
            },
        )

    def test_volume_attachment_delete__legacy_parameters(self):
        fake_server = server.Server(id=str(uuid.uuid4()))
        fake_volume = volume.Volume(id=str(uuid.uuid4()))

        with mock.patch.object(
            self.proxy,
            'find_server',
            return_value=None,
        ) as mock_find_server:
            # we are calling the method with volume and server ID arguments as
            # strings and in the wrong order, which results in a query as we
            # attempt to match the server ID to an actual server before we
            # switch the argument order once we realize we can't do this
            self.verify_delete(
                self.proxy.delete_volume_attachment,
                volume_attachment.VolumeAttachment,
                ignore_missing=False,
                method_args=[fake_volume.id, fake_server.id],
                method_kwargs={},
                expected_args=[None],
                expected_kwargs={
                    'id': fake_volume.id,
                    'server_id': fake_server.id,
                },
            )

            # note that we attempted to call the server with the volume ID but
            # this was mocked to return None (as would happen in the real
            # world)
            mock_find_server.assert_called_once_with(
                fake_volume.id,
                ignore_missing=True,
            )

    def test_volume_attachment_get(self):
        self.verify_get(
            self.proxy.get_volume_attachment,
            volume_attachment.VolumeAttachment,
            method_args=[],
            method_kwargs={'server': 'server_id', 'volume': 'volume_id'},
            expected_kwargs={
                'id': 'volume_id',
                'server_id': 'server_id',
            },
        )

    def test_volume_attachments(self):
        self.verify_list(
            self.proxy.volume_attachments,
            volume_attachment.VolumeAttachment,
            method_kwargs={'server': 'server_id'},
            expected_kwargs={'server_id': 'server_id'},
        )


class TestHypervisor(TestComputeProxy):
    def test_hypervisors_not_detailed(self):
        self.verify_list(
            self.proxy.hypervisors,
            hypervisor.Hypervisor,
            method_kwargs={"details": False},
            expected_kwargs={},
        )

    def test_hypervisors_detailed(self):
        self.verify_list(
            self.proxy.hypervisors,
            hypervisor.HypervisorDetail,
            method_kwargs={"details": True},
            expected_kwargs={},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_hypervisors_search_before_253_no_qp(self, sm):
        self.verify_list(
            self.proxy.hypervisors,
            hypervisor.Hypervisor,
            base_path='/os-hypervisors/detail',
            method_kwargs={'details': True},
            expected_kwargs={},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_hypervisors_search_before_253(self, sm):
        self.verify_list(
            self.proxy.hypervisors,
            hypervisor.Hypervisor,
            base_path='/os-hypervisors/substring/search',
            method_kwargs={'hypervisor_hostname_pattern': 'substring'},
            expected_kwargs={},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    def test_hypervisors_search_after_253(self, sm):
        self.verify_list(
            self.proxy.hypervisors,
            hypervisor.Hypervisor,
            method_kwargs={'hypervisor_hostname_pattern': 'substring'},
            base_path=None,
            expected_kwargs={'hypervisor_hostname_pattern': 'substring'},
        )

    def test_find_hypervisor_detail(self):
        self.verify_find(
            self.proxy.find_hypervisor,
            hypervisor.Hypervisor,
            expected_kwargs={
                'list_base_path': '/os-hypervisors/detail',
                'ignore_missing': True,
            },
        )

    def test_find_hypervisor_no_detail(self):
        self.verify_find(
            self.proxy.find_hypervisor,
            hypervisor.Hypervisor,
            method_kwargs={'details': False},
            expected_kwargs={'list_base_path': None, 'ignore_missing': True},
        )

    def test_get_hypervisor(self):
        self.verify_get(self.proxy.get_hypervisor, hypervisor.Hypervisor)

    def test_get_hypervisor_uptime(self):
        self._verify(
            "openstack.compute.v2.hypervisor.Hypervisor.get_uptime",
            self.proxy.get_hypervisor_uptime,
            method_args=["value"],
            expected_args=[self.proxy],
        )


class TestCompute(TestComputeProxy):
    def test_extension_find(self):
        self.verify_find(self.proxy.find_extension, extension.Extension)

    def test_extensions(self):
        self.verify_list(self.proxy.extensions, extension.Extension)

    @contextlib.contextmanager
    def _check_image_proxy_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            yield
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn(
                "This API is a proxy to the image service ",
                str(w[-1].message),
            )

    def test_image_delete(self):
        with self._check_image_proxy_deprecation_warning():
            self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        with self._check_image_proxy_deprecation_warning():
            self.verify_delete(self.proxy.delete_image, image.Image, True)

    def test_image_find(self):
        with self._check_image_proxy_deprecation_warning():
            self.verify_find(self.proxy.find_image, image.Image)

    def test_image_get(self):
        with self._check_image_proxy_deprecation_warning():
            self.verify_get(self.proxy.get_image, image.Image)

    def test_images_detailed(self):
        with self._check_image_proxy_deprecation_warning():
            self.verify_list(
                self.proxy.images,
                image.ImageDetail,
                method_kwargs={"details": True, "query": 1},
                expected_kwargs={"query": 1},
            )

    def test_images_not_detailed(self):
        with self._check_image_proxy_deprecation_warning():
            self.verify_list(
                self.proxy.images,
                image.Image,
                method_kwargs={"details": False, "query": 1},
                expected_kwargs={"query": 1},
            )

    def test_limits_get(self):
        self._verify(
            "openstack.compute.v2.limits.Limits.fetch",
            self.proxy.get_limits,
            method_args=[],
            method_kwargs={"a": "b"},
            expected_args=[self.proxy],
            expected_kwargs={"a": "b"},
        )

    def test_server_interface_create(self):
        self.verify_create(
            self.proxy.create_server_interface,
            server_interface.ServerInterface,
            method_kwargs={"server": "test_id"},
            expected_kwargs={"server_id": "test_id"},
        )

    def test_server_interface_delete(self):
        self.proxy._get_uri_attribute = lambda *args: args[1]

        interface_id = "test_interface_id"
        server_id = "test_server_id"
        test_interface = server_interface.ServerInterface(id=interface_id)
        test_interface.server_id = server_id

        # Case1: ServerInterface instance is provided as value
        self._verify(
            "openstack.proxy.Proxy._delete",
            self.proxy.delete_server_interface,
            method_args=[test_interface],
            method_kwargs={"server": server_id},
            expected_args=[server_interface.ServerInterface, interface_id],
            expected_kwargs={"server_id": server_id, "ignore_missing": True},
        )

        # Case2: ServerInterface ID is provided as value
        self._verify(
            "openstack.proxy.Proxy._delete",
            self.proxy.delete_server_interface,
            method_args=[interface_id],
            method_kwargs={"server": server_id},
            expected_args=[server_interface.ServerInterface, interface_id],
            expected_kwargs={"server_id": server_id, "ignore_missing": True},
        )

    def test_server_interface_delete_ignore(self):
        self.proxy._get_uri_attribute = lambda *args: args[1]
        self.verify_delete(
            self.proxy.delete_server_interface,
            server_interface.ServerInterface,
            True,
            method_kwargs={"server": "test_id"},
            expected_kwargs={"server_id": "test_id"},
        )

    def test_server_interface_get(self):
        self.proxy._get_uri_attribute = lambda *args: args[1]

        interface_id = "test_interface_id"
        server_id = "test_server_id"
        test_interface = server_interface.ServerInterface(id=interface_id)
        test_interface.server_id = server_id

        # Case1: ServerInterface instance is provided as value
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_server_interface,
            method_args=[test_interface],
            method_kwargs={"server": server_id},
            expected_args=[server_interface.ServerInterface],
            expected_kwargs={"port_id": interface_id, "server_id": server_id},
        )

        # Case2: ServerInterface ID is provided as value
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_server_interface,
            method_args=[interface_id],
            method_kwargs={"server": server_id},
            expected_args=[server_interface.ServerInterface],
            expected_kwargs={"port_id": interface_id, "server_id": server_id},
        )

    def test_server_interfaces(self):
        self.verify_list(
            self.proxy.server_interfaces,
            server_interface.ServerInterface,
            method_args=["test_id"],
            expected_args=[],
            expected_kwargs={"server_id": "test_id"},
        )

    def test_server_ips_with_network_label(self):
        self.verify_list(
            self.proxy.server_ips,
            server_ip.ServerIP,
            method_args=["test_id"],
            method_kwargs={"network_label": "test_label"},
            expected_args=[],
            expected_kwargs={
                "server_id": "test_id",
                "network_label": "test_label",
            },
        )

    def test_server_ips_without_network_label(self):
        self.verify_list(
            self.proxy.server_ips,
            server_ip.ServerIP,
            method_args=["test_id"],
            expected_args=[],
            expected_kwargs={"server_id": "test_id", "network_label": None},
        )

    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_server, server.Server)

    def test_server_delete(self):
        self.verify_delete(self.proxy.delete_server, server.Server, False)

    def test_server_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server, server.Server, True)

    def test_server_force_delete(self):
        self._verify(
            "openstack.compute.v2.server.Server.force_delete",
            self.proxy.delete_server,
            method_args=["value", False, True],
            expected_args=[self.proxy],
        )

    def test_server_find(self):
        self.verify_find(
            self.proxy.find_server,
            server.Server,
            method_kwargs={'all_projects': True},
            expected_kwargs={
                'list_base_path': '/servers/detail',
                'all_projects': True,
            },
        )

    def test_server_get(self):
        self.verify_get(self.proxy.get_server, server.Server)

    def test_servers_detailed(self):
        self.verify_list(
            self.proxy.servers,
            server.Server,
            method_kwargs={"details": True, "changes_since": 1, "image": 2},
            expected_kwargs={
                "changes_since": 1,
                "image": 2,
                "base_path": "/servers/detail",
            },
        )

    def test_servers_not_detailed(self):
        self.verify_list(
            self.proxy.servers,
            server.Server,
            method_kwargs={"details": False, "changes_since": 1, "image": 2},
            expected_kwargs={"changes_since": 1, "image": 2},
        )

    def test_server_update(self):
        self.verify_update(self.proxy.update_server, server.Server)

    def test_server_change_password(self):
        self._verify(
            "openstack.compute.v2.server.Server.change_password",
            self.proxy.change_server_password,
            method_args=["value", "password"],
            expected_args=[self.proxy, "password"],
        )

    def test_server_get_password(self):
        self._verify(
            "openstack.compute.v2.server.Server.get_password",
            self.proxy.get_server_password,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_clear_password(self):
        self._verify(
            "openstack.compute.v2.server.Server.clear_password",
            self.proxy.clear_server_password,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_wait_for(self):
        value = server.Server(id='1234')
        self.verify_wait_for_status(
            self.proxy.wait_for_server,
            method_args=[value],
            expected_args=[self.proxy, value, 'ACTIVE', ['ERROR'], 2, 120],
            expected_kwargs={'callback': None},
        )

    def test_server_resize(self):
        self._verify(
            "openstack.compute.v2.server.Server.resize",
            self.proxy.resize_server,
            method_args=["value", "test-flavor"],
            expected_args=[self.proxy, "test-flavor"],
        )

    def test_server_confirm_resize(self):
        self._verify(
            "openstack.compute.v2.server.Server.confirm_resize",
            self.proxy.confirm_server_resize,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_revert_resize(self):
        self._verify(
            "openstack.compute.v2.server.Server.revert_resize",
            self.proxy.revert_server_resize,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_rebuild(self):
        id = 'test_image_id'
        image_obj = image.Image(id='test_image_id')

        # Case1: image object is provided
        # NOTE: Inside of Server.rebuild is where image_obj gets converted
        # to an ID instead of object.
        self._verify(
            'openstack.compute.v2.server.Server.rebuild',
            self.proxy.rebuild_server,
            method_args=["value"],
            method_kwargs={
                "name": "test_server",
                "admin_password": "test_pass",
                "metadata": {"k1": "v1"},
                "image": image_obj,
            },
            expected_args=[self.proxy],
            expected_kwargs={
                "name": "test_server",
                "admin_password": "test_pass",
                "metadata": {"k1": "v1"},
                "image": image_obj,
            },
        )

        # Case2: image name or id is provided
        self._verify(
            'openstack.compute.v2.server.Server.rebuild',
            self.proxy.rebuild_server,
            method_args=["value"],
            method_kwargs={
                "name": "test_server",
                "admin_password": "test_pass",
                "metadata": {"k1": "v1"},
                "image": id,
            },
            expected_args=[self.proxy],
            expected_kwargs={
                "name": "test_server",
                "admin_password": "test_pass",
                "metadata": {"k1": "v1"},
                "image": id,
            },
        )

    def test_add_fixed_ip_to_server(self):
        self._verify(
            "openstack.compute.v2.server.Server.add_fixed_ip",
            self.proxy.add_fixed_ip_to_server,
            method_args=["value", "network-id"],
            expected_args=[self.proxy, "network-id"],
        )

    def test_fixed_ip_from_server(self):
        self._verify(
            "openstack.compute.v2.server.Server.remove_fixed_ip",
            self.proxy.remove_fixed_ip_from_server,
            method_args=["value", "address"],
            expected_args=[self.proxy, "address"],
        )

    def test_floating_ip_to_server(self):
        self._verify(
            "openstack.compute.v2.server.Server.add_floating_ip",
            self.proxy.add_floating_ip_to_server,
            method_args=["value", "floating-ip"],
            expected_args=[self.proxy, "floating-ip"],
            expected_kwargs={'fixed_address': None},
        )

    def test_add_floating_ip_to_server_with_fixed_addr(self):
        self._verify(
            "openstack.compute.v2.server.Server.add_floating_ip",
            self.proxy.add_floating_ip_to_server,
            method_args=["value", "floating-ip", 'fixed-addr'],
            expected_args=[self.proxy, "floating-ip"],
            expected_kwargs={'fixed_address': 'fixed-addr'},
        )

    def test_remove_floating_ip_from_server(self):
        self._verify(
            "openstack.compute.v2.server.Server.remove_floating_ip",
            self.proxy.remove_floating_ip_from_server,
            method_args=["value", "address"],
            expected_args=[self.proxy, "address"],
        )

    def test_server_backup(self):
        self._verify(
            "openstack.compute.v2.server.Server.backup",
            self.proxy.backup_server,
            method_args=["value", "name", "daily", 1],
            expected_args=[self.proxy, "name", "daily", 1],
        )

    def test_server_pause(self):
        self._verify(
            "openstack.compute.v2.server.Server.pause",
            self.proxy.pause_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_unpause(self):
        self._verify(
            "openstack.compute.v2.server.Server.unpause",
            self.proxy.unpause_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_suspend(self):
        self._verify(
            "openstack.compute.v2.server.Server.suspend",
            self.proxy.suspend_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_resume(self):
        self._verify(
            "openstack.compute.v2.server.Server.resume",
            self.proxy.resume_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_lock(self):
        self._verify(
            "openstack.compute.v2.server.Server.lock",
            self.proxy.lock_server,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={"locked_reason": None},
        )

    def test_server_lock_with_options(self):
        self._verify(
            "openstack.compute.v2.server.Server.lock",
            self.proxy.lock_server,
            method_args=["value"],
            method_kwargs={"locked_reason": "Because why not"},
            expected_args=[self.proxy],
            expected_kwargs={"locked_reason": "Because why not"},
        )

    def test_server_unlock(self):
        self._verify(
            "openstack.compute.v2.server.Server.unlock",
            self.proxy.unlock_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_rescue(self):
        self._verify(
            "openstack.compute.v2.server.Server.rescue",
            self.proxy.rescue_server,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={"admin_pass": None, "image_ref": None},
        )

    def test_server_rescue_with_options(self):
        self._verify(
            "openstack.compute.v2.server.Server.rescue",
            self.proxy.rescue_server,
            method_args=["value", 'PASS', 'IMG'],
            expected_args=[self.proxy],
            expected_kwargs={"admin_pass": 'PASS', "image_ref": 'IMG'},
        )

    def test_server_unrescue(self):
        self._verify(
            "openstack.compute.v2.server.Server.unrescue",
            self.proxy.unrescue_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_evacuate(self):
        self._verify(
            "openstack.compute.v2.server.Server.evacuate",
            self.proxy.evacuate_server,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={
                "host": None,
                "admin_pass": None,
                "force": None,
                "on_shared_storage": None,
            },
        )

    def test_server_evacuate_with_options(self):
        self._verify(
            "openstack.compute.v2.server.Server.evacuate",
            self.proxy.evacuate_server,
            method_args=["value", 'HOST2', 'NEW_PASS', True],
            method_kwargs={'on_shared_storage': False},
            expected_args=[self.proxy],
            expected_kwargs={
                "host": "HOST2",
                "admin_pass": 'NEW_PASS',
                "force": True,
                "on_shared_storage": False,
            },
        )

    def test_server_start(self):
        self._verify(
            "openstack.compute.v2.server.Server.start",
            self.proxy.start_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_stop(self):
        self._verify(
            "openstack.compute.v2.server.Server.stop",
            self.proxy.stop_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_restore(self):
        self._verify(
            "openstack.compute.v2.server.Server.restore",
            self.proxy.restore_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_shelve(self):
        self._verify(
            "openstack.compute.v2.server.Server.shelve",
            self.proxy.shelve_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_shelve_offload(self):
        self._verify(
            "openstack.compute.v2.server.Server.shelve_offload",
            self.proxy.shelve_offload_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_unshelve(self):
        self._verify(
            "openstack.compute.v2.server.Server.unshelve",
            self.proxy.unshelve_server,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={
                "host": None,
            },
        )

    def test_server_unshelve_with_options(self):
        self._verify(
            "openstack.compute.v2.server.Server.unshelve",
            self.proxy.unshelve_server,
            method_args=["value"],
            method_kwargs={"host": "HOST2"},
            expected_args=[self.proxy],
            expected_kwargs={
                "host": "HOST2",
            },
        )

    def test_server_trigger_dump(self):
        self._verify(
            "openstack.compute.v2.server.Server.trigger_crash_dump",
            self.proxy.trigger_server_crash_dump,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_server_add_tag(self):
        self._verify(
            "openstack.compute.v2.server.Server.add_tag",
            self.proxy.add_tag_to_server,
            method_args=["value", "tag"],
            expected_args=[self.proxy, "tag"],
        )

    def test_server_remove_tag(self):
        self._verify(
            "openstack.compute.v2.server.Server.remove_tag",
            self.proxy.remove_tag_from_server,
            method_args=["value", "tag"],
            expected_args=[self.proxy, "tag"],
        )

    def test_server_remove_tags(self):
        self._verify(
            "openstack.compute.v2.server.Server.remove_all_tags",
            self.proxy.remove_tags_from_server,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_get_server_output(self):
        self._verify(
            "openstack.compute.v2.server.Server.get_console_output",
            self.proxy.get_server_console_output,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={"length": None},
        )

        self._verify(
            "openstack.compute.v2.server.Server.get_console_output",
            self.proxy.get_server_console_output,
            method_args=["value", 1],
            expected_args=[self.proxy],
            expected_kwargs={"length": 1},
        )

    def test_availability_zones_not_detailed(self):
        self.verify_list(
            self.proxy.availability_zones,
            az.AvailabilityZone,
            method_kwargs={"details": False},
            expected_kwargs={},
        )

    def test_availability_zones_detailed(self):
        self.verify_list(
            self.proxy.availability_zones,
            az.AvailabilityZoneDetail,
            method_kwargs={"details": True},
            expected_kwargs={},
        )

    def test_get_all_server_metadata(self):
        self._verify(
            "openstack.compute.v2.server.Server.fetch_metadata",
            self.proxy.get_server_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=server.Server(id="value", metadata={}),
        )

    def test_set_server_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify(
            "openstack.compute.v2.server.Server.set_metadata",
            self.proxy.set_server_metadata,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=server.Server.existing(id=id, metadata=kwargs),
            expected_args=[self.proxy],
            expected_kwargs={'metadata': kwargs},
            expected_result=server.Server.existing(id=id, metadata=kwargs),
        )

    def test_delete_server_metadata(self):
        self._verify(
            "openstack.compute.v2.server.Server.delete_metadata_item",
            self.proxy.delete_server_metadata,
            expected_result=None,
            method_args=["value", ["key"]],
            expected_args=[self.proxy, "key"],
        )

    def test_create_image(self):
        metadata = {'k1': 'v1'}
        with mock.patch(
            'openstack.compute.v2.server.Server.create_image'
        ) as ci_mock:
            ci_mock.return_value = 'image_id'
            connection_mock = mock.Mock()
            connection_mock.get_image = mock.Mock(return_value='image')
            connection_mock.wait_for_image = mock.Mock()
            self.proxy._connection = connection_mock

            rsp = self.proxy.create_server_image(
                'server', 'image_name', metadata, wait=True, timeout=1
            )

            ci_mock.assert_called_with(self.proxy, 'image_name', metadata)

            self.proxy._connection.get_image.assert_called_with('image_id')
            self.proxy._connection.wait_for_image.assert_called_with(
                'image', timeout=1
            )

            self.assertEqual(connection_mock.wait_for_image(), rsp)

    def test_server_group_create(self):
        self.verify_create(
            self.proxy.create_server_group, server_group.ServerGroup
        )

    def test_server_group_delete(self):
        self.verify_delete(
            self.proxy.delete_server_group, server_group.ServerGroup, False
        )

    def test_server_group_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_server_group, server_group.ServerGroup, True
        )

    def test_server_group_find(self):
        self.verify_find(
            self.proxy.find_server_group,
            server_group.ServerGroup,
            method_kwargs={'all_projects': True},
            expected_kwargs={'all_projects': True},
        )

    def test_server_group_get(self):
        self.verify_get(self.proxy.get_server_group, server_group.ServerGroup)

    def test_server_groups(self):
        self.verify_list(self.proxy.server_groups, server_group.ServerGroup)

    def test_live_migrate_server(self):
        self._verify(
            'openstack.compute.v2.server.Server.live_migrate',
            self.proxy.live_migrate_server,
            method_args=["value"],
            method_kwargs={'host': 'host1', 'force': False},
            expected_args=[self.proxy],
            expected_kwargs={
                'host': 'host1',
                'force': False,
                'block_migration': None,
                'disk_over_commit': None,
            },
        )

    def test_abort_server_migration(self):
        self._verify(
            'openstack.proxy.Proxy._delete',
            self.proxy.abort_server_migration,
            method_args=['server_migration', 'server'],
            expected_args=[
                server_migration.ServerMigration,
                'server_migration',
            ],
            expected_kwargs={
                'server_id': 'server',
                'ignore_missing': True,
            },
        )

    def test_force_complete_server_migration(self):
        self._verify(
            'openstack.compute.v2.server_migration.ServerMigration.force_complete',  # noqa: E501
            self.proxy.force_complete_server_migration,
            method_args=['server_migration', 'server'],
            expected_args=[self.proxy],
        )

    def test_get_server_migration(self):
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_server_migration,
            method_args=['server_migration', 'server'],
            expected_args=[
                server_migration.ServerMigration,
                'server_migration',
            ],
            expected_kwargs={
                'server_id': 'server',
                'ignore_missing': True,
            },
        )

    def test_server_migrations(self):
        self._verify(
            'openstack.proxy.Proxy._list',
            self.proxy.server_migrations,
            method_args=['server'],
            expected_args=[server_migration.ServerMigration],
            expected_kwargs={'server_id': 'server'},
        )

    def test_migrations(self):
        self.verify_list(self.proxy.migrations, migration.Migration)

    def test_migrations_kwargs(self):
        self.verify_list(
            self.proxy.migrations,
            migration.Migration,
            method_kwargs={'host': 'h1'},
            expected_kwargs={'host': 'h1'},
        )

    def test_fetch_security_groups(self):
        self._verify(
            'openstack.compute.v2.server.Server.fetch_security_groups',
            self.proxy.fetch_server_security_groups,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_add_security_groups(self):
        self._verify(
            'openstack.compute.v2.server.Server.add_security_group',
            self.proxy.add_security_group_to_server,
            method_args=["value", 'sg'],
            expected_args=[self.proxy, 'sg'],
        )

    def test_remove_security_groups(self):
        self._verify(
            'openstack.compute.v2.server.Server.remove_security_group',
            self.proxy.remove_security_group_from_server,
            method_args=["value", 'sg'],
            expected_args=[self.proxy, 'sg'],
        )

    def test_usages(self):
        self.verify_list(self.proxy.usages, usage.Usage)

    def test_usages__with_kwargs(self):
        now = datetime.datetime.utcnow()
        start = now - datetime.timedelta(weeks=4)
        end = end = now + datetime.timedelta(days=1)
        self.verify_list(
            self.proxy.usages,
            usage.Usage,
            method_kwargs={'start': start, 'end': end},
            expected_kwargs={
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
        )

    def test_get_usage(self):
        self._verify(
            "openstack.compute.v2.usage.Usage.fetch",
            self.proxy.get_usage,
            method_args=['value'],
            method_kwargs={},
            expected_args=[self.proxy],
            expected_kwargs={},
        )

    def test_get_usage__with_kwargs(self):
        now = datetime.datetime.utcnow()
        start = now - datetime.timedelta(weeks=4)
        end = end = now + datetime.timedelta(days=1)
        self._verify(
            "openstack.compute.v2.usage.Usage.fetch",
            self.proxy.get_usage,
            method_args=['value'],
            method_kwargs={'start': start, 'end': end},
            expected_args=[self.proxy],
            expected_kwargs={
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
        )

    def test_create_server_remote_console(self):
        self.verify_create(
            self.proxy.create_server_remote_console,
            server_remote_console.ServerRemoteConsole,
            method_kwargs={"server": "test_id", "type": "fake"},
            expected_kwargs={"server_id": "test_id", "type": "fake"},
        )

    def test_get_console_url(self):
        self._verify(
            'openstack.compute.v2.server.Server.get_console_url',
            self.proxy.get_server_console_url,
            method_args=["value", "console_type"],
            expected_args=[self.proxy, "console_type"],
        )

    @mock.patch('openstack.utils.supports_microversion', autospec=True)
    @mock.patch('openstack.compute.v2._proxy.Proxy._create', autospec=True)
    @mock.patch(
        'openstack.compute.v2.server.Server.get_console_url', autospec=True
    )
    def test_create_console_mv_old(self, sgc, rcc, smv):
        console_fake = {'url': 'a', 'type': 'b', 'protocol': 'c'}
        smv.return_value = False
        sgc.return_value = console_fake
        ret = self.proxy.create_console('fake_server', 'fake_type')
        smv.assert_called_once_with(self.proxy, '2.6')
        rcc.assert_not_called()
        sgc.assert_called_with(mock.ANY, self.proxy, 'fake_type')
        self.assertDictEqual(console_fake, ret)

    @mock.patch('openstack.utils.supports_microversion', autospec=True)
    @mock.patch('openstack.compute.v2._proxy.Proxy._create', autospec=True)
    @mock.patch(
        'openstack.compute.v2.server.Server.get_console_url', autospec=True
    )
    def test_create_console_mv_2_6(self, sgc, rcc, smv):
        console_fake = {'url': 'a', 'type': 'b', 'protocol': 'c'}

        # Test server_remote_console is triggered when mv>=2.6
        smv.return_value = True
        rcc.return_value = server_remote_console.ServerRemoteConsole(
            **console_fake
        )
        ret = self.proxy.create_console('fake_server', 'fake_type')
        smv.assert_called_once_with(self.proxy, '2.6')
        sgc.assert_not_called()
        rcc.assert_called_with(
            mock.ANY,
            server_remote_console.ServerRemoteConsole,
            server_id='fake_server',
            type='fake_type',
            protocol=None,
        )
        self.assertEqual(console_fake['url'], ret['url'])


class TestQuotaClassSet(TestComputeProxy):
    def test_quota_class_set_get(self):
        self.verify_get(
            self.proxy.get_quota_class_set, quota_class_set.QuotaClassSet
        )

    def test_quota_class_set_update(self):
        self.verify_update(
            self.proxy.update_quota_class_set,
            quota_class_set.QuotaClassSet,
            False,
        )


class TestQuotaSet(TestComputeProxy):
    def test_quota_set_get(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            expected_args=[
                self.proxy,
                False,
                None,
                None,
                False,
            ],
            expected_kwargs={
                'microversion': None,
                'resource_response_key': None,
            },
            method_result=quota_set.QuotaSet(),
            expected_result=quota_set.QuotaSet(),
        )

    def test_quota_set_get_query(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            method_kwargs={'usage': True, 'user_id': 'uid'},
            expected_args=[
                self.proxy,
                False,
                '/os-quota-sets/%(project_id)s/detail',
                None,
                False,
            ],
            expected_kwargs={
                'microversion': None,
                'resource_response_key': None,
                'user_id': 'uid',
            },
        )

    def test_quota_set_get_defaults(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set_defaults,
            method_args=['prj'],
            expected_args=[
                self.proxy,
                False,
                '/os-quota-sets/%(project_id)s/defaults',
                None,
                False,
            ],
            expected_kwargs={
                'microversion': None,
                'resource_response_key': None,
            },
        )

    def test_quota_set_reset(self):
        self._verify(
            'openstack.resource.Resource.delete',
            self.proxy.revert_quota_set,
            method_args=['prj'],
            method_kwargs={'user_id': 'uid'},
            expected_args=[self.proxy],
            expected_kwargs={'user_id': 'uid'},
        )

    @mock.patch.object(proxy_base.Proxy, "_get_resource")
    def test_quota_set_update(self, mock_get):
        fake_project = project.Project(id='prj')
        fake_quota_set = quota_set.QuotaSet(project_id='prj')
        mock_get.side_effect = [fake_project, fake_quota_set]

        self._verify(
            'openstack.resource.Resource.commit',
            self.proxy.update_quota_set,
            method_args=['prj'],
            method_kwargs={'ram': 123},
            expected_args=[self.proxy],
            expected_kwargs={},
        )
        mock_get.assert_has_calls(
            [
                mock.call(project.Project, 'prj'),
                mock.call(quota_set.QuotaSet, None, project_id='prj', ram=123),
            ]
        )

    @mock.patch.object(proxy_base.Proxy, "_get_resource")
    def test_quota_set_update__legacy(self, mock_get):
        fake_quota_set = quota_set.QuotaSet(project_id='prj')
        mock_get.side_effect = [fake_quota_set]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            self._verify(
                'openstack.resource.Resource.commit',
                self.proxy.update_quota_set,
                method_args=[fake_quota_set],
                method_kwargs={'ram': 123},
                expected_args=[self.proxy],
                expected_kwargs={},
            )

            self.assertEqual(1, len(w))
            self.assertEqual(
                os_warnings.RemovedInSDK50Warning,
                w[-1].category,
            )
            self.assertIn(
                "The signature of 'update_quota_set' has changed ",
                str(w[-1]),
            )


class TestServerAction(TestComputeProxy):
    def test_server_action_get(self):
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_server_action,
            method_args=['request_id'],
            method_kwargs={'server': 'server_id'},
            expected_args=[server_action.ServerAction],
            expected_kwargs={
                'request_id': 'request_id',
                'server_id': 'server_id',
            },
        )

    def test_server_actions(self):
        self.verify_list(
            self.proxy.server_actions,
            server_action.ServerAction,
            method_kwargs={'server': 'server_a'},
            expected_kwargs={'server_id': 'server_a'},
        )


class TestValidateConsoleAuthToken(TestComputeProxy):
    def test_validate_console_auth_token(self):
        self.verify_get(
            self.proxy.validate_console_auth_token,
            console_auth_token.ConsoleAuthToken,
        )
