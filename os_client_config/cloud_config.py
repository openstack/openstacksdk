# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
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

import warnings


class CloudConfig(object):
    def __init__(self, name, region, config,
                 force_ipv4=False, auth_plugin=None):
        self.name = name
        self.region = region
        self.config = config
        self._force_ipv4 = force_ipv4
        self._auth = auth_plugin

    def __getattr__(self, key):
        """Return arbitrary attributes."""

        if key.startswith('os_'):
            key = key[3:]

        if key in [attr.replace('-', '_') for attr in self.config]:
            return self.config[key]
        else:
            return None

    def __iter__(self):
        return self.config.__iter__()

    def __eq__(self, other):
        return (self.name == other.name and self.region == other.region
                and self.config == other.config)

    def __ne__(self, other):
        return not self == other

    def get_requests_verify_args(self):
        """Return the verify and cert values for the requests library."""
        if self.config['verify'] and self.config['cacert']:
            verify = self.config['cacert']
        else:
            verify = self.config['verify']
            if self.config['cacert']:
                warnings.warn(
                    "You are specifying a cacert for the cloud {0} but "
                    "also to ignore the host verification. The host SSL cert "
                    "will not be verified.".format(self.name))

        cert = self.config.get('cert', None)
        if cert:
            if self.config['key']:
                cert = (cert, self.config['key'])
        return (verify, cert)

    def get_services(self):
        """Return a list of service types we know something about."""
        services = []
        for key, val in self.config.items():
            if (key.endswith('api_version')
                    or key.endswith('service_type')
                    or key.endswith('service_name')):
                services.append("_".join(key.split('_')[:-2]))
        return list(set(services))

    def get_auth_args(self):
        return self.config['auth']

    def get_interface(self, service_type=None):
        interface = self.config.get('interface')
        if not service_type:
            return interface
        key = '{service_type}_interface'.format(service_type=service_type)
        return self.config.get(key, interface)

    def get_region_name(self, service_type=None):
        if not service_type:
            return self.region
        key = '{service_type}_region_name'.format(service_type=service_type)
        return self.config.get(key, self.region)

    def get_api_version(self, service_type):
        key = '{service_type}_api_version'.format(service_type=service_type)
        return self.config.get(key, None)

    def get_service_type(self, service_type):
        key = '{service_type}_service_type'.format(service_type=service_type)
        return self.config.get(key, service_type)

    def get_service_name(self, service_type):
        key = '{service_type}_service_name'.format(service_type=service_type)
        return self.config.get(key, None)

    def get_endpoint(self, service_type):
        key = '{service_type}_endpoint'.format(service_type=service_type)
        return self.config.get(key, None)

    @property
    def prefer_ipv6(self):
        return not self._force_ipv4

    @property
    def force_ipv4(self):
        return self._force_ipv4

    def get_auth(self):
        """Return a keystoneauth plugin from the auth credentials."""
        return self._auth
