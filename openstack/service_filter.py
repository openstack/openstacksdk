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
The :class:`~openstack.service_filter.ServiceFilter` is the base class
for service identifiers and user service preferences.  Each
:class:`~openstack.resource.Resource` has a service identifier to
associate the resource with a service.  An example of a service identifier
would be ``openstack.compute.compute_service.ComputeService``.
The preferences are stored in the
:class:`~openstack.profile.Profile` object.
The service preference and the service identifier are joined to create a
filter to match a service.

Examples
--------

The :class:`~openstack.service_filter.ServiceFilter` class can be built
with a service type, interface, region, name, and version.

Create a service filter
~~~~~~~~~~~~~~~~~~~~~~~

Create a compute service and service preference. Join the services
and match::

    from openstack import service_filter
    from openstack.compute import compute_service
    default = compute_service.ComputeService()
    preference = service_filter.ServiceFilter('compute', version='v2')
    result = preference.join(default)
    matches = (result.match_service_type('compute') and
               result.match_service_name('Hal9000') and
               result.match_region('DiscoveryOne') and
               result.match_interface('public'))
    print(str(result))
    print("matches=" + str(matches))

The resulting output from the code::

    service_type=compute,interface=public,version=v2
    matches=True
"""


class ValidVersion(object):

    def __init__(self, module, path=None):
        """" Valid service version.

        :param string module: Module associated with version.
        :param string path: URL path version.
        """
        self.module = module
        self.path = path or module


class ServiceFilter(dict):
    UNVERSIONED = ''
    PUBLIC = 'public'
    INTERNAL = 'internal'
    ADMIN = 'admin'
    valid_versions = []

    def __init__(self, service_type, interface=PUBLIC, region=None,
                 service_name=None, version=None):
        """Create a service identifier.

        :param string service_type: The desired type of service.
        :param string interface: The exposure of the endpoint. Should be
                                  `public` (default), `internal` or `admin`.
        :param string region: The desired region (optional).
        :param string service_name: Name of the service
        :param string version: Version of service to use.
        """
        self['service_type'] = service_type.lower()
        self['interface'] = interface
        self['region_name'] = region
        self['service_name'] = service_name
        self['version'] = version

    @property
    def service_type(self):
        return self['service_type']

    @property
    def interface(self):
        return self['interface']

    @interface.setter
    def interface(self, value):
        self['interface'] = value

    @property
    def region(self):
        return self['region_name']

    @region.setter
    def region(self, value):
        self['region_name'] = value

    @property
    def service_name(self):
        return self['service_name']

    @service_name.setter
    def service_name(self, value):
        self['service_name'] = value

    @property
    def version(self):
        return self['version']

    @version.setter
    def version(self, value):
        self['version'] = value

    @property
    def path(self):
        return self['path']

    @path.setter
    def path(self, value):
        self['path'] = value

    def get_path(self, version=None):
        if not self.version:
            self.version = version
        return self.get('path', self._get_valid_version().path)

    def get_filter(self):
        filter = dict(self)
        del filter['version']
        return filter

    def _get_valid_version(self):
        if self.valid_versions:
            if self.version:
                for valid in self.valid_versions:
                    # NOTE(thowe): should support fuzzy match e.g: v2.1==v2
                    if self.version.startswith(valid.module):
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
