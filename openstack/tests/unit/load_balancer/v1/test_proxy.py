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
from testtools import matchers

from openstack.load_balancer import load_balancer_service
from openstack.load_balancer.v1 import _proxy
from openstack.load_balancer.v1 import load_balancer as _load_balancer
from openstack.load_balancer.v1 import certificate as _cert
from openstack.load_balancer.v1 import listener as _listener
from openstack.load_balancer.v1 import health_check as _hc
from openstack.load_balancer.v1 import quota as _quota
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase


class TestLoadBalancerProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=load_balancer_service.LoadBalancerService,
            **kwargs)


class TestLoadBalancerLoadBalancer(TestLoadBalancerProxy):
    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerLoadBalancer, self).__init__(*args, **kwargs)

    def test_list_load_balancer(self):
        query = {
            "id": "id",
            "name": "name",
            "status": "status",
            "type": "type",
            "description": "description",
            "vpc_id": "vpc_id",
            "vip_subnet_id": "vip_subnet_id",
            "vip_address": "vip_address",
            "security_group_id": "security_group_id",
            "is_admin_state_up": True
        }
        self.mock_response_json_file_values("list_lb.json")
        load_balancers = list(self.proxy.load_balancers(**query))

        transferred_query = {
            "id": "id",
            "name": "name",
            "status": "status",
            "type": "type",
            "description": "description",
            "vpc_id": "vpc_id",
            "vip_subnet_id": "vip_subnet_id",
            "vip_address": "vip_address",
            "security_group_id": "security_group_id",
            "admin_state_up": True,
        }
        self.assert_session_list_with("/elbaas/loadbalancers",
                                      params=transferred_query)

        self.assertEquals(1, len(load_balancers))

        lb = load_balancers[0]
        self.assertIsInstance(lb, _load_balancer.LoadBalancer)

        self.assertEqual("0b07acf06d243925bc24a0ac7445267a", lb.id)
        self.assertEqual("MY_ELB", lb.name)
        self.assertEqual("ACTIVE", lb.status)
        self.assertEqual("External", lb.type)
        self.assertEqual("2015-09-14 02:34:32", lb.create_time)
        self.assertEqual("2015-09-14 02:34:32", lb.update_time)
        self.assertEqual("192.144.62.114", lb.vip_address)
        self.assertEqual(1, lb.bandwidth)
        self.assertEqual("f54a3ffd-7a55-4568-9e3d-f0ff2d46a107", lb.vpc_id)
        self.assertEqual(True, lb.is_admin_state_up)
        self.assertIsNone(lb.description)
        self.assertIsNone(lb.vip_subnet_id)
        self.assertIsNone(lb.security_group_id)

    def test_create_internal_load_balancer(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })

        _lb = self.get_file_content("create_internal_lb.json")
        create_lb_job = self.proxy.create_load_balancer(**_lb)
        expect_post_json = {
            "name": "loadbalancer1",
            "description": "simple lb",
            "vpc_id": "vpc_id",
            "vip_subnet_id": "subnet_id",
            "vip_address": "192.168.7.2",
            "az": "eu-de",
            "security_group_id": "sg-id",
            "type": "Internal",
            "admin_state_up": True,
            "tenantId": "eu-de"
        }
        self.assert_session_post_with("/elbaas/loadbalancers",
                                      json=expect_post_json)
        self.assertEqual("id", create_lb_job.job_id)

    def test_create_external_load_balancer(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })

        _lb = {
            "name": "loadbalancer1",
            "description": "simple lb",
            "vpc_id": "f54a3ffd-7a55-4568-9e3d-f0ff2d46a107",
            "bandwidth": 200,
            "type": "External",
            "admin_state_up": True
        }

        create_lb_job = self.proxy.create_load_balancer(**_lb)
        expect_post_json = {
            "name": "loadbalancer1",
            "description": "simple lb",
            "vpc_id": "f54a3ffd-7a55-4568-9e3d-f0ff2d46a107",
            "bandwidth": 200,
            "type": "External",
            "admin_state_up": True
        }
        self.assert_session_post_with("/elbaas/loadbalancers",
                                      json=expect_post_json)
        self.assertEqual("id", create_lb_job.job_id)

    def test_create_external_load_balancer2(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })

        _lb = {
            "name": "loadbalancer1",
            "description": "simple lb",
            "vpc_id": "f54a3ffd-7a55-4568-9e3d-f0ff2d46a107",
            "charge_mode": "bandwidth",
            "bandwidth": 10,
            "eip_type": "5_telcom",
            "type": "External",
            "is_admin_state_up": True
        }

        create_lb_job = self.proxy.create_load_balancer(**_lb)
        expect_post_json = {
            "name": "loadbalancer1",
            "description": "simple lb",
            "vpc_id": "f54a3ffd-7a55-4568-9e3d-f0ff2d46a107",
            "charge_mode": "bandwidth",
            "bandwidth": 10,
            "eip_type": "5_telcom",
            "type": "External",
            "admin_state_up": True
        }
        self.assert_session_post_with("/elbaas/loadbalancers",
                                      json=expect_post_json)
        self.assertEqual("id", create_lb_job.job_id)

    def test_get_load_balancer_with_id(self):
        self.mock_response_json_file_values("get_lb.json")
        load_balancer = self.proxy.get_load_balancer(
            "0b07acf06d243925bc24a0ac7445267a")
        self.assert_session_get_with(
            "elbaas/loadbalancers/0b07acf06d243925bc24a0ac7445267a")
        self.assertIsInstance(load_balancer, _load_balancer.LoadBalancer)
        self.assertEquals("0b07acf06d243925bc24a0ac7445267a",
                          load_balancer.id)
        self.assertEquals("MY_ELB", load_balancer.name)
        self.assertEquals("192.144.62.114", load_balancer.vip_address)
        self.assertEquals("2015-09-14 02:34:32", load_balancer.update_time)
        self.assertEquals("2015-09-14 02:34:32", load_balancer.create_time)
        self.assertEquals("ACTIVE", load_balancer.status)
        self.assertEquals(1, load_balancer.bandwidth)
        self.assertEquals("f54a3ffd-7a55-4568-9e3d-f0ff2d46a107",
                          load_balancer.vpc_id)
        self.assertIsNone(load_balancer.security_group_id)
        self.assertIsNone(load_balancer.vip_subnet_id)
        self.assertIsNone(load_balancer.description)
        self.assertTrue(load_balancer.is_admin_state_up)
        self.assertEquals("External", load_balancer.type)

    def test_delete_load_balancer_with_id(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })
        job = self.proxy.delete_load_balancer("some-load-balancer-id")
        self.assert_session_delete(
            "elbaas/loadbalancers/some-load-balancer-id")
        self.assertEqual("id", job.job_id)

    def test_delete_load_balancer_with_instance(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })
        job = self.proxy.delete_load_balancer(
            _load_balancer.LoadBalancer(id="some-load-balancer-id"))
        self.assert_session_delete(
            "elbaas/loadbalancers/some-load-balancer-id")
        self.assertEqual("id", job.job_id)

    def test_delete_load_balancer_with_job_instance(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })
        job = self.proxy.delete_load_balancer(
            _load_balancer.LoadBalancerJob(id="some-load-balancer-id"))
        self.assert_session_delete(
            "elbaas/loadbalancers/some-load-balancer-id")
        self.assertEqual("id", job.job_id)

    def test_update_lb(self):
        self.mock_response_json_values({
            "uri": "/v1/project_id/jobs/id",
            "job_id": "id"
        })

        updated = {
            "name": "new-name",
            "description": "description",
            "bandwidth": 20,
            "is_admin_state_up": True
        }
        self.proxy.update_load_balancer("lb-id", **updated)
        self.assert_session_put_with("elbaas/loadbalancers/lb-id",
                                     json={
                                         "name": "new-name",
                                         "description": "description",
                                         "bandwidth": 20,
                                         "admin_state_up": True
                                     })


