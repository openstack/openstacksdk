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

from os_client_config.config import OpenStackConfig  # noqa


def simple_client(service_key, cloud=None, region_name=None):
    """Simple wrapper function. It has almost no features.

    This will get you a raw requests Session Adapter that is mounted
    on the given service from the keystone service catalog. If you leave
    off cloud and region_name, it will assume that you've got env vars
    set, but if you give them, it'll use clouds.yaml as you'd expect.

    This function is deliberately simple. It has no flexibility. If you
    want flexibility, you can make a cloud config object and call
    get_session_client on it. This function is to make it easy to poke
    at OpenStack REST APIs with a properly configured keystone session.
    """
    return OpenStackConfig().get_one_cloud(
        cloud=cloud, region_name=region_name).get_session_client('compute')
