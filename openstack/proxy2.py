# Copyright 2018 Red Hat, Inc.
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

from openstack import proxy
from openstack import utils


class Proxy(proxy.Proxy):

    @utils.deprecated(deprecated_in="0.10.0", removed_in="1.0",
                      details="openstack.proxy2 is now openstack.proxy")
    def __init__(self, *args, **kwargs):
        super(Proxy, self).__init__(*args, **kwargs)
