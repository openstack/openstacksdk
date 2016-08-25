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
import testtools

from keystoneauth1 import exceptions as _exceptions

from openstack import exceptions
from openstack import profile
from openstack import session
from openstack import utils


class TestSession(testtools.TestCase):

    def test_init_user_agent_none(self):
        sot = session.Session(None)
        self.assertTrue(sot.user_agent.startswith("openstacksdk"))

    def test_init_user_agent_set(self):
        sot = session.Session(None, user_agent="testing/123")
        self.assertTrue(sot.user_agent.startswith("testing/123 openstacksdk"))

    def test_init_with_single_api_request(self):
        prof = profile.Profile()
        prof.set_api_version('clustering', '1.2')

        sot = session.Session(prof)

        # The assertion acutally tests the property assigned in parent class
        self.assertEqual({'openstack-api-version': 'clustering 1.2'},
                         sot.additional_headers)

    def test_init_with_multi_api_requests(self):
        prof = profile.Profile()
        prof.set_api_version('clustering', '1.2')
        prof.set_api_version('compute', '2.15')

        sot = session.Session(prof)

        versions = sot.additional_headers['openstack-api-version']
        requests = [req.strip() for req in versions.split(',')]
        self.assertIn('clustering 1.2', requests)
        self.assertIn('compute 2.15', requests)

    def test_init_with_no_api_requests(self):
        prof = profile.Profile()

        sot = session.Session(prof)

        self.assertEqual({}, sot.additional_headers)

    def test_map_exceptions_not_found_exception(self):
        ksa_exc = _exceptions.HttpError(message="test", http_status=404)
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.NotFoundException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.NotFoundException)
        self.assertEqual(ksa_exc.message, os_exc.message)
        self.assertEqual(ksa_exc.http_status, os_exc.http_status)
        self.assertEqual(ksa_exc, os_exc.cause)

    def test_map_exceptions_http_exception(self):
        ksa_exc = _exceptions.HttpError(message="test", http_status=400)
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.HttpException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.HttpException)
        self.assertEqual(ksa_exc.message, os_exc.message)
        self.assertEqual(ksa_exc.http_status, os_exc.http_status)
        self.assertEqual(ksa_exc, os_exc.cause)

    def test_map_exceptions_sdk_exception_1(self):
        ksa_exc = _exceptions.ClientException()
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.SDKException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.SDKException)
        self.assertEqual(ksa_exc, os_exc.cause)

    def test_map_exceptions_sdk_exception_2(self):
        ksa_exc = _exceptions.VersionNotAvailable()
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.SDKException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.SDKException)
        self.assertEqual(ksa_exc, os_exc.cause)

    def _test__get_endpoint_versions(self, body, versions, endpoint=None):
        sot = session.Session(None)

        fake_response = mock.Mock()
        fake_response.json = mock.Mock(return_value=body)
        sot.get = mock.Mock(return_value=fake_response)

        if endpoint is None:
            # default case with port numbers, we strip the path to get base
            endpoint = 'https://hostname:1234/v2.1/project_id'
            root = 'https://hostname:1234'
        else:
            # otherwise we preserve the whole URI
            root = endpoint

        rv = sot._get_endpoint_versions("compute", endpoint)

        sot.get.assert_called_with(root)

        self.assertEqual(root, rv[0])
        self.assertEqual(versions, rv[1])

    def test__get_endpoint_versions_nested(self):
        versions = [{"id": "v2.0"}, {"id": "v2.1"}]
        body = {"versions": {"values": versions}}
        self._test__get_endpoint_versions(body, versions)

    def test__get_endpoint_versions(self):
        versions = [{"id": "v2.0"}, {"id": "v2.1"}]
        body = {"versions": versions}
        self._test__get_endpoint_versions(body, versions)

    def test__get_endpoint_versions_apache_case(self):
        # test for service running in apache, i.e. those that doesn't have a
        # port number in its endpoint URI but the path in its URI should be
        # preserved.
        versions = [{"id": "v2.0"}, {"id": "v2.1"}]
        body = {"versions": versions}
        self._test__get_endpoint_versions(
            body, versions, endpoint='http://hostname/service_path')

    def test__get_endpoint_versions_exception(self):
        sot = session.Session(None)

        fake_response = mock.Mock()
        fake_response.json = mock.Mock(return_value={})
        sot.get = mock.Mock(return_value=fake_response)

        self.assertRaises(exceptions.EndpointNotFound,
                          sot._get_endpoint_versions, "service", "endpoint")

    def test__parse_version(self):
        sot = session.Session(None)

        self.assertEqual(sot._parse_version("2"), (2, -1))
        self.assertEqual(sot._parse_version("v2"), (2, -1))
        self.assertEqual(sot._parse_version("v2.1"), (2, 1))
        self.assertRaises(ValueError, sot._parse_version, "lol")

    def test__get_version_match_none(self):
        sot = session.Session(None)

        self.assertRaises(
            exceptions.EndpointNotFound,
            sot._get_version_match, [], None, "service", "root", False)

    def test__get_version_match_fuzzy(self):
        match = "http://devstack/v2.1"
        root_endpoint = "http://devstack"
        versions = [{"id": "v2.0",
                     "links": [{"href": "http://devstack/v2/",
                                "rel": "self"}]},
                    {"id": "v2.1",
                     "links": [{"href": match,
                                "rel": "self"}]}]

        sot = session.Session(None)
        # Look for a v2 match, which we internally denote as a minor
        # version of -1 so we can find the highest matching minor.
        rv = sot._get_version_match(versions, session.Version(2, -1),
                                    "service", root_endpoint, False)
        self.assertEqual(rv, match)

    def test__get_version_match_exact(self):
        match = "http://devstack/v2"
        root_endpoint = "http://devstack"
        versions = [{"id": "v2.0",
                     "links": [{"href": match,
                                "rel": "self"}]},
                    {"id": "v2.1",
                     "links": [{"href": "http://devstack/v2.1/",
                                "rel": "self"}]}]

        sot = session.Session(None)
        rv = sot._get_version_match(versions, session.Version(2, 0),
                                    "service", root_endpoint, False)
        self.assertEqual(rv, match)

    def test__get_version_match_fragment(self):
        root = "http://cloud.net"
        match = "/v2"
        versions = [{"id": "v2.0", "links": [{"href": match, "rel": "self"}]}]

        sot = session.Session(None)
        rv = sot._get_version_match(versions, session.Version(2, 0),
                                    "service", root, False)
        self.assertEqual(rv, root+match)

    def test__get_version_match_project_id(self):
        match = "http://devstack/v2"
        root_endpoint = "http://devstack"
        project_id = "asdf123"
        versions = [{"id": "v2.0", "links": [{"href": match, "rel": "self"}]}]

        sot = session.Session(None)
        sot.get_project_id = mock.Mock(return_value=project_id)
        rv = sot._get_version_match(versions, session.Version(2, 0),
                                    "service", root_endpoint, True)
        match_endpoint = utils.urljoin(match, project_id)
        self.assertEqual(rv, match_endpoint)

    def test_get_endpoint_cached(self):
        sot = session.Session(None)
        service_type = "compute"
        interface = "public"
        endpoint = "the world wide web"

        sot.endpoint_cache[(service_type, interface)] = endpoint
        rv = sot.get_endpoint(service_type=service_type, interface=interface)
        self.assertEqual(rv, endpoint)
