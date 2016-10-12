# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Normalizer(object):
    '''Mix-in class to provide the normalization functions.

    This is in a separate class just for on-disk source code organization
    reasons.
    '''

    def _normalize_servers(self, servers):
        # Here instead of _utils because we need access to region and cloud
        # name from the cloud object
        ret = []
        for server in servers:
            ret.append(self._normalize_server(server))
        return ret

    def _normalize_server(self, server):
        server.pop('links', None)
        server['flavor'].pop('links', None)
        # OpenStack can return image as a string when you've booted
        # from volume
        if str(server['image']) != server['image']:
            server['image'].pop('links', None)

        server['region'] = self.region_name
        server['cloud'] = self.name
        server['location'] = self.current_location

        az = server.get('OS-EXT-AZ:availability_zone', None)
        if az:
            server['az'] = az

        # Ensure volumes is always in the server dict, even if empty
        server['volumes'] = []

        return server
