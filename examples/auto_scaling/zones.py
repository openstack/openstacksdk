# Copyright 2017 HuaWei Tld
# Copyright 2017 OpenStack.org
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import sys

from examples.connect import create_connection_from_config
from openstack import utils
from openstack.dns.v2.zone import Zone

# utils.enable_logging(debug=False, stream=sys.stdout)

# You must initialize logging, otherwise you'll not see debug output.
from openstack import resource2 as resource

class Resource1(resource.Resource):
    name = resource.Body("name")

class Resource2(resource.Resource):
    name = resource.Body("name")
    resource1 = resource.Body("resource1", type=Resource1, default={})

r1 = Resource1.new(name="r1")
r2 = Resource2.new(name="r2")
print r2

# get_zone(connection, 'ff8080825ca865e8015ca99563af004a')
# create_zone(connection)
# delete_zone(connection)
# get_nameservers(connection)
# add_router_to_zone(connection)
# remove_router_from_zone(connection)
