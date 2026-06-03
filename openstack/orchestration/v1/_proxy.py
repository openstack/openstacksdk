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

from collections.abc import Callable, Generator, Sequence
import queue
from typing import Any, ClassVar, Literal, overload

from openstack import exceptions
from openstack.orchestration.util import template_utils
from openstack.orchestration.v1 import resource as _resource
from openstack.orchestration.v1 import software_config as _sc
from openstack.orchestration.v1 import software_deployment as _sd
from openstack.orchestration.v1 import stack as _stack
from openstack.orchestration.v1 import stack_environment as _stack_environment
from openstack.orchestration.v1 import stack_event as _stack_event
from openstack.orchestration.v1 import stack_files as _stack_files
from openstack.orchestration.v1 import stack_template as _stack_template
from openstack.orchestration.v1 import template as _template
from openstack import proxy
from openstack.proxy import CleanupDependency
from openstack import resource


# TODO(rladntjr4): Some of these methods support lookup by ID, while others
# support lookup by ID or name. We should choose one and use it consistently.
class Proxy(proxy.Proxy):
    api_version: ClassVar[Literal['1']] = '1'

    _resource_registry = {
        "resource": _resource.Resource,
        "software_config": _sc.SoftwareConfig,
        "software_deployment": _sd.SoftwareDeployment,
        "stack": _stack.Stack,
        "stack_environment": _stack_environment.StackEnvironment,
        "stack_files": _stack_files.StackFiles,
        "stack_template": _stack_template.StackTemplate,
    }

    def _extract_name_consume_url_parts(
        self, url_parts: list[str]
    ) -> list[str]:
        if (
            len(url_parts) == 3
            and url_parts[0] == 'software_deployments'
            and url_parts[1] == 'metadata'
        ):
            # Another nice example of totally different URL naming scheme,
            # which we need to repair /software_deployment/metadata/server_id -
            # just replace server_id with metadata to keep further logic
            return ['software_deployment', 'metadata']
        if (
            url_parts[0] == 'stacks'
            and len(url_parts) > 2
            and url_parts[2] not in ['preview', 'resources']
        ):
            # orchestrate introduce having stack name and id part of the URL
            # (/stacks/name/id/everything_else), so if on third position we
            # have not a known part - discard it, not to brake further logic
            del url_parts[2]
        return super()._extract_name_consume_url_parts(url_parts)

    def read_env_and_templates(
        self,
        template_file: str | None = None,
        template_url: str | None = None,
        template_object: str | None = None,
        files: dict[str, Any] | None = None,
        environment_files: list[str] | None = None,
    ) -> dict[str, Any]:
        """Read templates and environment content and prepares
        corresponding stack attributes

        :param template_file: Path to the template.
        :param template_url: URL of template.
        :param template_object: URL to retrieve template object.
        :param files: Dict of additional file content to include.
        :param environment_files: Paths to environment files to apply.

        :returns: Attributes dict to be set on the
            :class:`~openstack.orchestration.v1.stack.Stack`
        """
        stack_attrs: dict[str, Any] = {}
        envfiles: dict[str, Any] = {}
        tpl_files: dict[str, Any] | None = None
        if environment_files:
            (
                envfiles,
                env,
            ) = template_utils.process_multiple_environments_and_files(
                env_paths=environment_files
            )
            stack_attrs['environment'] = env
        if template_file or template_url or template_object:
            tpl_files, template = template_utils.get_template_contents(
                template_file=template_file,
                template_url=template_url,
                template_object=template_object,
                files=files,
            )
            stack_attrs['template'] = template
            if tpl_files or envfiles:
                stack_attrs['files'] = dict(
                    list(tpl_files.items()) + list(envfiles.items())
                )
        return stack_attrs

    def create_stack(
        self, preview: bool = False, **attrs: Any
    ) -> _stack.Stack:
        """Create a new stack from attributes

        :param preview: When ``True``, a preview endpoint will be used to
            verify the template
            *Default: ``False``*
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.orchestration.v1.stack.Stack`,
            comprised of the properties on the Stack class.

        :returns: The results of stack creation
        """

        base_path = None if not preview else '/stacks/preview'
        return self._create(_stack.Stack, base_path=base_path, **attrs)

    @overload
    def find_stack(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        resolve_outputs: bool = True,
    ) -> _stack.Stack: ...

    @overload
    def find_stack(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        resolve_outputs: bool = True,
    ) -> _stack.Stack | None: ...

    def find_stack(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        resolve_outputs: bool = True,
    ) -> _stack.Stack | None:
        """Find a single stack

        :param name_or_id: The name or ID of a stack.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.orchestration.v1.stack.Stack` or None
        """
        return self._find(
            _stack.Stack,
            name_or_id,
            ignore_missing=ignore_missing,
            resolve_outputs=resolve_outputs,
        )

    def stacks(self, **query: Any) -> Generator[_stack.Stack, None, None]:
        """Return a generator of stacks

        :param query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of stack objects
        """
        return self._list(_stack.Stack, **query)

    def get_stack(
        self,
        stack: str | _stack.Stack,
        resolve_outputs: bool = True,
    ) -> _stack.Stack:
        """Get a single stack

        :param stack: The value can be the ID of a stack or a
            :class:`~openstack.orchestration.v1.stack.Stack` instance.
        :param resolve_outputs: Whether stack should contain outputs resolved.

        :returns: One :class:`~openstack.orchestration.v1.stack.Stack`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_stack.Stack, stack, resolve_outputs=resolve_outputs)

    def update_stack(
        self, stack: str | _stack.Stack, *, preview: bool = False, **attrs: Any
    ) -> _stack.Stack:
        """Update a stack

        :param stack: The value can be the ID of a stack or a
            :class:`~openstack.orchestration.v1.stack.Stack` instance.
        :param attrs: The attributes to update on the stack
            represented by ``value``.

        :returns: The updated stack
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        res = self._get_resource(_stack.Stack, stack, **attrs)
        return res.commit(self, preview)

    def delete_stack(
        self, stack: str | _stack.Stack, ignore_missing: bool = True
    ) -> None:
        """Delete a stack

        :param stack: The value can be either the ID of a stack or a
            :class:`~openstack.orchestration.v1.stack.Stack`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the stack does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent stack.

        :returns: ``None``
        """
        self._delete(_stack.Stack, stack, ignore_missing=ignore_missing)

    def check_stack(self, stack: str | _stack.Stack) -> None:
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

        stk_obj.check(self)

    def abandon_stack(self, stack: str | _stack.Stack) -> dict[str, Any]:
        """Abandon a stack's without deleting it's resources

        :param stack: The value can be either the ID of a stack or an instance
            of :class:`~openstack.orchestration.v1.stack.Stack`.
        :returns: ``None``
        """
        res = self._get_resource(_stack.Stack, stack)
        return res.abandon(self)

    def export_stack(self, stack: str | _stack.Stack) -> dict[str, Any]:
        """Get the stack data in JSON format

        :param stack: The value can be the ID or a name or
            an instance of :class:`~openstack.orchestration.v1.stack.Stack`
        :returns: A dictionary containing the stack data.
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)
        return obj.export(self)

    def suspend_stack(self, stack: str | _stack.Stack) -> None:
        """Suspend a stack status

        :param stack: The value can be either the ID of a stack or an instance
            of :class:`~openstack.orchestration.v1.stack.Stack`.
        :returns: ``None``
        """
        res = self._get_resource(_stack.Stack, stack)
        res.suspend(self)

    def resume_stack(self, stack: str | _stack.Stack) -> None:
        """Resume a stack status

        :param stack: The value can be either the ID of a stack or an instance
            of :class:`~openstack.orchestration.v1.stack.Stack`.
        :returns: ``None``
        """
        res = self._get_resource(_stack.Stack, stack)
        res.resume(self)

    def get_stack_template(
        self, stack: str | _stack.Stack
    ) -> _stack_template.StackTemplate:
        """Get template used by a stack

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`

        :returns: One object of
            :class:`~openstack.orchestration.v1.stack_template.StackTemplate`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)

        return self._get(
            _stack_template.StackTemplate,
            requires_id=False,
            stack_name=obj.name,
            stack_id=obj.id,
        )

    def get_stack_environment(
        self, stack: str | _stack.Stack
    ) -> _stack_environment.StackEnvironment:
        """Get environment used by a stack

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`

        :returns: One object of
            :class:`~openstack.orchestration.v1.stack_environment.StackEnvironment`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)

        return self._get(
            _stack_environment.StackEnvironment,
            requires_id=False,
            stack_name=obj.name,
            stack_id=obj.id,
        )

    def get_stack_files(self, stack: str | _stack.Stack) -> dict[str, Any]:
        """Get files used by a stack

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`

        :returns: A dictionary containing the names and contents of all files
            used by the stack.
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when the stack cannot be found.
        """
        if isinstance(stack, _stack.Stack):
            stk = stack
        else:
            stk = self._find(_stack.Stack, stack, ignore_missing=False)

        obj = _stack_files.StackFiles(stack_name=stk.name, stack_id=stk.id)
        return obj.fetch(self)

    def resources(
        self,
        stack: str | _stack.Stack,
        **query: Any,
    ) -> Generator[_resource.Resource, None, None]:
        """Return a generator of resources

        :param stack: This can be a stack object, or the name of a stack
            for which the resources are to be listed.
        :param query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of resource objects if the stack exists and
            there are resources in it. If the stack cannot be found,
            an exception is thrown.
            :class:`~openstack.orchestration.v1.resource.Resource`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when the stack cannot be found.
        """
        # first try treat the value as a stack object or an ID
        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._find(_stack.Stack, stack, ignore_missing=False)

        return self._list(
            _resource.Resource, stack_name=obj.name, stack_id=obj.id, **query
        )

    def create_software_config(self, **attrs: Any) -> _sc.SoftwareConfig:
        """Create a new software config from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`,
            comprised of the properties on the SoftwareConfig class.

        :returns: The results of software config creation
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        """
        return self._create(_sc.SoftwareConfig, **attrs)

    def software_configs(
        self,
        **query: Any,
    ) -> Generator[_sc.SoftwareConfig, None, None]:
        """Returns a generator of software configs

        :param query: Optional query parameters to be sent to limit the
            software configs returned.
        :returns: A generator of software config objects.
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        """
        return self._list(_sc.SoftwareConfig, **query)

    def get_software_config(
        self, software_config: str | _sc.SoftwareConfig
    ) -> _sc.SoftwareConfig:
        """Get details about a specific software config.

        :param software_config: The value can be the ID of a software config
            or a instace of
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`,

        :returns: An object of type
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        """
        return self._get(_sc.SoftwareConfig, software_config)

    def delete_software_config(
        self,
        software_config: str | _sc.SoftwareConfig,
        ignore_missing: bool = True,
    ) -> None:
        """Delete a software config

        :param software_config: The value can be either the ID of a software
            config or an instance of
            :class:`~openstack.orchestration.v1.software_config.SoftwareConfig`
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the software config does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent software config.
        :returns: ``None``
        """
        self._delete(
            _sc.SoftwareConfig, software_config, ignore_missing=ignore_missing
        )

    def create_software_deployment(
        self, **attrs: Any
    ) -> _sd.SoftwareDeployment:
        """Create a new software deployment from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`,
            comprised of the properties on the SoftwareDeployment class.

        :returns: The results of software deployment creation
        """
        return self._create(_sd.SoftwareDeployment, **attrs)

    def software_deployments(
        self,
        **query: Any,
    ) -> Generator[_sd.SoftwareDeployment, None, None]:
        """Returns a generator of software deployments

        :param query: Optional query parameters to be sent to limit the
            software deployments returned.
        :returns: A generator of software deployment objects.
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        """
        return self._list(_sd.SoftwareDeployment, **query)

    def get_software_deployment(
        self, software_deployment: str | _sd.SoftwareDeployment
    ) -> _sd.SoftwareDeployment:
        """Get details about a specific software deployment resource

        :param software_deployment: The value can be the ID of a software
            deployment or an instace of
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`,

        :returns: An object of type
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        """
        return self._get(_sd.SoftwareDeployment, software_deployment)

    def delete_software_deployment(
        self,
        software_deployment: str | _sd.SoftwareDeployment,
        ignore_missing: bool = True,
    ) -> None:
        """Delete a software deployment

        :param software_deployment: The value can be either the ID of a
            software deployment or an instance of
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the software deployment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent software deployment.
        :returns: ``None``
        """
        self._delete(
            _sd.SoftwareDeployment,
            software_deployment,
            ignore_missing=ignore_missing,
        )

    def update_software_deployment(
        self, software_deployment: str | _sd.SoftwareDeployment, **attrs: Any
    ) -> _sd.SoftwareDeployment:
        """Update a software deployment

        :param server: Either the ID of a software deployment or an instance of
            :class:`~openstack.orchestration.v1.software_deployment.SoftwareDeployment`
        :param attrs: The attributes to update on the software deployment
            represented by ``software_deployment``.

        :returns: The updated software deployment
        """
        return self._update(
            _sd.SoftwareDeployment, software_deployment, **attrs
        )

    def validate_template(
        self,
        template: dict[str, Any] | None,
        environment: dict[str, Any] | None = None,
        template_url: str | None = None,
        ignore_errors: str | None = None,
    ) -> _template.Template:
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
                "'template_url' must be specified when template is None"
            )

        tmpl = _template.Template.new()
        return tmpl.validate(
            self,
            template,
            environment=environment,
            template_url=template_url,
            ignore_errors=ignore_errors,
        )

    def get_template_contents(
        self,
        template_file: str | None = None,
        template_url: str | None = None,
        template_object: str | None = None,
        files: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        try:
            return template_utils.get_template_contents(
                template_file=template_file,
                template_url=template_url,
                template_object=template_object,
                files=files,
            )
        except Exception as e:
            raise exceptions.SDKException(
                f"Error in processing template files: {e!s}"
            )

    # ========== Stack events ==========

    def stack_events(
        self,
        stack: str | _stack.Stack,
        resource_name: str | None = None,
        **attr: Any,
    ) -> Generator[_stack_event.StackEvent, None, None]:
        """Get a stack events

        :param stack: The value can be the ID of a stack or an instance of
            :class:`~openstack.orchestration.v1.stack.Stack`
        :param resource_name: The name of resource. If the resource_name is not
            None, the base_path changes.

        :returns: A generator of stack_events objects
        """

        if isinstance(stack, _stack.Stack):
            obj = stack
        else:
            obj = self._get(_stack.Stack, stack)

        if resource_name:
            return self._list(
                _stack_event.StackEvent,
                stack_name=obj.name,
                stack_id=obj.id,
                resource_name=resource_name,
                base_path=(
                    '/stacks/%(stack_name)s/%(stack_id)s/resources/'
                    '%(resource_name)s/events'
                ),
                **attr,
            )

        return self._list(
            _stack_event.StackEvent,
            stack_name=obj.name,
            stack_id=obj.id,
            **attr,
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: Callable[[int], None] | None = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :returns: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int | float | None = 2,
        wait: int | None = 120,
        callback: Callable[[int], None] | None = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)

    def _get_cleanup_dependencies(self) -> dict[str, CleanupDependency]:
        return {
            'orchestration': {
                'before': ['compute', 'network', 'identity'],
                'after': [],
            }
        }

    def _service_cleanup(
        self,
        dry_run: bool = True,
        client_status_queue: queue.Queue[resource.Resource] | None = None,
        identified_resources: dict[str, resource.Resource] | None = None,
        filters: dict[str, Any] | None = None,
        resource_evaluation_fn: Callable[
            [
                resource.Resource,
                dict[str, Any] | None,
                dict[str, resource.Resource] | None,
            ],
            bool,
        ]
        | None = None,
        skip_resources: Sequence[str] | None = None,
    ) -> None:
        if self.should_skip_resource_cleanup("stack", skip_resources):
            return

        stacks = []
        for obj in self.stacks():
            need_delete = self._service_cleanup_del_res(
                self.delete_stack,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn,
            )
            if not dry_run and need_delete:
                stacks.append(obj)

        for stack in stacks:
            self.wait_for_delete(stack)