class TestLoadBalancerCertificate(TestLoadBalancerProxy):
    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerCertificate, self).__init__(*args, **kwargs)

    def test_list_cert(self):
        self.mock_response_json_file_values("list_cert.json")
        certificates = list(self.proxy.certificates())
        self.assert_session_list_with("/elbaas/certificate",
                                      params={})
        self.assertEquals(1, len(certificates))

        cert = certificates[0]
        self.verify_cert_instance(cert)

    def verify_cert_instance(self, cert):
        self.assertIsInstance(cert, _cert.Certificate)
        self.assertEqual("5b8f908b5495452aa13beede0afc5d99", cert.id)
        self.assertEqual("cert-bky", cert.name)
        self.assertEqual("certificate", cert.description)
        self.assertEqual("2016-06-27 08:14:42", cert.create_time)
        self.assertEqual("2016-06-27 08:14:42", cert.update_time)
        self.assertThat(cert.certificate,
                        matchers.Contains("BEGIN CERTIFICATE"))
        self.assertThat(cert.private_key,
                        matchers.Contains("BEGIN RSA PRIVATE KEY"))

    def test_create_cert(self):
        self.mock_response_json_file_values("create_cert_response.json")
        create_cert_body = self.get_file_content("create_cert.json")
        cert = self.proxy.create_certificate(**create_cert_body)
        self.assert_session_post_with("/elbaas/certificate",
                                      json=create_cert_body)
        self.verify_cert_instance(cert)

    def test_delete_cert_with_id(self):
        self.proxy.delete_certificate("any-cert-id")
        self.assert_session_delete(
            "elbaas/certificate/any-cert-id")

    def test_delete_cert_with_instance(self):
        self.proxy.delete_certificate(
            _cert.Certificate(id="any-cert-id"))
        self.assert_session_delete(
            "elbaas/certificate/any-cert-id")

    def test_update_cert(self):
        self.mock_response_json_file_values("create_cert_response.json")
        updated = {
            "name": "cert-bky",
            "description": "certificate"
        }
        cert = self.proxy.update_certificate("cert-id", **updated)
        self.assert_session_put_with("elbaas/certificate/cert-id",
                                     json={
                                         "name": "cert-bky",
                                         "description": "certificate"
                                     })
        self.verify_cert_instance(cert)


