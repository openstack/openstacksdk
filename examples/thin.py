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
Example Connection Command

Make sure you can authenticate before running this command.

For example:
    python -m examples.thin
"""

import sys

from examples import common
from examples import connection
from openstack.network.v2 import thin


def run_thin(opts):
    session = connection.make_connection(opts).session
    request = thin.Thin()
    for objay in request.list_networks(session):
        print(objay['id'])
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_thin))
