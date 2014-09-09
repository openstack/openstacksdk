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

"""
Authentication example

To authenticate you must have the environment variables set or use the
command line options.  This is a good example to start with because once
you know you can authenticate, you can perform other operations that
require authentication.  Refer to the example common.py for the environment
variables or command line options to use.

If you use the environment variables, authenticate with:

     python -m examples.authenticate

"""

import sys

from examples import common
from examples import transport
from openstack.auth import base
from openstack.auth.identity import authenticator


class TestAuthenticator(base.BaseAuthPlugin):
    def __init__(self, token, endpoint):
        super(TestAuthenticator, self).__init__()
        self.token = token
        self.endpoint = endpoint

    def get_token(self, transport, **kwargs):
        return self.token

    def get_endpoint(self, transport, service, **kwargs):
        return self.endpoint


def make_authenticate(opts):
    args = {
        'auth_plugin': opts.auth_plugin,
        'auth_url': opts.auth_url,
        'project_name': opts.project_name,
        'domain_name': opts.domain_name,
        'project_domain_name': opts.project_domain_name,
        'user_domain_name': opts.user_domain_name,
        'user_name': opts.user_name,
        'password': opts.password,
        'region_name': opts.region_name,
        'verify': opts.verify,
        'token': opts.token,
    }
    return authenticator.create(**args)


def run_authenticate(opts):
    auth = make_authenticate(opts)
    xport = transport.make_transport(opts)
    print(auth.authorize(xport))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_authenticate))
