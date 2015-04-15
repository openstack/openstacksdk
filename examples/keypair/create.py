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

Create a working keypair.

To run:
    python examples/keypair/create.py
"""

import os
import sys

from examples import common
from examples import connection


def create(conn, name):

    kp = conn.compute.find_keypair(name)
    if kp is None:
        dirname = os.path.expanduser("~/.ssh")
        try:
            os.mkdir(dirname, 0o700)
        except OSError:
            pass
        filename = os.path.join(dirname, name)
        filenamepub = filename + '.pub'
        args = {'name': name}
        pubkey = None
        try:
            with open(filenamepub, 'r') as f:
                pubkey = f.read()
            args['public_key'] = pubkey
        except IOError:
            pass
        kp = conn.compute.create_keypair(**args)
        if pubkey is None:
            with open(filename, 'w') as f:
                f.write("%s" % kp.private_key)
            with open(filenamepub, 'w') as f:
                f.write("%s" % kp.public_key)
            os.chmod(filename, 0o640)
            os.chmod(filenamepub, 0o644)
    print(str(kp))
    return kp


def run_keypair(opts):
    name = opts.data.pop('name', 'pare')
    conn = connection.make_connection(opts)
    return(create(conn, name))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_keypair))
