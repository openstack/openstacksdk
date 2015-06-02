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

_defaults = dict(
    api_timeout=None,
    auth_type='password',
    baremetal_api_version='1',
    compute_api_version='2',
    database_api_version='1.0',
    endpoint_type='public',
    floating_ip_source='neutron',
    identity_api_version='2',
    image_api_use_tasks=False,
    image_api_version='1',
    network_api_version='2',
    object_api_version='1',
    secgroup_source='neutron',
    volume_api_version='1',
    disable_vendor_agent={},
    # SSL Related args
    verify=True,
    cacert=None,
    cert=None,
    key=None,
)


def get_defaults():
    return _defaults.copy()
