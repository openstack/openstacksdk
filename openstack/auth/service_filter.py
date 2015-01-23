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
The :class:`~openstack.auth.service_filter.ServiceFilter` is the base class
for service identifiers and user service preferences.  Each
:class:`~openstack.resource.Resource` has a service identifier to
associate the resource with a service.  An example of a service identifier
would be ``openstack.compute.compute_service.ComputeService``.
The preferences are stored in the
:class:`~openstack.user_preference.UserPreference` object.
The service preference and the service identifier are joined to create a
filter to match a service.

Examples
--------

The :class:`~openstack.auth.service_filter.ServiceFilter` class can be built
with a service type, visibility, region, name, and version.

Create a service filter
~~~~~~~~~~~~~~~~~~~~~~~

Create a compute service and service preference. Join the services
and match::

    from openstack.auth import service_filter
    from openstack.compute import compute_service
    default = compute_service.ComputeService()
    preference = service_filter.ServiceFilter('compute', version='v2')
    result = preference.join(default)
    matches = (result.match_service_type('compute') and
               result.match_service_name('Hal9000') and
               result.match_region('DiscoveryOne') and
               result.match_visibility('public'))
    print(str(result))
    print("matches=" + str(matches))

The resulting output from the code::

    service_type=compute,visibility=public,version=v2
    matches=True
"""

from openstack import exceptions


class ValidVersion(object):

    def __init__(self, module, path=None):
        """" Valid service version.

        :param string module: Module associated with version.
        :param string path: URL path version.
        """
        self.module = module
        self.path = path or module


class ServiceFilter(object):
    UNVERSIONED = ''
    ANY = 'any'
    PUBLIC = 'public'
    INTERNAL = 'internal'
    ADMIN = 'admin'
    VISIBILITY = [PUBLIC, INTERNAL, ADMIN]
    valid_versions = []

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
        :type default: :class:`~openstack.auth.service_filter.ServiceFilter`
        """
        if default.version == self.UNVERSIONED:
            version = default.version
        else:
            version = self.version
        response = ServiceFilter()
        response.service_type = default.service_type
        response.service_name = self.service_name
        response.valid_versions = default.valid_versions
        response.visibility = default.visibility
        if self.visibility:
            response.visibility = self.visibility
        if self.region:
            response.region = self.region
        response.version = version
        return response

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

    def _get_valid_version(self):
        if self.valid_versions:
            if self.version:
                for valid in self.valid_versions:
                    # NOTE(thowe): should support fuzzy match e.g: v2.1==v2
                    if self.version == valid.module:
                        return valid
            return self.valid_versions[0]
        return ValidVersion('')

    def get_module(self):
        """Get the full module name associated with the service."""
        module = self.__class__.__module__.split('.')
        module = ".".join(module[:-1])
        module = module + "." + self._get_valid_version().module
        return module

    def get_service_module(self):
        """Get the module version of the service name.

        This would often be the same as the service type except in cases like
        object store where the service type is `object-store` and the module
        is `object_store`.
        """
        return self.__class__.__module__.split('.')[1]

    def get_version_path(self, version):
        """Get the desired version path.

        If the service does not have a version, use the suggested version.
        """
        if self.version is not None:
            return self.version
        valid = self._get_valid_version()
        if valid.path:
            return valid.path
        if version:
            return version
        return ''
