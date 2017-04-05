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
from openstack.orchestration.v1 import resource as _resource
from openstack.orchestration.v1 import software_config as _sc
from openstack.orchestration.v1 import software_deployment as _sd
from openstack.orchestration.v1 import stack as _stack
from openstack.orchestration.v1 import stack_environment as _stack_environment
from openstack.orchestration.v1 import stack_files as _stack_files
from openstack.orchestration.v1 import stack_template as _stack_template
from openstack.orchestration.v1 import template as _template
from openstack import proxy2


class Proxy(proxy2.BaseProxy):

    def create_stack(self, preview=False, **attrs):
        """Create a new stack from attributes

        :param bool perview: When ``True``, returns
            an :class:`~openstack.orchestration.v1.stack.StackPreview` object,
            otherwise an :class:`~openstack.orchestration.v1.stack.Stack`
            object.
            *Default: ``False``*
        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.orchestration.v1.stack.Stack`,
                           comprised of the properties on the Stack class.

        :returns: The results of stack creation
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        """
        res_type = _stack.StackPreview if preview else _stack.Stack
        return self._create(res_type, **attrs)

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
        return self._find(_stack.Stack, name_or_id,
                          ignore_missing=ignore_missing)

    def stacks(self, **query):
        """Return a generator of stacks

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of stack objects
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        """
        return self._list(_stack.Stack, paginated=False, **query)

    def get_stack(self, stack):
        """Get a single stack

        :param stack: The value can be the ID of a stack or a
               :class:`~openstack.orchestration.v1.stack.Stack` instance.

        :returns: One :class:`~openstack.orchestration.v1.stack.Stack`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_stack.Stack, stack)

    def update_stack(self, stack, **attrs):
        """Update a stack

        :param stack: The value can be the ID of a stack or a
               :class:`~openstack.orchestration.v1.stack.Stack` instance.
        :param kwargs \*\*attrs: The attributes to update on the stack
                                 represented by ``value``.

        :returns: The updated stack
        :rtype: :class:`~openstack.orchestration.v1.stack.Stack`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._update(_stack.Stack, stack, **attrs)

    def delete_stack(self, stack, ignore_missing=True):
        """Delete a stack

        :param stack: The value can be either the ID of a stack or a
                      :class:`~openstack.orchestration.v1.stack.Stack`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the stack does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent stack.

        :returns: ``None``
        """
        self._delete(_stack.Stack, stack, ignore_missing=ignore_missing)

    def check_stack(self, stack):
        """Check a stack's status

        Since this is an asynchronous action, the only way to check the result
        is to track the stack's status.

        :param stack: The value can be either the ID of a stack or an instance
                      of :class:`~openstack.orchestration.v1.stack.Stack`.
        :returns: ``None``
        """
        if isinstance(stack, _stack.Stack):
            stk_obj = stack
        else:
            stk_obj = _stack.Stack.existing(id=stack)

        stk_obj.check(self._session)

    def get_stack_template(self, stack):
        """Get template used by a stack

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`

        :returns: One object of
            :class:`~openstack.orchestration.v1.stack_template.StackTemplate`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)

        return self._get(_stack_template.StackTemplate, requires_id=False,
                         stack_name=obj.name, stack_id=obj.id)

    def get_stack_environment(self, stack):
        """Get environment used by a stack

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`

        :returns: One object of
                  :class:`~openstack.orchestration.v1.stack_environment.\
                  StackEnvironment`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
                 resource can be found.
        """
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)

        return self._get(_stack_environment.StackEnvironment,
                         requires_id=False, stack_name=obj.name,
                         stack_id=obj.id)

    def get_stack_files(self, stack):
        """Get files used by a stack

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`

        :returns: A dictionary containing the names and contents of all files
                  used by the stack.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when the stack cannot be found.
        """
        if isinstance(stack, _stack.Stack):
            stk = stack
        else:
            stk = self._find(_stack.Stack, stack, ignore_missing=False)

        obj = _stack_files.StackFiles(stack_name=stk.name, stack_id=stk.id)
        return obj.get(self._session)

    def resources(self, stack, **query):
        """Return a generator of resources

        :param stack: This can be a stack object, or the name of a stack
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
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)

        return self._list(_resource.Resource, paginated=False,
                          stack_name=obj.name, stack_id=obj.id, **query)

    def create_software_config(self, **attrs):
        """Create a new software config from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`,
            comprised of the properties on the SoftwareConfig class.

        :returns: The results of software config creation
        :rtype:
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        """
        return self._create(_sc.SoftwareConfig, **attrs)

    def software_configs(self, **query):
        """Returns a generator of software configs

        :param dict query: Optional query parameters to be sent to limit the
                           software configs returned.
        :returns: A generator of software config objects.
        :rtype: :class:`~openstack.orchestration.v1.software_config.\
                SoftwareConfig`
        """
        return self._list(_sc.SoftwareConfig, paginated=True, **query)

    def get_software_config(self, software_config):
        """Get details about a specific software config.

        :param software_config: The value can be the ID of a software config
            or a instace of
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`,

        :returns: An object of type
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        """
        return self._get(_sc.SoftwareConfig, software_config)

    def delete_software_config(self, software_config, ignore_missing=True):
        """Delete a software config

        :param software_config: The value can be either the ID of a software
            config or an instance of
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the software config does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent software config.
        :returns: ``None``
        """
        self._delete(_sc.SoftwareConfig, software_config,
                     ignore_missing=ignore_missing)

    def create_software_deployment(self, **attrs):
        """Create a new software deployment from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`,
            comprised of the properties on the SoftwareDeployment class.

        :returns: The results of software deployment creation
        :rtype:
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        """
        return self._create(_sd.SoftwareDeployment, **attrs)

    def software_deployments(self, **query):
        """Returns a generator of software deployments

        :param dict query: Optional query parameters to be sent to limit the
                           software deployments returned.
        :returns: A generator of software deployment objects.
        :rtype: :class:`~openstack.orchestration.v1.software_deployment.\
                SoftwareDeployment`
        """
        return self._list(_sd.SoftwareDeployment, paginated=False, **query)

    def get_software_deployment(self, software_deployment):
        """Get details about a specific software deployment resource

        :param software_deployment: The value can be the ID of a software
            deployment or an instace of
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`,

        :returns: An object of type
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        """
        return self._get(_sd.SoftwareDeployment, software_deployment)

    def delete_software_deployment(self, software_deployment,
                                   ignore_missing=True):
        """Delete a software deployment

        :param software_deployment: The value can be either the ID of a
            software deployment or an instance of
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the software deployment does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent software deployment.
        :returns: ``None``
        """
        self._delete(_sd.SoftwareDeployment, software_deployment,
                     ignore_missing=ignore_missing)

    def update_software_deployment(self, software_deployment, **attrs):
        """Update a software deployment

        :param server: Either the ID of a software deployment or an instance of
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        :param dict attrs: The attributes to update on the software deployment
                           represented by ``software_deployment``.

        :returns: The updated software deployment
        :rtype: :class:`~openstack.orchestration.v1.software_deployment.\
                SoftwareDeployment`
        """
        return self._update(_sd.SoftwareDeployment, software_deployment,
                            **attrs)

    def validate_template(self, template, environment=None, template_url=None,
                          ignore_errors=None):
        """Validates a template.

        :param template: The stack template on which the validation is
                         performed.
        :param environment: A JSON environment for the stack, if provided.
        :param template_url: A URI to the location containing the stack
                             template for validation. This parameter is only
                             required if the ``template`` parameter is None.
                             This parameter is ignored if ``template`` is
                             specified.
        :param ignore_errors: A string containing comma separated error codes
                              to ignore. Currently the only valid error code
                              is '99001'.
        :returns: The result of template validation.
        :raises: :class:`~openstack.exceptions.InvalidRequest` if neither
                 `template` not `template_url` is provided.
        :raises: :class:`~openstack.exceptions.HttpException` if the template
                 fails the validation.
        """
        if template is None and template_url is None:
            raise exceptions.InvalidRequest(
                "'template_url' must be specified when template is None")

        tmpl = _template.Template.new()
        return tmpl.validate(self._session, template, environment=environment,
                             template_url=template_url,
                             ignore_errors=ignore_errors)
