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
Example Create Command

For example:
    python -m examples.create openstack/network/v2_0/network.py \
           --data '{"name": "foo"}'
"""

import sys

from examples import common
from examples import session


def run_create(opts):
    sess = session.make_session(opts)
    cls = common.find_resource_cls(opts)
    obj = cls.new(**common.get_data_option(opts))
    obj.create(sess)
    print(str(obj))
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_create))
