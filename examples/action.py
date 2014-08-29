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
Example Action Command

Invoke an action method on a resource.

A session will be provided to the action if needed. The action itself
must be identified by the 'action' key. Arguments to the action may be
provided through an 'action_args' dictionary.

For examples:
    python -m examples.action openstack/telemetry/v2/alarm.py \
           --data '{"alarm_id": "33109eea-24dd-45ff-93f7-82292d1dd38c",
                    "action": "change_state",
                    "action_args": {"next_state": "insufficient data"}'

    python -m examples.action openstack/compute/v2/server.py \
           --data '{"id": "a1369557-748f-429c-bd3e-fc385aacaec7",
                    "action": "reboot",
                    "action_args": {"reboot_type": "SOFT"}}'
"""

import inspect
import sys

from examples import common
from examples import session


def filter_args(method, params):
    expected_args = inspect.getargspec(method).args
    accepted_args = ([a for a in expected_args if a != 'self'])
    filtered_args = {desired: params[desired] for desired in accepted_args}
    return filtered_args


def invoke_method(target, method_name, params):
    action = getattr(target, method_name)
    filtered_args = filter_args(action, params)
    reply = action(**filtered_args)
    return reply


def run_action(options):
    sess = session.make_session(options)
    cls = common.find_resource_cls(options)
    data = common.get_data_option(options)

    action = data.pop('action')
    if 'action_args' in data:
        args = data.pop('action_args')
    else:
        args = {}
    args.update(session=sess)

    obj = cls.new(**data)
    reply = invoke_method(obj, action, args)
    print(str(reply))
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_action))
