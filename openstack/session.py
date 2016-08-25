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

"""
The :class:`~openstack.session.Session` overrides
:class:`~keystoneauth1.session.Session` to provide end point filtering and
mapping KSA exceptions to SDK exceptions.

"""
from collections import namedtuple

from keystoneauth1 import exceptions as _exceptions
from keystoneauth1 import session as _session

from openstack import exceptions
from openstack import utils
from openstack import version as openstack_version

from six.moves.urllib import parse

DEFAULT_USER_AGENT = "openstacksdk/%s" % openstack_version.__version__
API_REQUEST_HEADER = "openstack-api-version"

Version = namedtuple("Version", ["major", "minor"])


def map_exceptions(func):
    def map_exceptions_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except _exceptions.HttpError as e:
            if e.http_status == 404:
                raise exceptions.NotFoundException(
                    message=e.message, details=e.details,
                    response=e.response, request_id=e.request_id,
                    url=e.url, method=e.method,
                    http_status=e.http_status, cause=e)
            else:
                raise exceptions.HttpException(
                    message=e.message, details=e.details,
                    response=e.response, request_id=e.request_id,
                    url=e.url, method=e.method,
                    http_status=e.http_status, cause=e)
        except _exceptions.ClientException as e:
            raise exceptions.SDKException(message=e.message, cause=e)

    return map_exceptions_wrapper


class Session(_session.Session):

    def __init__(self, profile, user_agent=None, **kwargs):
        """Create a new Keystone auth session with a profile.

        :param profile: If the user has any special profiles such as the
            service name, region, version or interface, they may be provided
            in the profile object.  If no profiles are provided, the
            services that appear first in the service catalog will be used.
        :param user_agent: A User-Agent header string to use for the
                           request. If not provided, a default of
                           :attr:`~openstack.session.DEFAULT_USER_AGENT`
                           is used, which contains the openstacksdk version
                           When a non-None value is passed, it will be
                           prepended to the default.
        :type profile: :class:`~openstack.profile.Profile`
        """
        if user_agent is not None:
            self.user_agent = "%s %s" % (user_agent, DEFAULT_USER_AGENT)
        else:
            self.user_agent = DEFAULT_USER_AGENT

        self.profile = profile
        api_version_header = self._get_api_requests()
        self.endpoint_cache = {}

        super(Session, self).__init__(user_agent=self.user_agent,
                                      additional_headers=api_version_header,
                                      **kwargs)

    def _get_api_requests(self):
        """Get API micro-version requests.

        :param profile: A profile object that contains customizations about
                        service name, region, version, interface or
                        api_version.
        :return: A standard header string if there is any specialization in
                 API microversion, or None if no such request exists.
        """
        if self.profile is None:
            return None

        req = []
        for svc in self.profile.get_services():
            if svc.service_type and svc.api_version:
                req.append(" ".join([svc.service_type, svc.api_version]))
        if req:
            return {API_REQUEST_HEADER: ",".join(req)}

        return None

    def _get_endpoint_versions(self, service_type, endpoint):
        """Get available endpoints from the remote service

        Take the endpoint that the Service Catalog gives us, then split off
        anything and just take the root. We need to make a request there
        to get the versions the API exposes.
        """
        parts = parse.urlparse(endpoint)
        if ':' in parts.netloc:
            root_endpoint = "://".join([parts.scheme, parts.netloc])
        else:
            root_endpoint = endpoint

        response = self.get(root_endpoint)

        # Normalize the version response. Identity nests the versions
        # a level deeper than others, inside of a "values" dictionary.
        response_body = response.json()
        if "versions" in response_body:
            versions = response_body["versions"]
            if "values" in versions:
                versions = versions["values"]
            return root_endpoint, versions

        raise exceptions.EndpointNotFound(
            "Unable to parse endpoints for %s" % service_type)

    def _parse_version(self, version):
        """Parse the version and return major and minor components

        If the version was given with a leading "v", e.g., "v3", strip
        that off to just numerals.
        """
        version_num = version[version.find("v") + 1:]
        components = version_num.split(".")
        if len(components) == 1:
            # The minor version of a v2 ends up being -1 so that we can
            # loop through versions taking the highest available match
            # while also working around a direct match for 2.0.
            rv = Version(int(components[0]), -1)
        elif len(components) == 2:
            rv = Version(*[int(component) for component in components])
        else:
            raise ValueError("Unable to parse version string %s" % version)

        return rv

    def _get_version_match(self, versions, profile_version, service_type,
                           root_endpoint, requires_project_id):
        """Return the best matching version

        Look through each version trying to find the best match for
        the version specified in this profile.
         * The best match will only ever be found within the same
           major version, meaning a v2 profile will never match if
           only v3 is available on the server.
         * The search for the best match is fuzzy if needed.
           * If the profile specifies v2 and the server has
             v2.0, v2.1, and v2.2, the match will be v2.2.
           * When an exact major/minor is specified, e.g., v2.0,
             it will only match v2.0.
        """

        match_version = None

        for version in versions:
            api_version = self._parse_version(version["id"])
            if profile_version.major != api_version.major:
                continue

            if profile_version.minor <= api_version.minor:
                for link in version["links"]:
                    if link["rel"] == "self":
                        resp_link = link['href']
                        match_version = parse.urlsplit(resp_link).path

            # Only break out of the loop on an exact match,
            # otherwise keep trying.
            if profile_version.minor == api_version.minor:
                break

        if match_version is None:
            raise exceptions.EndpointNotFound(
                "Unable to determine endpoint for %s" % service_type)

        # Make sure "root_endpoint" has no overlap with match_version
        root_parts = parse.urlsplit(root_endpoint)
        match_version = match_version.replace(root_parts.path, "", 1)
        match = utils.urljoin(root_endpoint, match_version)

        # For services that require the project id in the request URI,
        # add them in here.
        if requires_project_id:
            match = utils.urljoin(match, self.get_project_id())

        return match

    def get_endpoint(self, auth=None, interface=None, service_type=None,
                     **kwargs):
        """Override get endpoint to automate endpoint filtering

        This method uses the service catalog to find the root URI of
        each service and then gets all available versions directly
        from the service, not from the service catalog.

        Endpoints are cached per service type and interface combination
        so that they're only requested from the remote service once
        per instance of this class.
        """
        key = (service_type, interface)
        if key in self.endpoint_cache:
            return self.endpoint_cache[key]

        filt = self.profile.get_filter(service_type)
        if filt.interface is None:
            filt.interface = interface
        sc_endpoint = super(Session, self).get_endpoint(auth,
                                                        **filt.get_filter())

        # Object Storage is, of course, different. Just use what we get
        # back from the service catalog as not only does it not offer
        # a list of supported versions, it appends an "AUTH_" prefix to
        # the project id so we'd have to special case that as well.
        if service_type == "object-store":
            self.endpoint_cache[key] = sc_endpoint
            return sc_endpoint

        root_endpoint, versions = self._get_endpoint_versions(service_type,
                                                              sc_endpoint)
        profile_version = self._parse_version(filt.version)
        match = self._get_version_match(versions, profile_version,
                                        service_type, root_endpoint,
                                        filt.requires_project_id)

        self.endpoint_cache[key] = match
        return match

    @map_exceptions
    def request(self, *args, **kwargs):
        return super(Session, self).request(*args, **kwargs)
