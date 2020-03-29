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

import pprint
import sys
from urllib import parse as urlparse

import openstack.config


def print_versions(r):
    if 'version' in r:
        for version in r['version']:
            print_version(version)
    if 'values' in r:
        for version in r['values']:
            print_version(version)
    if isinstance(r, list):
        for version in r:
            print_version(version)


def print_version(version):
    if version['status'] in ('CURRENT', 'stable'):
        print(
            "\tVersion ID: {id} updated {updated}".format(
                id=version.get('id'),
                updated=version.get('updated')))


verbose = '-v' in sys.argv
ran = []
for cloud in openstack.config.OpenStackConfig().get_all_clouds():
    if cloud.name in ran:
        continue
    ran.append(cloud.name)
    # We don't actually need a compute client - but we'll be getting full urls
    # anyway. Without this SSL cert info becomes wrong.
    c = cloud.get_session_client('compute')
    endpoint = cloud.config['auth']['auth_url']
    try:
        print(endpoint)
        r = c.get(endpoint).json()
        if verbose:
            pprint.pprint(r)
    except Exception as e:
        print("Error with {cloud}: {e}".format(cloud=cloud.name, e=str(e)))
        continue
    if 'version' in r:
        print_version(r['version'])
        url = urlparse.urlparse(endpoint)
        parts = url.path.split(':')
        if len(parts) == 2:
            path, port = parts
        else:
            path = url.path
            port = None
        stripped = path.rsplit('/', 2)[0]
        if port:
            stripped = '{stripped}:{port}'.format(stripped=stripped, port=port)
        endpoint = urlparse.urlunsplit(
            (url.scheme, url.netloc, stripped, url.params, url.query))
        print("  also {endpoint}".format(endpoint=endpoint))
        try:
            r = c.get(endpoint).json()
            if verbose:
                pprint.pprint(r)
        except Exception:
            print("\tUnauthorized")
            continue
        if 'version' in r:
            print_version(r)
        elif 'versions' in r:
            print_versions(r['versions'])
        else:
            print("\n\nUNKNOWN\n\n{r}".format(r=r))
    else:
        print_versions(r['versions'])
