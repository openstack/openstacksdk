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

from openstack import exceptions


class ServiceFilter(object):
    """The basic structure of an authentication plugin."""

    ANY = 'any'
    PUBLIC = 'public'
    INTERNAL = 'internal'
    ADMIN = 'admin'
    VISIBILITY = [PUBLIC, INTERNAL, ADMIN]

    def __init__(self, service_type=ANY, visibility=PUBLIC, region=None,
                 service_name=None, version=None):
        """" Create a service identifier.

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
        return ServiceFilter(service_type=default.service_type,
                             visibility=self.visibility or default.visibility,
                             region=self.region,
                             service_name=self.service_name,
                             version=self.version)

    def match_service_type(self, service_type):
        if self.service_type == self.ANY:
            return True
        return self.service_type == service_type

    def match_service_name(self, service_name):
        if not self.service_name:
            return True
        if self.service_name == service_name:
            return True
        return False

    def match_region(self, region):
        if not self.region:
            return True
        if self.region == region:
            return True
        return False

    def match_visibility(self, visibility):
        if not self.visibility:
            return True
        return self.visibility == visibility

    def set_visibility(self, visibility):
        if not visibility:
            self.visibility = None
            return
        visibility = visibility.replace('URL', '')
        visibility = visibility.lower()
        if visibility not in self.VISIBILITY:
            msg = "Visibility <%s> not in %s" % (visibility, self.VISIBILITY)
            raise exceptions.SDKException(msg)
        self.visibility = visibility
