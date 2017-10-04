# Copyright (c) 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import openstack.config

ran = []
for cloud in openstack.config.OpenStackConfig().get_all_clouds():
    if cloud.name in ran:
        continue
    ran.append(cloud.name)
    c = cloud.get_session_client('compute')
    try:
        raw_endpoint = c.get_endpoint()
        have_current = False
        endpoint = raw_endpoint.rsplit('/', 2)[0]
        print(endpoint)
        r = c.get(endpoint).json()
    except Exception:
        print("Error with %s" % cloud.name)
        continue
    for version in r['versions']:
        if version['status'] == 'CURRENT':
            have_current = True
            print(
                "\tVersion ID: {id} updated {updated}".format(
                    id=version.get('id'),
                    updated=version.get('updated')))
            print(
                "\tVersion Max: {max}".format(max=version.get('version')))
            print(
                "\tVersion Min: {min}".format(min=version.get('min_version')))
    if not have_current:
        for version in r['versions']:
            if version['status'] == 'SUPPORTED':
                have_current = True
                print(
                    "\tVersion ID: {id} updated {updated}".format(
                        id=version.get('id'),
                        updated=version.get('updated')))
                print(
                    "\tVersion Max: {max}".format(max=version.get('version')))
                print(
                    "\tVersion Min: {min}".format(
                        min=version.get('min_version')))
