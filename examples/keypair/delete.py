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
Keypair example

Destroy a keypair.

To run:
    python examples/keypair/delete.py
"""

import sys

from examples import common
from examples import connection


def delete(conn, name):
    kp = conn.compute.find_keypair(name)
    if kp is not None:
        print(str(kp))
        conn.delete(kp)


def run_keypair(opts):
    name = opts.data.pop('name', 'pare')
    conn = connection.make_connection(opts)
    return(delete(conn, name))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_keypair))
