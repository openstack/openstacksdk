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

from examples import authenticate
from examples import common
from examples import transport
from openstack.auth import service_filter
from openstack import session


def make_session(opts):
    region = opts.os_region
    preference = service_filter.ServiceFilter(region=region)
    xport = transport.make_transport(opts)
    auth = authenticate.make_authenticate(opts)
    return session.Session(xport, auth, preference=preference)


def run_session(opts):
    argument = opts.argument
    if argument is None:
        raise Exception("A path argument must be specified")
    sess = make_session(opts)
    filtration = service_filter.ServiceFilter(service_type='Identity')
    print("Session: %s" % sess)
    print(sess.get(argument, service=filtration).text)
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_session))
