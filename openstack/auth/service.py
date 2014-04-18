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


class ServiceIdentifier(object):
    """The basic structure of an authentication plugin."""

    PUBLIC = 'public'
    INTERNAL = 'internal'
    ADMIN = 'admin'
    VISIBILITY = [PUBLIC, INTERNAL, ADMIN]

    def __init__(self, service_type, visibility=PUBLIC, region=None):
        """" Create a service identifier.

        :param string service_type: The desired type of service.
        :param string visibility: The exposure of the endpoint. Should be
                                  `public` (default), `internal` or `admin`.
        :param string region: The desired region (optional).
        """
        self.service_type = service_type
        self.visibility = visibility
        self.region = region
