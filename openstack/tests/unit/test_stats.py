# Copyright 2013 Hewlett-Packard Development Company, L.P.
# Copyright 2014 OpenStack Foundation
# Copyright 2018 Red Hat, Inc.
#
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

import itertools
import os
import pprint
import select
import socket
import threading
import time

import fixtures
from keystoneauth1 import exceptions
import prometheus_client
from requests import exceptions as rexceptions
import testtools.content

from openstack.tests.unit import base


class StatsdFixture(fixtures.Fixture):
    def _setUp(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.port = self.sock.getsockname()[1]
        self.wake_read, self.wake_write = os.pipe()
        self.stats = []
        self.thread.start()
        self.addCleanup(self._cleanup)

    def run(self):
        while self.running:
            poll = select.poll()
            poll.register(self.sock, select.POLLIN)
            poll.register(self.wake_read, select.POLLIN)
            ret = poll.poll()
            for fd, event in ret:
                if fd == self.sock.fileno():
                    data = self.sock.recvfrom(1024)
                    if not data:
                        return
                    self.stats.append(data[0])
                if fd == self.wake_read:
                    return

    def _cleanup(self):
        self.running = False
        os.write(self.wake_write, b'1\n')
        self.thread.join()


class TestStats(base.TestCase):
    def setUp(self):
        self.statsd = StatsdFixture()
        self.useFixture(self.statsd)
        # note, use 127.0.0.1 rather than localhost to avoid getting ipv6
        # see: https://github.com/jsocol/pystatsd/issues/61
        self.useFixture(
            fixtures.EnvironmentVariable('STATSD_HOST', '127.0.0.1')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('STATSD_PORT', str(self.statsd.port))
        )

        self.add_info_on_exception('statsd_content', self.statsd.stats)
        # Set up the above things before the super setup so that we have the
        # environment variables set when the Connection is created.
        super().setUp()

        self._registry = prometheus_client.CollectorRegistry()
        self.cloud.config._collector_registry = self._registry
        self.addOnException(self._add_prometheus_samples)

    def _add_prometheus_samples(self, exc_info):
        samples = []
        for metric in self._registry.collect():
            for s in metric.samples:
                samples.append(s)
        self.addDetail(
            'prometheus_samples',
            testtools.content.text_content(pprint.pformat(samples)),
        )

    def assert_reported_stat(self, key, value=None, kind=None):
        """Check statsd output

        Check statsd return values.  A ``value`` should specify a
        ``kind``, however a ``kind`` may be specified without a
        ``value`` for a generic match.  Leave both empty to just check
        for key presence.

        :arg str key: The statsd key
        :arg str value: The expected value of the metric ``key``
        :arg str kind: The expected type of the metric ``key``  For example

          - ``c`` counter
          - ``g`` gauge
          - ``ms`` timing
          - ``s`` set

        Note that for ``ms`` type, you are expressing a maximum value,
        not an exact value. This is to avoid flakey tests.
        """

        self.assertIsNotNone(self.statsd)

        if value:
            self.assertNotEqual(kind, None)

        start = time.time()
        while time.time() < (start + 1):
            # Note our fake statsd just queues up results in a queue.
            # We just keep going through them until we find one that
            # matches, or fail out.  If statsd pipelines are used,
            # large single packets are sent with stats separated by
            # newlines; thus we first flatten the stats out into
            # single entries.
            stats = itertools.chain.from_iterable(
                [s.decode('utf-8').split('\n') for s in self.statsd.stats]
            )
            for stat in stats:
                k, v = stat.split(':')
                if key == k:
                    if kind is None:
                        # key with no qualifiers is found
                        return True

                    s_value, s_kind = v.split('|')

                    # if no kind match, look for other keys
                    if kind != s_kind:
                        continue

                    if value:
                        # special-case value|ms because statsd can turn
                        # timing results into float of indeterminate
                        # length, hence foiling string matching.
                        if kind == 'ms':
                            if float(value) >= float(s_value):
                                return True
                        elif value == s_value:
                            return True
                        # otherwise keep looking for other matches
                        continue

                    # this key matches
                    return True
            time.sleep(0.1)

        raise Exception(f"Key {key} not found in reported stats")

    def assert_prometheus_stat(self, name, value, labels=None):
        sample_value = self._registry.get_sample_value(name, labels)
        self.assertEqual(sample_value, value)

    def test_list_projects(self):
        mock_uri = self.get_mock_url(
            service_type='identity', resource='projects', base_url_append='v3'
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=mock_uri,
                    status_code=200,
                    json={'projects': []},
                )
            ]
        )

        self.cloud.list_projects()
        self.assert_calls()

        self.assert_reported_stat(
            'openstack.api.identity.GET.projects.200', value='1', kind='c'
        )
        self.assert_prometheus_stat(
            'openstack_http_requests_total',
            1,
            dict(
                service_type='identity',
                endpoint=mock_uri,
                method='GET',
                status_code='200',
            ),
        )

    def test_projects(self):
        mock_uri = self.get_mock_url(
            service_type='identity', resource='projects', base_url_append='v3'
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=mock_uri,
                    status_code=200,
                    json={'projects': []},
                )
            ]
        )

        list(self.cloud.identity.projects())
        self.assert_calls()

        self.assert_reported_stat(
            'openstack.api.identity.GET.projects.200', value='1', kind='c'
        )
        self.assert_prometheus_stat(
            'openstack_http_requests_total',
            1,
            dict(
                service_type='identity',
                endpoint=mock_uri,
                method='GET',
                status_code='200',
            ),
        )

    def test_servers(self):
        mock_uri = 'https://compute.example.com/v2.1/servers/detail'

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=mock_uri,
                    status_code=200,
                    json={'servers': []},
                ),
            ]
        )

        list(self.cloud.compute.servers())
        self.assert_calls()

        self.assert_reported_stat(
            'openstack.api.compute.GET.servers_detail.200', value='1', kind='c'
        )
        self.assert_reported_stat(
            'openstack.api.compute.GET.servers_detail.200',
            value='5',
            kind='ms',
        )
        self.assert_prometheus_stat(
            'openstack_http_requests_total',
            1,
            dict(
                service_type='compute',
                endpoint=mock_uri,
                method='GET',
                status_code='200',
            ),
        )

    def test_servers_no_detail(self):
        mock_uri = 'https://compute.example.com/v2.1/servers'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=mock_uri,
                    status_code=200,
                    json={'servers': []},
                )
            ]
        )

        self.cloud.compute.get('/servers')
        self.assert_calls()

        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.200', value='1', kind='c'
        )
        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.200', value='5', kind='ms'
        )
        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.attempted', value='1', kind='c'
        )
        self.assert_prometheus_stat(
            'openstack_http_requests_total',
            1,
            dict(
                service_type='compute',
                endpoint=mock_uri,
                method='GET',
                status_code='200',
            ),
        )

    def test_servers_error(self):
        mock_uri = 'https://compute.example.com/v2.1/servers'

        self.register_uris(
            [dict(method='GET', uri=mock_uri, status_code=500, json={})]
        )

        self.cloud.compute.get('/servers')
        self.assert_calls()

        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.500', value='1', kind='c'
        )
        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.500', value='5', kind='ms'
        )
        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.attempted', value='1', kind='c'
        )
        self.assert_prometheus_stat(
            'openstack_http_requests_total',
            1,
            dict(
                service_type='compute',
                endpoint=mock_uri,
                method='GET',
                status_code='500',
            ),
        )

    def test_timeout(self):
        mock_uri = 'https://compute.example.com/v2.1/servers'

        self.register_uris(
            [dict(method='GET', uri=mock_uri, exc=rexceptions.ConnectTimeout)]
        )

        try:
            self.cloud.compute.get('/servers')
        except exceptions.ConnectTimeout:
            pass

        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.failed', value='1', kind='c'
        )
        self.assert_reported_stat(
            'openstack.api.compute.GET.servers.attempted', value='1', kind='c'
        )


class TestNoStats(base.TestCase):
    def setUp(self):
        super().setUp()
        self.statsd = StatsdFixture()
        self.useFixture(self.statsd)

    def test_no_stats(self):
        mock_uri = self.get_mock_url(
            service_type='identity', resource='projects', base_url_append='v3'
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=mock_uri,
                    status_code=200,
                    json={'projects': []},
                )
            ]
        )

        self.cloud.identity._statsd_client = None
        list(self.cloud.identity.projects())
        self.assert_calls()
        self.assertEqual([], self.statsd.stats)
