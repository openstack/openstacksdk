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

import functools

from openstack.config import loader
from openstack import connection
from openstack import exceptions
from openstack.cloud import _utils

__all__ = ['OpenStackInventory']


class OpenStackInventory:

    # Put this here so the capability can be detected with hasattr on the class
    extra_config = None

    def __init__(
            self, config_files=None, refresh=False, private=False,
            config_key=None, config_defaults=None, cloud=None,
            use_direct_get=False):
        if config_files is None:
            config_files = []
        config = loader.OpenStackConfig(
            config_files=loader.CONFIG_FILES + config_files)
        self.extra_config = config.get_extra_config(
            config_key, config_defaults)

        if cloud is None:
            self.clouds = [
                connection.Connection(config=cloud_region)
                for cloud_region in config.get_all()
            ]
        else:
            self.clouds = [
                connection.Connection(config=config.get_one(cloud))
            ]

        if private:
            for cloud in self.clouds:
                cloud.private = True

        # Handle manual invalidation of entire persistent cache
        if refresh:
            for cloud in self.clouds:
                cloud._cache.invalidate()

    def list_hosts(self, expand=True, fail_on_cloud_config=True,
                   all_projects=False):
        hostvars = []

        for cloud in self.clouds:
            try:
                # Cycle on servers
                for server in cloud.list_servers(detailed=expand,
                                                 all_projects=all_projects):
                    hostvars.append(server)
            except exceptions.OpenStackCloudException:
                # Don't fail on one particular cloud as others may work
                if fail_on_cloud_config:
                    raise

        return hostvars

    def search_hosts(self, name_or_id=None, filters=None, expand=True):
        hosts = self.list_hosts(expand=expand)
        return _utils._filter_list(hosts, name_or_id, filters)

    def get_host(self, name_or_id, filters=None, expand=True):
        if expand:
            func = self.search_hosts
        else:
            func = functools.partial(self.search_hosts, expand=False)
        return _utils._get_entity(self, func, name_or_id, filters)
