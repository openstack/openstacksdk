# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

import os_client_config

import shade
from shade import _utils


class OpenStackInventory(object):

    def __init__(
            self, config_files=[], refresh=False):
        config = os_client_config.config.OpenStackConfig(
            config_files=os_client_config.config.CONFIG_FILES + config_files)

        self.clouds = [
            shade.OpenStackCloud(
                cloud=f.name,
                cache_interval=config.get_cache_max_age(),
                cache_class=config.get_cache_class(),
                cache_arguments=config.get_cache_arguments(),
                **f.config)
            for f in config.get_all_clouds()
            ]

        # Handle manual invalidation of entire persistent cache
        if refresh:
            for cloud in self.clouds:
                cloud._cache.invalidate()

    def list_hosts(self):
        hostvars = []

        for cloud in self.clouds:

            # Cycle on servers
            for server in cloud.list_servers():

                meta = cloud.get_openstack_vars(server)
                hostvars.append(meta)

        return hostvars

    def search_hosts(self, name_or_id=None, filters=None):
        hosts = self.list_hosts()
        return _utils._filter_list(hosts, name_or_id, filters)

    def get_host(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_hosts, name_or_id, filters)