class TestLoadBalancerListener(TestLoadBalancerProxy):
    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerListener, self).__init__(*args, **kwargs)

    def test_list_listener(self):
        self.mock_response_json_file_values("list_listener.json")
        query = {
            "id": "id",
            "name": "name",
            "loadbalancer_id": "loadbalancer_id",
            "description": "description",
            "status": "status",
            "healthcheck_id": "healthcheck_id",
            "certificate_id": "certificate_id",
            "port": 80,
            "protocol": "protocol",
            "backend_port": 9000,
            "backend_protocol": "backend_protocol",
            "lb_algorithm": "lb_algorithm",
        }
        listeners = list(self.proxy.listeners(**query))
        self.assert_session_list_with("/elbaas/listeners",
                                      params=query)
        self.assertEquals(2, len(listeners))
        listener = listeners[0]
        self.assertIsInstance(listener, _listener.Listener)
        self.assertEqual("a824584fb3ba4d39ba0cf372c7cbbb67", listener.id)
        self.assertEqual("lis", listener.name)
        self.assertEqual("", listener.description)
        self.assertEqual("2016-12-01 07:12:43", listener.create_time)
        self.assertEqual("2016-12-01 07:12:59", listener.update_time)
        self.assertEqual(9090, listener.backend_port)
        self.assertTrue(listener.is_tcp_draining)
        self.assertEqual("TCP", listener.backend_protocol)
        self.assertEqual(None, listener.sticky_session_type)
        self.assertEqual("f54c65b1b5dd4a4f95b71b44796ac013",
                         listener.loadbalancer_id)
        self.assertEqual("ACTIVE", listener.status)
        self.assertEqual("TCP", listener.protocol)
        self.assertEqual(9092, listener.port)
        self.assertEqual(100, listener.cookie_timeout)
        self.assertEqual(False, listener.is_admin_state_up)
        self.assertEqual(True, listener.is_session_sticky)
        self.assertEqual("roundrobin", listener.lb_algorithm)
        self.assertEqual(True, listener.is_tcp_draining)
        self.assertEqual(5, listener.tcp_draining_timeout)
        self.assertEqual(None, listener.certificate_id)
        self.assertEqual(1, listener.tcp_timeout)
        self.assertEqual(0, listener.member_number)
        self.assertEqual(None, listener.healthcheck_id)

    def test_create_listener(self):
        self.mock_response_json_file_values("create_listener_response.json")
        create_listener_body = self.get_file_content("create_listener.json")
        listener = self.proxy.create_listener(**create_listener_body)
        self.assert_session_post_with("/elbaas/listeners",
                                      json=create_listener_body)
        self.assertIsInstance(listener, _listener.Listener)
        self.assertEqual("248425d7b97dc26920eb23720115e068", listener.id)
        self.assertEqual("listener1", listener.name)
        self.assertEqual("", listener.description)
        self.assertEqual("2015-09-15 07:41:17", listener.create_time)
        self.assertEqual("2015-09-15 07:41:17", listener.update_time)
        self.assertEqual(80, listener.backend_port)
        self.assertTrue(listener.is_tcp_draining)
        self.assertEqual("HTTP", listener.backend_protocol)
        self.assertEqual("insert", listener.sticky_session_type)
        self.assertEqual("0b07acf06d243925bc24a0ac7445267a",
                         listener.loadbalancer_id)
        self.assertEqual("ACTIVE", listener.status)
        self.assertEqual("TCP", listener.protocol)
        self.assertEqual(88, listener.port)
        self.assertEqual(100, listener.cookie_timeout)
        self.assertEqual(True, listener.is_admin_state_up)
        self.assertEqual(True, listener.is_session_sticky)
        self.assertEqual("roundrobin", listener.lb_algorithm)
        self.assertEqual(True, listener.is_tcp_draining)
        self.assertEqual(5, listener.tcp_draining_timeout)

    def test_delete_listener_with_id(self):
        self.proxy.delete_listener("any-listener-id")
        self.assert_session_delete(
            "elbaas/listeners/any-listener-id")

    def test_delete_listener_with_instance(self):
        self.proxy.delete_listener(
            _listener.Listener(id="any-listener-id"))
        self.assert_session_delete(
            "elbaas/listeners/any-listener-id")

    def test_update_listener(self):
        self.mock_response_json_file_values("update_listener.json")
        updated = {
            "name": "lis",
            "description": "",
            "port": 9090,
            "backend_port": 9090,
            "lb_algorithm": "roundrobin"
        }
        listener = self.proxy.update_listener("listener-id", **updated)
        self.assert_session_put_with("elbaas/listeners/listener-id",
                                     json={
                                         "name": "lis",
                                         "description": "",
                                         "port": 9090,
                                         "backend_port": 9090,
                                         "lb_algorithm": "roundrobin"
                                     })
        self.assertIsInstance(listener, _listener.Listener)
        self.assertEqual("a824584fb3ba4d39ba0cf372c7cbbb67", listener.id)
        self.assertEqual("lis", listener.name)
        self.assertEqual("", listener.description)
        self.assertEqual("2016-12-01 07:12:43", listener.create_time)
        self.assertEqual("2016-12-01 07:12:59", listener.update_time)
        self.assertEqual(9090, listener.backend_port)
        self.assertTrue(listener.is_tcp_draining)
        self.assertEqual("TCP", listener.backend_protocol)
        self.assertEqual(None, listener.sticky_session_type)
        self.assertEqual("f54c65b1b5dd4a4f95b71b44796ac013",
                         listener.loadbalancer_id)
        self.assertEqual("ACTIVE", listener.status)
        self.assertEqual("TCP", listener.protocol)
        self.assertEqual(9092, listener.port)
        self.assertEqual(100, listener.cookie_timeout)
        self.assertEqual(False, listener.is_admin_state_up)
        self.assertEqual(True, listener.is_session_sticky)
        self.assertEqual("roundrobin", listener.lb_algorithm)
        self.assertEqual(True, listener.is_tcp_draining)
        self.assertEqual(5, listener.tcp_draining_timeout)
        self.assertEqual(None, listener.certificate_id)
        self.assertEqual(1, listener.tcp_timeout)
        self.assertEqual(None, listener.member_number)
        self.assertEqual(None, listener.healthcheck_id)

    def test_add_members(self):
        self.mock_response_json_values({
            "uri": "/v1/55300f3c8f764c06b1a32e2302edc305/jobs/job-id",
            "job_id": "job-id"
        })
        members = [{"server_id": "dbecb618-2259-405f-ab17-9b68c4f541b0",
                    "address": "172.16.0.31"}]

        job = self.proxy.add_members_to_listener("listener-id", members)
        self.assert_session_post_with(
            "elbaas/listeners/listener-id/members", json=members)
        self.assertIsInstance(job, _listener.OperateMemberJob)
        self.assertEqual("job-id", job.id)

    def test_remove_members(self):
        self.mock_response_json_values({
            "uri": "/v1/55300f3c8f764c06b1a32e2302edc305/jobs/job-id",
            "job_id": "job-id"
        })
        members = ["member-id-1", "member-id-2"]
        job = self.proxy.remove_members_of_listener("listener-id", members)
        self.assert_session_post_with(
            "elbaas/listeners/listener-id/members/action",
            json={"removeMember": [{"id": "member-id-1"},
                                   {"id": "member-id-2"}]}
        )
        self.assertIsInstance(job, _listener.OperateMemberJob)
        self.assertEqual("job-id", job.id)

    def test_list_listener_member(self):
        self.mock_response_json_file_values("list_listener_members.json")
        members = list(self.proxy.listener_members("lid", limit=10))
        self.assert_session_list_with("/elbaas/listeners/lid/members",
                                      params={"limit": 10,
                                              'listener_id': 'lid'})
        self.assertEquals(2, len(members))
        member = members[0]
        self.assertIsInstance(member, _listener.Member)
        self.assertEqual("4ac8777333bc20777147ab160ea61baf", member.id)
        self.assertEqual(None, member.server_name)
        self.assertEqual("172.16.0.16", member.server_address)
        self.assertEqual("2015-12-28 10:35:50", member.create_time)
        self.assertEqual("2015-12-28 10:35:51", member.update_time)
        self.assertEqual("100.64.27.96", member.address)
        self.assertEqual("NORMAL", member.health_status)
        self.assertEqual("ACTIVE", member.status)
        self.assertEqual([{
            "id": "65093734fb966b3d70f6af26cc63e125"
        }, {
            "id": "a659fe780a542e1adf204db767a021a3"
        }], member.listeners)


