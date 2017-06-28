class TestLoadBalancerHealthCheck(TestLoadBalancerProxy):
    def __init__(self, *args, **kwargs):
        super(TestLoadBalancerHealthCheck, self).__init__(*args, **kwargs)

    def test_list_listener(self):
        self.mock_response_json_file_values("list_listener.json")
        listeners = list(self.proxy.listeners())
        self.assert_session_list_with("/elbaas/listeners",
                                      params={})
        self.assertEquals(2, len(listeners))
        listener = listeners[0]
        self.assertIsInstance(listener, _hc.HealthCheck)
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
        self.assertIsInstance(listener, _hc.HealthCheck)
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
            _listener.HealthCheck(id="any-listener-id"))
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
        self.assertIsInstance(listener, _hc.HealthCheck)
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