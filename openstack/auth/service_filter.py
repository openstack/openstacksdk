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
The ``ServiceFilter`` is the base class for service identifiers and user
service preferences.  Each
:class:`Resource <openstack.resource.Resource>` has a service identifier to
associate the resource with a service.  An example of a service identifier
would be ``openstack.compute.compute_service.ComputeService``.
The preferences are stored in the
:class:`UserPreference <openstack.user_preference.UserPreference>` object.
The service preference and the service identifier are joined to create a
filter to match a service.
"""

from openstack import exceptions


class ServiceFilter(object):
    ANY = 'any'
    PUBLIC = 'public'
    INTERNAL = 'internal'
    ADMIN = 'admin'
    VISIBILITY = [PUBLIC, INTERNAL, ADMIN]

    def __init__(self, service_type=ANY, visibility=PUBLIC, region=None,
                 service_name=None, version=None):
        """Create a service identifier.

        :param string service_type: The desired type of service.
        :param string visibility: The exposure of the endpoint. Should be
                                  `public` (default), `internal` or `admin`.
        :param string region: The desired region (optional).
        :param string service_name: Name of the service
        :param string version: Version of service to use.
        """
        self.service_type = service_type.lower()
        self.set_visibility(visibility)
        self.region = region
        self.service_name = service_name
        self.version = version

    def __repr__(self):
        ret = "service_type=%s" % self.service_type
        if self.visibility is not None:
            ret += ",visibility=%s" % self.visibility
        if self.region is not None:
            ret += ",region=%s" % self.region
        if self.service_name:
            ret += ",service_name=%s" % self.service_name
        if self.version:
            ret += ",version=%s" % self.version
        return ret

    def join(self, default):
        """Create a new service filter by joining filters.

        Create a new service filter by joining this service preference with
        the default service identifier.

        :param default: Default service identifier from the resource.
        :type default: :class:`openstack.auth.service_filter.ServiceFilter`
        """
        return ServiceFilter(service_type=default.service_type,
                             visibility=self.visibility or default.visibility,
                             region=self.region,
                             service_name=self.service_name,
                             version=self.version)

    def match_service_type(self, service_type):
        """Service types are equavilent."""
        if self.service_type == self.ANY:
            return True
        return self.service_type == service_type

    def match_service_name(self, service_name):
        """Service names are equavilent."""
        if not self.service_name:
            return True
        if self.service_name == service_name:
            return True
        return False

    def match_region(self, region):
        """Service regions are equavilent."""
        if not self.region:
            return True
        if self.region == region:
            return True
        return False

    def match_visibility(self, visibility):
        """Service visibilities are equavilent."""
        if not self.visibility:
            return True
        return self.visibility == visibility

    def set_visibility(self, visibility):
        """Set the visibility of the service filter."""
        if not visibility:
            self.visibility = None
            return
        visibility = visibility.replace('URL', '')
        visibility = visibility.lower()
        if visibility not in self.VISIBILITY:
            msg = "Visibility <%s> not in %s" % (visibility, self.VISIBILITY)
            raise exceptions.SDKException(msg)
        self.visibility = visibility
