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

import six

from openstack import exceptions


class ServiceCatalog(object):
    """Helper methods for dealing with a Keystone Service Catalog."""

    def __init__(self, catalog):
        if catalog is None:
            self.catalog = []
            raise exceptions.EmptyCatalog('The service catalog is missing')
        self.catalog = copy.deepcopy(catalog)

    def get_urls(self, filtration):
        """Fetch and filter endpoints for the specified service.

        Returns endpoints for the specified service (or all) containing
        the specified type (or all) and region (or all) and service name.

        If there is no name in the service catalog the service_name check will
        be skipped.  This allows compatibility with services that existed
        before the name was available in the catalog.
        """
        eps = []
        for service in self.catalog:
            if not filtration.match_service_type(service.get('type')):
                continue
            if not filtration.match_service_name(service.get('name')):
                continue
            for endpoint in service.get('endpoints', []):
                if not filtration.match_region(endpoint.get('region')):
                    continue
                if not filtration.match_visibility(endpoint.get('interface')):
                    continue
                url = endpoint.get('url')
                if url is not None:
                    eps += [url]
        return eps

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
    """The V2 service catalog from Keystone.
    """
    def __init__(self, catalog):
        super(ServiceCatalogV2, self).__init__(catalog)
        self._normalize()

    def _normalize(self):
        """Handle differences in the way v2 and v3 catalogs specify endpoints.

        Normallize the v2 service catalog to the endpoint types used in v3.
        """
        for service in self.catalog:
            eps = []
            for endpoint in service['endpoints']:
                if 'adminURL' in endpoint:
                    eps += [{
                        'interface': 'admin',
                        'region': endpoint['region'],
                        'url': endpoint['adminURL'],
                    }]
                if 'internalURL' in endpoint:
                    eps += [{
                        'interface': 'internal',
                        'region': endpoint['region'],
                        'url': endpoint['internalURL'],
                    }]
                if 'publicURL' in endpoint:
                    eps += [{
                        'interface': 'public',
                        'region': endpoint['region'],
                        'url': endpoint['publicURL'],
                    }]
            service['endpoints'] = eps
