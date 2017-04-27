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

from openstack.metric.v1 import capabilities
from openstack import proxy2 as proxy


class Proxy(proxy.BaseProxy):

    def capabilities(self, **query):
        """Return a generator of capabilities

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of capability objects
        :rtype: :class:`~openstack.metric.v1.capabilities.Capabilities`
        """
        return self._list(capabilities.Capabilities, paginated=False, **query)
