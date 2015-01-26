# Copyright 2011 OpenStack Foundation
# Copyright 2011, Piston Cloud Computing, Inc.
# Copyright 2011 Nebula, Inc.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import re

import six
from six.moves.urllib import parse

from openstack import exceptions


class ServiceCatalog(object):
    """Helper methods for dealing with a Keystone Service Catalog."""

    def __init__(self, catalog):
        if catalog is None:
            self.catalog = []
            raise exceptions.EmptyCatalog('The service catalog is missing')
        self.catalog = copy.deepcopy(catalog)
        self._normalize()
        self._parse_endpoints()

    def _normalize(self):
        return

    def _parse_endpoints(self):
        pattern = re.compile('/v\d[\d.]*')
        for service in self.catalog:
            for endpoint in service.get('endpoints', []):
                url = endpoint.get('url', '')
                if not url:
                    continue
                split = parse.urlsplit(url)
                split = list(split)
                path = split[2]
                vstr = pattern.search(path)
                if not vstr:
                    endpoint['url'] = (endpoint['url'].rstrip('/') +
                                       '/%(version)s')
                    continue
                start, end = vstr.span()
                endpoint['version'] = path[start + 1:end]
                path = path[:start] + '/%(version)s' + path[end:]
                path = path.rstrip('/')
                split[2] = path
                endpoint['url'] = parse.urlunsplit(split)

    def _get_endpoints(self, filtration):
        """Fetch and filter urls and version tuples for the specified service.

        Returns a tuple containting the url and version for the specified
        service (or all) containing the specified type, name, region and
        visibility.
        """
        eps = []
        for service in self.catalog:
            if not filtration.match_service_type(service.get('type')):
                continue
            if not filtration.match_service_name(service.get('name')):
                continue
            for endpoint in service.get('endpoints', []):
                if not filtration.match_region(endpoint.get('region', None)):
                    continue
                if not filtration.match_visibility(endpoint.get('interface')):
                    continue
                url = endpoint.get('url', None)
                if not url:
                    continue
                version = endpoint.get('version', None)
                eps.append((url, version))
        return eps

    def get_urls(self, filtration):
        """Fetch the urls based on the given service filter.

        Returns a list of urls based on the service filter.  If not endpoints
        are found that match the service filter, an empty list is returned.
        The filter may specify type, name, region, version and visibility.
        """
        urls = []
        for url, version in self._get_endpoints(filtration):
            version = filtration.get_version_path(version)
            url = url % {'version': version}
            urls.append(url)
        return urls

    def get_versions(self, filtration):
        """Fetch the versions based on the given service filter.

        Returns a list of versions based on the service filter.  If there is
        no endpoint matching the filter, None will be returned.  An empty
        list of versions means the service is supported, but no version is
        specified in the service catalog.  The filter may specify type, name,
        region, version and visibility.
        """
        vers = None
        for url, version in self._get_endpoints(filtration):
            vers = vers or []
            if not version:
                continue
            if filtration.version and version != filtration.version:
                continue
            vers.append(version)
        return vers

    def get_url(self, service):
        """Fetch an endpoint from the service catalog.

        Get the first endpoint that matches the service filter.

        :param ServiceFilter service: The filter to identify the desired
                                      service.
        """
        urls = self.get_urls(service)
        if len(urls) < 1:
            message = "Endpoint not found for %s" % six.text_type(service)
            raise exceptions.EndpointNotFound(message)
        return urls[0]


class ServiceCatalogV2(ServiceCatalog):
    """The V2 service catalog from Keystone."""

    def _extract_details(self, endpoint, interface):
        value = {
            'interface': interface,
            'url': endpoint['%sURL' % interface]
        }
        region = endpoint.get('region', None)
        if region:
            value['region'] = region

        return value

    def _normalize(self):
        """Handle differences in the way v2 and v3 catalogs specify endpoints.

        Normallize the v2 service catalog to the endpoint types used in v3.
        """
        for service in self.catalog:
            eps = []
            for endpoint in service['endpoints']:
                if 'publicURL' in endpoint:
                    eps += [self._extract_details(endpoint, "public")]
                if 'internalURL' in endpoint:
                    eps += [self._extract_details(endpoint, "internal")]
                if 'adminURL' in endpoint:
                    eps += [self._extract_details(endpoint, "admin")]
            service['endpoints'] = eps
