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

from openstack.orchestration.v1 import stack
from openstack import proxy
from openstack import resource


class Proxy(proxy.BaseProxy):

    def create_stack(self, **attrs):
        """Create a new stack from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.orchestration.v1.stack.Stack`,
                           comprised of the properties on the Stack class.

        :returns: The results of stack creation
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        """
        return self._create(stack.Stack, **attrs)

    def find_stack(self, name_or_id):
        """Find a single stack

        :param name_or_id: The name or ID of a stack.
        :returns: One :class:`~openstack.orchestration.v1.stack.Stack` or None
        """
        return stack.Stack.find(self.session, name_or_id)

    def stacks(self):
        """Return a generator of stacks

        :returns: A generator of stack objects
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        """
        return self._list(stack.Stack, paginated=False)

    def get_stack(self, value):
        """Get a single stack

        :param value: The value can be the ID of a stack or a
               :class:`~openstack.orchestration.v1.stack.Stack` instance.

        :returns: One :class:`~openstack.orchestration.v1.stack.Stack`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(stack.Stack, value)

    def delete_stack(self, value, ignore_missing=True):
        """Delete a stack

        :param value: The value can be either the ID of a stack or a
                      :class:`~openstack.orchestration.v1.stack.Stack`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the stack does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(stack.Stack, value, ignore_missing=ignore_missing)

    def wait_for_stack(self, value, status='CREATE_COMPLETE',
                       failures=['CREATE_FAILED'], interval=2, wait=120):
        return resource.wait_for_status(self.session, value, status,
                                        failures, interval, wait)
