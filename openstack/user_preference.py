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


import six

from openstack.compute import compute_service
from openstack.database import database_service
from openstack import exceptions
from openstack.identity import identity_service
from openstack.image import image_service
from openstack.network import network_service
from openstack.object_store import object_store_service
from openstack.orchestration import orchestration_service
from openstack.telemetry import telemetry_service

USER_AGENT = 'OSPythonSDK'


class UserPreference(object):

    ALL = "*"

    def __init__(self):
        """User preference for each service.

        NOTE(thowe): We should probably do something more clever here rather
        than brute force create all the services.  Maybe use entry points
        or something, but I'd like to leave that work for another commit.
        """
        self._preferences = {}
        self._services = {}
        serv = compute_service.ComputeService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = database_service.DatabaseService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = identity_service.IdentityService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = image_service.ImageService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = network_service.NetworkService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = object_store_service.ObjectStoreService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = orchestration_service.OrchestrationService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        serv = telemetry_service.TelemetryService()
        serv.set_visibility(None)
        self._services[serv.service_type] = serv
        self.service_names = sorted(self._services.keys())

    def __repr__(self):
        return repr(self._preferences)

    def get_preference(self, service):
        """Get a service preference."""
        return self._preferences.get(service, None)

    def get_services(self):
        services = []
        for name, service in six.iteritems(self._services):
            services.append(service)
        return services

    def _get_service(self, service):
        """Get a valid service filter."""
        serv = self._services.get(service, None)
        if serv is not None:
            self._preferences[service] = serv
            return serv
        msg = ("Service %s not in list of valid services: %s" %
               (service, self.service_names))
        raise exceptions.SDKException(msg)

    def set_name(self, service, name):
        if service == self.ALL:
            services = self.service_names
        else:
            services = [service]
        for service in services:
            self._get_service(service).service_name = name

    def set_region(self, service, region):
        if service == self.ALL:
            services = self.service_names
        else:
            services = [service]
        for service in services:
            self._get_service(service).region = region

    def set_version(self, service, version):
        if service == self.ALL:
            services = self.service_names
        else:
            services = [service]
        for service in services:
            self._get_service(service).version = version

    def set_visibility(self, service, visibility):
        if service == self.ALL:
            services = self.service_names
        else:
            services = [service]
        for service in services:
            self._get_service(service).set_visibility(visibility)
