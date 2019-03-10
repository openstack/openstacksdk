# Copyright (c) 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' Wrapper around keystoneauth Adapter to wrap calls in TaskManager '''

try:
    import simplejson
    JSONDecodeError = simplejson.scanner.JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from six.moves import urllib
from keystoneauth1 import adapter

from openstack import exceptions


def _extract_name(url, service_type=None):
    '''Produce a key name to use in logging/metrics from the URL path.

    We want to be able to logic/metric sane general things, so we pull
    the url apart to generate names. The function returns a list because
    there are two different ways in which the elements want to be combined
    below (one for logging, one for statsd)

    Some examples are likely useful:

    /servers -> ['servers']
    /servers/{id} -> ['servers']
    /servers/{id}/os-security-groups -> ['servers', 'os-security-groups']
    /v2.0/networks.json -> ['networks']
    '''

    url_path = urllib.parse.urlparse(url).path.strip()
    # Remove / from the beginning to keep the list indexes of interesting
    # things consistent
    if url_path.startswith('/'):
        url_path = url_path[1:]

    # Special case for neutron, which puts .json on the end of urls
    if url_path.endswith('.json'):
        url_path = url_path[:-len('.json')]

    url_parts = url_path.split('/')
    if url_parts[-1] == 'detail':
        # Special case detail calls
        # GET /servers/detail
        # returns ['servers', 'detail']
        name_parts = url_parts[-2:]
    else:
        # Strip leading version piece so that
        # GET /v2.0/networks
        # returns ['networks']
        if url_parts[0] in ('v1', 'v2', 'v2.0'):
            url_parts = url_parts[1:]
        name_parts = []
        # Pull out every other URL portion - so that
        # GET /servers/{id}/os-security-groups
        # returns ['servers', 'os-security-groups']
        for idx in range(0, len(url_parts)):
            if not idx % 2 and url_parts[idx]:
                name_parts.append(url_parts[idx])

    # Keystone Token fetching is a special case, so we name it "tokens"
    if url_path.endswith('tokens'):
        name_parts = ['tokens']

    # Getting the root of an endpoint is doing version discovery
    if not name_parts:
        if service_type == 'object-store':
            name_parts = ['account']
        else:
            name_parts = ['discovery']

    # Strip out anything that's empty or None
    return [part for part in name_parts if part]


def _json_response(response, result_key=None, error_message=None):
    """Temporary method to use to bridge from ShadeAdapter to SDK calls."""
    exceptions.raise_from_response(response, error_message=error_message)

    if not response.content:
        # This doesn't have any content
        return response

    # Some REST calls do not return json content. Don't decode it.
    if 'application/json' not in response.headers.get('Content-Type'):
        return response

    try:
        result_json = response.json()
    except JSONDecodeError:
        return response
    return result_json


class OpenStackSDKAdapter(adapter.Adapter):
    """Wrapper around keystoneauth1.adapter.Adapter."""

    def __init__(
            self, session=None,
            *args, **kwargs):
        super(OpenStackSDKAdapter, self).__init__(
            session=session, *args, **kwargs)

    def request(
            self, url, method, error_message=None,
            raise_exc=False, connect_retries=1, *args, **kwargs):
        response = super(OpenStackSDKAdapter, self).request(
            url, method,
            connect_retries=connect_retries, raise_exc=False,
            **kwargs)
        return response

    def _version_matches(self, version):
        api_version = self.get_api_major_version()
        if api_version:
            return api_version[0] == version
        return False


class ShadeAdapter(OpenStackSDKAdapter):
    """Wrapper for shade methods that expect json unpacking."""

    def request(self, url, method, error_message=None, **kwargs):
        response = super(ShadeAdapter, self).request(url, method, **kwargs)
        return _json_response(response, error_message=error_message)
