#!/usr/bin/env python3
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Utility to get Keystone token
"""
from ansible.module_utils.basic import AnsibleModule

import openstack


def get_cloud(cloud):
    if isinstance(cloud, dict):
        config = openstack.config.loader.OpenStackConfig().get_one(**cloud)
        return openstack.connection.Connection(config=config)
    else:
        return openstack.connect(cloud=cloud)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cloud=dict(required=True, type='raw', no_log=True),
        )
    )
    cloud = get_cloud(module.params.get('cloud'))
    module.exit_json(
        changed=True,
        auth_token=cloud.auth_token
    )


if __name__ == '__main__':
    main()
