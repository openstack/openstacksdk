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
:class:`~openstack.profile.Profile` is deprecated. Code should use
:class:`~openstack.config.cloud_region.CloudRegion` instead.
"""

import copy

from openstack import _log
from openstack.config import cloud_region
from openstack.config import defaults as config_defaults
from openstack.baremetal import baremetal_service
from openstack.block_storage import block_storage_service
from openstack.clustering import clustering_service
from openstack.compute import compute_service
from openstack.database import database_service
from openstack import exceptions
from openstack.identity import identity_service
from openstack.image import image_service
from openstack.key_manager import key_manager_service
from openstack.load_balancer import load_balancer_service as lb_service
from openstack.message import message_service
from openstack.network import network_service
from openstack.object_store import object_store_service
from openstack.orchestration import orchestration_service
from openstack import utils
from openstack.workflow import workflow_service

_logger = _log.setup_logging('openstack')


def _get_config_from_profile(profile, authenticator, **kwargs):
    # TODO(shade) Remove this once we've shifted python-openstackclient
    # to not use the profile interface.

    region_name = None
    for service in profile.get_services():
        if service.region:
            region_name = service.region
        service_type = service.service_type
        if service.interface:
            key = cloud_region._make_key('interface', service_type)
            kwargs[key] = service.interface
        if service.version:
            version = service.version
            if version.startswith('v'):
                version = version[1:]
            key = cloud_region._make_key('api_version', service_type)
            kwargs[key] = version

    config_kwargs = config_defaults.get_defaults()
    config_kwargs.update(kwargs)
    config = cloud_region.CloudRegion(
        region_name=region_name, config=config_kwargs)
    config._auth = authenticator
    return config


class Profile(object):

    ALL = "*"
    """Wildcard service identifier representing all services."""

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def __init__(self, plugins=None):
        """User preference for each service.

        :param plugins: List of entry point namespaces to load.

        Create a new :class:`~openstack.profile.Profile`
        object with no preferences defined, but knowledge of the services.
        Services are identified by their service type, e.g.: 'identity',
        'compute', etc.
        """
        self._services = {}

        self._add_service(baremetal_service.BaremetalService(version="v1"))
        self._add_service(
            block_storage_service.BlockStorageService(version="v2"))
        self._add_service(clustering_service.ClusteringService(version="v1"))
        self._add_service(compute_service.ComputeService(version="v2"))
        self._add_service(database_service.DatabaseService(version="v1"))
        self._add_service(identity_service.IdentityService(version="v3"))
        self._add_service(image_service.ImageService(version="v2"))
        self._add_service(key_manager_service.KeyManagerService(version="v1"))
        self._add_service(lb_service.LoadBalancerService(version="v2"))
        self._add_service(message_service.MessageService(version="v1"))
        self._add_service(network_service.NetworkService(version="v2"))
        self._add_service(
            object_store_service.ObjectStoreService(version="v1"))
        self._add_service(
            orchestration_service.OrchestrationService(version="v1"))
        self._add_service(workflow_service.WorkflowService(version="v2"))

        self.service_keys = sorted(self._services.keys())

    def __repr__(self):
        return repr(self._services)

    def _add_service(self, serv):
        serv.interface = None
        self._services[serv.service_type] = serv

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def get_filter(self, service):
        """Get a service preference.

        :param str service: Desired service type.
        """
        return copy.copy(self._get_filter(service))

    def _get_filter(self, service):
        """Get a service preference.

        :param str service: Desired service type.
        """
        serv = self._services.get(service, None)
        if serv is not None:
            return serv
        msg = ("Service %s not in list of valid services: %s" %
               (service, self.service_keys))
        raise exceptions.SDKException(msg)

    def _get_services(self, service):
        return self.service_keys if service == self.ALL else [service]

    def _setter(self, service, attr, value):
        for service in self._get_services(service):
            setattr(self._get_filter(service), attr, value)

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def get_services(self):
        """Get a list of all the known services."""
        services = []
        for name, service in self._services.items():
            services.append(service)
        return services

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def set_name(self, service, name):
        """Set the desired name for the specified service.

        :param str service: Service type.
        :param str name: Desired service name.
        """
        self._setter(service, "service_name", name)

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def set_region(self, service, region):
        """Set the desired region for the specified service.

        :param str service: Service type.
        :param str region: Desired service region.
        """
        self._setter(service, "region", region)

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def set_version(self, service, version):
        """Set the desired version for the specified service.

        :param str service: Service type.
        :param str version: Desired service version.
        """
        self._get_filter(service).version = version

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def set_api_version(self, service, api_version):
        """Set the desired API micro-version for the specified service.

        :param str service: Service type.
        :param str api_version: Desired service API micro-version.
        """
        self._setter(service, "api_version", api_version)

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="Use openstack.config instead")
    def set_interface(self, service, interface):
        """Set the desired interface for the specified service.

        :param str service: Service type.
        :param str interface: Desired service interface.
        """
        self._setter(service, "interface", interface)
