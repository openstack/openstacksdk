#!/usr/bin/env python3
#
# Copyright 2014 Rackspace Australia
# Copyright 2018 Red Hat, Inc
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
Utility to revoke Keystone token
"""

import logging
import traceback

from ansible.module_utils.basic import AnsibleModule
import keystoneauth1.exceptions
import requests
import requests.exceptions

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
            revoke_token=dict(required=True, type='str', no_log=True)
        )
    )

    p = module.params
    cloud = get_cloud(p.get('cloud'))
    try:
        cloud.identity.delete(
            '/auth/tokens',
            headers={
                'X-Subject-Token': p.get('revoke_token')
            }
        )
    except (keystoneauth1.exceptions.http.HttpError,
            requests.exceptions.RequestException):
        s = "Error performing token revoke"
        logging.exception(s)
        s += "\n" + traceback.format_exc()
        module.fail_json(
            changed=False,
            msg=s,
            cloud=cloud.name,
            region_name=cloud.config.region_name)
    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
