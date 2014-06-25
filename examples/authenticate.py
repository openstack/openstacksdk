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

import sys

from examples import common
from examples import transport
from openstack.auth import base
from openstack.auth.identity import v2
from openstack.auth.identity import v3


class TestAuthenticator(base.BaseAuthenticator):
    def __init__(self, token, endpoint):
        super(TestAuthenticator, self).__init__()
        self.token = token
        self.endpoint = endpoint

    def get_token(self, transport, **kwargs):
        return self.token

    def get_endpoint(self, transport, service, **kwargs):
        return self.endpoint


def make_authenticate(opts):
    """Create authenticator of some sort."""
    token = opts.os_token
    username = opts.os_username
    password = opts.os_password
    auth_url = opts.os_auth_url
    project_name = opts.os_project_name
    version = opts.os_identity_api_version
    if version is None:
        version = '3'
    else:
        version = version.lower().replace('v', '')
    version = version.split('.')[0]
    if version == '3':
        if not token:
            args = {'username': username, 'password': password}
            if project_name:
                args['project_name'] = project_name
            return v3.Password(auth_url, **args)
        else:
            return v3.Token(auth_url, token=token)
    elif version == '2':
        if not token:
            args = {}
            if project_name:
                args['tenant_name'] = project_name
            return v2.Password(auth_url, username, password, **args)
        else:
            return v2.Token(auth_url, token)
    raise Exception("No support for version: %s" % version)


def run_authenticate(opts):
    auth = make_authenticate(opts)
    xport = transport.make_transport(opts)
    print(auth.authorize(xport))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_authenticate))
