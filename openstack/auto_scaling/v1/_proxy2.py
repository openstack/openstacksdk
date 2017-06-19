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

from openstack import proxy2
from openstack.auto_scaling.v1 import policy as _policy
from openstack.exceptions import InvalidRequest


class Proxy(proxy2.BaseProxy):
    def policies(self, **query):
        """Retrieve a generator of policies
        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``name``: policy name
            * ``type``: policy type
            * ``scaling_group_id``: scaling group id the policy applied to
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of policy
                  (:class:`~openstack.auto_scaling.v2.policy.Policy`) instances
        """
        return self._list(_policy.Policy, paginated=True, **query)

    def create_policy(self, **attrs):
        """Create a new policy from attributes
        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.auto_scaling.v2.policy.Policy`,
                           comprised of the properties on the Policy class.
        :returns: The results of policy creation
        :rtype: :class:`~openstack.auto_scaling.v2.policy.Policy`
        """
        return self._create(_policy.Policy, prepend_key=False, **attrs)

    def get_policy(self, policy):
        """Get a policy
        :param policy: The value can be the ID of a policy
             or a :class:`~openstack.auto_scaling.v2.policy.Policy` instance.
        :returns: Policy instance
        :rtype: :class:`~openstack.auto_scaling.v2.policy.Policy`
        """
        return self._get(_policy.Policy, policy)

    def delete_policy(self, policy, ignore_missing=True):
        """Delete a policy

        :param policy: The value can be the ID of a policy
             or a :class:`~openstack.auto_scaling.v2.policy.Policy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the policy does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent policy.

        :returns: Policy been deleted
        :rtype: :class:`~openstack.auto_scaling.v2.policy.Policy`
        """
        return self._delete(_policy.Policy, policy, ignore_missing=ignore_missing)

    def find_policy(self, name_or_id, ignore_missing=True):
        """Find a single policy

        :param name_or_id: The name or ID of a policy
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the policy does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent policy.

        :returns: ``None``
        """
        return self._find(_policy.Policy, name_or_id,
                          ignore_missing=ignore_missing,
                          name=name_or_id)
