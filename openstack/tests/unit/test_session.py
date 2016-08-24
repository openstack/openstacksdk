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

    def test__parse_versions_response_exception(self):
        uri = "http://www.openstack.org"
        level = "DEBUG"
        sot = session.Session(None)
        sot.get = mock.Mock(side_effect=exceptions.NotFoundException)

        with self.assertLogs(logger=session.__name__, level=level) as log:
            self.assertIsNone(sot._parse_versions_response(uri))

            self.assertEqual(len(log.output), 1,
                             "Too many warnings were logged")
            self.assertEqual(
                log.output[0],
                "%s:%s:Looking for versions at %s" % (level, session.__name__,
                                                      uri))

    def test__parse_versions_response_no_json(self):
        sot = session.Session(None)
        retval = mock.Mock()
        retval.json = mock.Mock(side_effect=ValueError)
        sot.get = mock.Mock(return_value=retval)

        self.assertIsNone(sot._parse_versions_response("test"))

    def test__parse_versions_response_no_versions(self):
        sot = session.Session(None)
        retval = mock.Mock()
        retval.json = mock.Mock(return_value={"no_versions_here": "blarga"})
        sot.get = mock.Mock(return_value=retval)

        self.assertIsNone(sot._parse_versions_response("test"))

    def test__parse_versions_response_with_versions(self):
        uri = "http://openstack.org"
        versions = [1, 2, 3]

        sot = session.Session(None)
        retval = mock.Mock()
        retval.json = mock.Mock(return_value={"versions": versions})
        sot.get = mock.Mock(return_value=retval)

        expected = session.Session._Endpoint(uri, versions)
        self.assertEqual(expected, sot._parse_versions_response(uri))

    def test__parse_versions_response_with_nested_versions(self):
        uri = "http://openstack.org"
        versions = [1, 2, 3]

        sot = session.Session(None)
        retval = mock.Mock()
        retval.json = mock.Mock(return_value={"versions":
                                              {"values": versions}})
        sot.get = mock.Mock(return_value=retval)

        expected = session.Session._Endpoint(uri, versions)
        self.assertEqual(expected, sot._parse_versions_response(uri))

    def test__get_endpoint_versions_at_subdomain(self):
        # This test covers a common case of services deployed under
        # subdomains. Additionally, it covers the case of a service
        # deployed at the root, which will be the first request made
        # for versions.
        sc_uri = "https://service.cloud.com/v1/"
        versions_uri = "https://service.cloud.com"

        sot = session.Session(None)
        sot.get_project_id = mock.Mock(return_value="project_id")

        responses = [session.Session._Endpoint(versions_uri, "versions")]
        sot._parse_versions_response = mock.Mock(side_effect=responses)

        result = sot._get_endpoint_versions("type", sc_uri)

        sot._parse_versions_response.assert_called_once_with(versions_uri)
        self.assertEqual(result, responses[0])
        self.assertFalse(result.needs_project_id)

    def test__get_endpoint_versions_at_path(self):
        # This test covers a common case of services deployed under
        # a path. Additionally, it covers the case of a service
        # deployed at a path deeper than the root, which will mean
        # more than one request will need to be made.
        sc_uri = "https://cloud.com/api/service/v2/project_id"
        versions_uri = "https://cloud.com/api/service"

        sot = session.Session(None)
        sot.get_project_id = mock.Mock(return_value="project_id")

        responses = [None, None,
                     session.Session._Endpoint(versions_uri, "versions")]
        sot._parse_versions_response = mock.Mock(side_effect=responses)

        result = sot._get_endpoint_versions("type", sc_uri)

        sot._parse_versions_response.assert_has_calls(
            [mock.call("https://cloud.com"),
             mock.call("https://cloud.com/api"),
             mock.call(versions_uri)])
        self.assertEqual(result, responses[2])
        self.assertTrue(result.needs_project_id)

    def test__get_endpoint_versions_at_port(self):
        # This test covers a common case of services deployed under
        # a port.
        sc_uri = "https://cloud.com:1234/v3"
        versions_uri = "https://cloud.com:1234"

        sot = session.Session(None)
        sot.get_project_id = mock.Mock(return_value="project_id")

        responses = [session.Session._Endpoint(versions_uri, "versions")]
        sot._parse_versions_response = mock.Mock(side_effect=responses)

        result = sot._get_endpoint_versions("type", sc_uri)

        sot._parse_versions_response.assert_called_once_with(versions_uri)
        self.assertEqual(result, responses[0])
        self.assertFalse(result.needs_project_id)

    def test__parse_version(self):
        sot = session.Session(None)

        self.assertEqual(sot._parse_version("2"), (2, -1))
        self.assertEqual(sot._parse_version("v2"), (2, -1))
        self.assertEqual(sot._parse_version("v2.1"), (2, 1))
        self.assertRaises(ValueError, sot._parse_version, "lol")

    def test__get_version_match_none(self):
        sot = session.Session(None)

        endpoint = session.Session._Endpoint("root", [])
        self.assertRaises(
            exceptions.EndpointNotFound,
            sot._get_version_match, endpoint, None, "service")

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

        endpoint = session.Session._Endpoint(root_endpoint, versions)
        # Look for a v2 match, which we internally denote as a minor
        # version of -1 so we can find the highest matching minor.
        rv = sot._get_version_match(endpoint, session.Version(2, -1),
                                    "service")
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
        endpoint = session.Session._Endpoint(root_endpoint, versions)
        rv = sot._get_version_match(endpoint, session.Version(2, 0),
                                    "service")
        self.assertEqual(rv, match)

    def test__get_version_match_fragment(self):
        root = "http://cloud.net"
        match = "/v2"
        versions = [{"id": "v2.0", "links": [{"href": match, "rel": "self"}]}]

        sot = session.Session(None)
        endpoint = session.Session._Endpoint(root, versions)
        rv = sot._get_version_match(endpoint, session.Version(2, 0), "service")
        self.assertEqual(rv, root + match)

    def test__get_version_match_project_id(self):
        match = "http://devstack/v2"
        root_endpoint = "http://devstack"
        project_id = "asdf123"
        versions = [{"id": "v2.0", "links": [{"href": match, "rel": "self"}]}]

        sot = session.Session(None)
        sot.get_project_id = mock.Mock(return_value=project_id)
        endpoint = session.Session._Endpoint(root_endpoint, versions,
                                             project_id=project_id,
                                             needs_project_id=True)
        rv = sot._get_version_match(endpoint, session.Version(2, 0),
                                    "service")
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