class TestLoadBalancerHealthCheck(TestLoadBalancerProxy):
    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerHealthCheck, self).__init__(*args, **kwargs)

    def test_create_health_check(self):
        self.mock_response_json_file_values("create_hc.json")
        _health_check = {
            "healthcheck_connect_port": 80,
            "healthcheck_interval": 5,
            "healthcheck_protocol": "HTTP",
            "healthcheck_timeout": 10,
            "healthcheck_uri": "/",
            "healthy_threshold": 3,
            "listener_id": "3ce8c4429478a5eb6ef4930de2d75b28",
            "unhealthy_threshold": 3
        }

        hc = self.proxy.create_health_check(**_health_check)
        self.assert_session_post_with("/elbaas/healthcheck",
                                      json=_health_check)
        self.verify_hc_instance(hc)

    def test_delete_health_check_with_id(self):
        self.proxy.delete_health_check("any-hc-id")
        self.assert_session_delete("elbaas/healthcheck/any-hc-id")

    def test_delete_health_check_with_instance(self):
        self.proxy.delete_health_check(
            _hc.HealthCheck(id="any-hc-id"))
        self.assert_session_delete("elbaas/healthcheck/any-hc-id")

    def test_update_health_check(self):
        self.mock_response_json_values({
            "healthcheck_interval": 5,
            "listener_id": "3ce8c4429478a5eb6ef4930de2d75b28",
            "id": "134e5ea962327c6a574b83e6e7f31f35",
            "healthcheck_protocol": "HTTP",
            "unhealthy_threshold": 2,
            "update_time": "2015-12-25 03:57:23",
            "create_time": "2015-12-25 03:57:23",
            "healthcheck_connect_port": 88,
            "healthcheck_timeout": 10,
            "healthcheck_uri": "/",
            "healthy_threshold": 3
        })

        updated = {
            "healthcheck_connect_port": 88,
            "healthcheck_interval": 5,
            "healthcheck_protocol": "HTTP",
            "healthcheck_timeout": 10,
            "healthcheck_uri": "/",
            "healthy_threshold": 3,
            "unhealthy_threshold": 2
        }

        hc = self.proxy.update_health_check("hc-id", **updated)
        self.assert_session_put_with("elbaas/healthcheck/hc-id",
                                     json=updated)
        self.verify_hc_instance(hc)

    def test_get_hc_with_id(self):
        self.mock_response_json_values({
            "healthcheck_interval": 5,
            "listener_id": "3ce8c4429478a5eb6ef4930de2d75b28",
            "id": "134e5ea962327c6a574b83e6e7f31f35",
            "healthcheck_protocol": "HTTP",
            "unhealthy_threshold": 2,
            "update_time": "2015-12-25 03:57:23",
            "create_time": "2015-12-25 03:57:23",
            "healthcheck_connect_port": 88,
            "healthcheck_timeout": 10,
            "healthcheck_uri": "/",
            "healthy_threshold": 3
        }
        )
        hc = self.proxy.get_health_check(
            "0b07acf06d243925bc24a0ac7445267a")
        self.assert_session_get_with(
            "elbaas/healthcheck/0b07acf06d243925bc24a0ac7445267a")
        self.verify_hc_instance(hc)

    def verify_hc_instance(self, hc):
        self.assertIsInstance(hc, _hc.HealthCheck)
        self.assertEqual("134e5ea962327c6a574b83e6e7f31f35", hc.id)
        self.assertEqual("3ce8c4429478a5eb6ef4930de2d75b28", hc.listener_id)
        self.assertEqual(5, hc.healthcheck_interval)
        self.assertEqual("2015-12-25 03:57:23", hc.create_time)
        self.assertEqual("2015-12-25 03:57:23", hc.update_time)
        self.assertEqual("HTTP", hc.healthcheck_protocol)
        self.assertEqual(10, hc.healthcheck_timeout)
        self.assertEqual("/", hc.healthcheck_uri)
        self.assertEqual(3, hc.healthy_threshold)


class TestLoadBalancerQuota(TestLoadBalancerProxy):

    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerQuota, self).__init__(*args, **kwargs)

    def test_list_quota(self):
        self.mock_response_json_file_values("list_quota.json")
        quotas = list(self.proxy.quotas())
        self.assert_session_list_with("/elbaas/quotas",
                                      params={})
        self.assertEquals(2, len(quotas))
        quota = quotas[0]
        self.assertIsInstance(quota, _quota.Quota)
        self.assertEqual("elb", quota.type)
        self.assertEqual(2, quota.used)
        self.assertEqual(5, quota.quota)
        self.assertEqual(100, quota.max)
        self.assertEqual(1, quota.min)
