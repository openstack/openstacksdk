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

from openstack import exceptions
from openstack.orchestration.v1 import resource as stack_resource
from openstack.orchestration.v1 import stack
from openstack import proxy


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

    def find_stack(self, name_or_id, ignore_missing=True):
        """Find a single stack

        :param name_or_id: The name or ID of a stack.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.orchestration.v1.stack.Stack` or None
        """
        return self._find(stack.Stack, name_or_id,
                          ignore_missing=ignore_missing)

    def stacks(self, **query):
        """Return a generator of stacks

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of stack objects
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        """
        return self._list(stack.Stack, paginated=False, **query)

    def get_stack(self, value):
        """Get a single stack

        :param value: The value can be the ID of a stack or a
               :class:`~openstack.orchestration.v1.stack.Stack` instance.

        :returns: One :class:`~openstack.orchestration.v1.stack.Stack`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(stack.Stack, value)

    def update_stack(self, value, **attrs):
        """Update a stack

        :param value: The value can be the ID of a stack or a
               :class:`~openstack.orchestration.v1.stack.Stack` instance.
        :param kwargs \*\*attrs: The attributes to update on the stack
                                 represented by ``value``.

        :returns: The updated stack
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._update(stack.Stack, value, **attrs)

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

    def resources(self, value, **query):
        """Return a generator of resources

        :param value: This can be a stack object, or the name of a stack
                      for which the resources are to be listed.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of resource objects if the stack exists and
                  there are resources in it. If the stack cannot be found,
                  an exception is thrown.
        :rtype: A generator of
            :class:`~openstack.orchestration.v1.resource.Resource`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when the stack cannot be found.
        """
        # first try treat the value as a stack object or an ID
        try:
            stk = stack.Stack.from_id(value)
        except ValueError:
            raise exceptions.ResourceNotFound(
                "No stack found for %(v)s" % {'v': value})

        # if stack object doesn't contain a valid name, it means the object
        # was created on the fly so we need to retrieve its name
        if not stk.name:
            stk = self.find_stack(value)
            if stk is None:
                raise exceptions.ResourceNotFound(
                    "No stack found for %(v)s" % {'v': value})

        path_args = {
            'stack_name': stk.name,
            'stack_id': stk.id,
        }
        return self._list(stack_resource.Resource, paginated=False,
                          path_args=path_args, **query)
