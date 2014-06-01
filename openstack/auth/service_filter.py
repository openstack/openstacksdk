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

    PUBLIC = 'public'
    INTERNAL = 'internal'
    ADMIN = 'admin'
    VISIBILITY = [PUBLIC, INTERNAL, ADMIN]

    def __init__(self, service_type, visibility=PUBLIC, region=None,
                 service_name=None):
        """" Create a service identifier.

        :param string service_type: The desired type of service.
        :param string visibility: The exposure of the endpoint. Should be
                                  `public` (default), `internal` or `admin`.
        :param string region: The desired region (optional).
        :param string service_name: Name of the service
        """
        self.service_type = service_type
        if not service_type:
            msg = "Service type must be specified to locate service"
            raise exceptions.SdkException(msg)
        if not visibility:
            msg = "Visibility must be specified to locate service"
            raise exceptions.SdkException(msg)
        visibility = visibility.rstrip('URL')
        if visibility not in self.VISIBILITY:
            msg = "Visibility <%s> not in %s" % (visibility, self.VISIBILITY)
            raise exceptions.SdkException(msg)
        self.visibility = visibility
        self.region = region
        self.service_name = service_name

    def __repr__(self):
        ret = "service_type=%s" % self.service_type
        ret += ",visibility=%s" % self.visibility
        if self.region is not None:
            ret += ",region=%s" % self.region
        if self.service_name:
            ret += ",service_name=%s" % self.service_name
        return ret

    def match_service_type(self, service_type):
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
        return self.visibility == visibility
