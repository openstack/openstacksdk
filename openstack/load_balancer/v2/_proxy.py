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

from openstack.load_balancer.v2 import load_balancer as _lb
from openstack import proxy2


class Proxy(proxy2.BaseProxy):

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.load_balancer.v2.
                           load_balancer.LoadBalancer`,
                           comprised of the properties on the
                           LoadBalancer class.

        :returns: The results of load balancer creation
        :rtype: :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._create(_lb.LoadBalancer, **attrs)

    def get_load_balancer(self, *attrs):
        """Get a load balancer

        :param load_balancer: The value can be the name of a load balancer
             or :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
             instance.

        :returns: One
             :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._get(_lb.LoadBalancer, *attrs)

    def load_balancers(self, **query):
        """Retrieve a generator of load balancers

        :returns: A generator of load balancer instances
        """
        return self._list(_lb.LoadBalancer, paginated=True, **query)

    def delete_load_balancer(self, load_balancer, ignore_missing=True):
        """Delete a load balancer

        :param load_balancer: The load_balancer can be either the name or a
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent load balancer.

        :returns: ``None``
        """
        return self._delete(_lb.LoadBalancer, load_balancer,
                            ignore_missing=ignore_missing)

    def find_load_balancer(self, name_or_id, ignore_missing=True):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent load balancer.

        :returns: ``None``
        """
        return self._find(_lb.LoadBalancer, name_or_id,
                          ignore_missing=ignore_missing)
