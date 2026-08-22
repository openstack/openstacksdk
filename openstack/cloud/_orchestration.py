# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack.orchestration.util import event_utils
from openstack.orchestration.v1 import stack as _stack


class OrchestrationCloudMixin(openstackcloud._OpenStackCloudMixin):
    def get_template_contents(
        self,
        template_file: str | None = None,
        template_url: str | None = None,
        template_object: str | None = None,
        files: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        return self.orchestration.get_template_contents(
            template_file=template_file,
            template_url=template_url,
            template_object=template_object,
            files=files,
        )

    def create_stack(
        self,
        name: str,
        tags: list[str] | None = None,
        template_file: str | None = None,
        template_url: str | None = None,
        template_object: str | None = None,
        files: dict[str, Any] | None = None,
        rollback: bool = True,
        wait: bool = False,
        timeout: int | float = 3600,
        environment_files: list[str] | None = None,
        **parameters: Any,
    ) -> _stack.Stack | None:
        """Create a stack.

        :param name: Name of the stack.
        :param tags: List of tag(s) of the stack. (optional)
        :param template_file: Path to the template.
        :param template_url: URL of template.
        :param template_object: URL to retrieve template object.
        :param files: dict of additional file content to include.
        :param rollback: Enable rollback on create failure.
        :param wait: Whether to wait for the delete to finish.
        :param timeout: Stack create timeout in seconds.
        :param environment_files: Paths to environment files to apply.

        Other arguments will be passed as stack parameters which will take
        precedence over any parameters specified in the environments.

        Only one of template_file, template_url, template_object should be
        specified.

        :returns: a dict containing the stack description
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        params: dict[str, Any] = {
            'tags': tags,
            'is_rollback_disabled': not rollback,
            'timeout_mins': timeout // 60,
            'parameters': parameters,
        }
        params.update(
            self.orchestration.read_env_and_templates(
                template_file=template_file,
                template_url=template_url,
                template_object=template_object,
                files=files,
                environment_files=environment_files,
            )
        )
        self.orchestration.create_stack(name=name, **params)
        if wait:
            event_utils.poll_for_events(self, stack_name=name, action='CREATE')
        return self.get_stack(name)

    def update_stack(
        self,
        name_or_id: str,
        template_file: str | None = None,
        template_url: str | None = None,
        template_object: str | None = None,
        files: dict[str, Any] | None = None,
        rollback: bool = True,
        tags: list[str] | None = None,
        wait: bool = False,
        timeout: int | float = 3600,
        environment_files: list[str] | None = None,
        **parameters: Any,
    ) -> _stack.Stack | None:
        """Update a stack.

        :param name_or_id: Name or ID of the stack to update.
        :param template_file: Path to the template.
        :param template_url: URL of template.
        :param template_object: URL to retrieve template object.
        :param files: dict of additional file content to include.
        :param rollback: Enable rollback on update failure.
        :param wait: Whether to wait for the delete to finish.
        :param timeout: Stack update timeout in seconds.
        :param environment_files: Paths to environment files to apply.

        Other arguments will be passed as stack parameters which will take
        precedence over any parameters specified in the environments.

        Only one of template_file, template_url, template_object should be
        specified.

        :returns: a dict containing the stack description
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API calls
        """
        params: dict[str, Any] = {
            'tags': tags,
            'is_rollback_disabled': not rollback,
            'timeout_mins': timeout // 60,
            'parameters': parameters,
        }
        params.update(
            self.orchestration.read_env_and_templates(
                template_file=template_file,
                template_url=template_url,
                template_object=template_object,
                files=files,
                environment_files=environment_files,
            )
        )
        if wait:
            # find the last event to use as the marker
            events = event_utils.get_events(
                self, name_or_id, event_args={'sort_dir': 'desc', 'limit': 1}
            )
            marker = events[0].id if events else None

        self.orchestration.update_stack(name_or_id, **params)

        if wait:
            event_utils.poll_for_events(
                self, name_or_id, action='UPDATE', marker=marker
            )
        return self.get_stack(name_or_id)

    def delete_stack(self, name_or_id: str, wait: bool = False) -> bool:
        """Delete a stack

        :param name_or_id: Stack name or ID.
        :param wait: Whether to wait for the delete to finish

        :returns: True if delete succeeded, False if the stack was not found.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        stack = self.get_stack(name_or_id, resolve_outputs=False)
        if stack is None:
            self.log.debug("Stack %s not found for deleting", name_or_id)
            return False

        if wait:
            # find the last event to use as the marker
            events = event_utils.get_events(
                self, name_or_id, event_args={'sort_dir': 'desc', 'limit': 1}
            )
            marker = events[0].id if events else None

        self.orchestration.delete_stack(stack)

        if wait:
            try:
                event_utils.poll_for_events(
                    self, stack_name=name_or_id, action='DELETE', marker=marker
                )
            except exceptions.HttpException:
                pass
            stack = self.get_stack(name_or_id, resolve_outputs=False)
            if stack and stack['stack_status'] == 'DELETE_FAILED':
                raise exceptions.SDKException(
                    "Failed to delete stack {id}: {reason}".format(
                        id=name_or_id, reason=stack['stack_status_reason']
                    )
                )

        return True

    def search_stacks(
        self,
        name_or_id: str | None = None,
        filters: dict[str, Any] | str | None = None,
    ) -> list[_stack.Stack]:
        """Search stacks.

        :param name_or_id: Name or ID of the desired stack.
        :param filters: a dict containing additional filters to use. e.g.
                {'stack_status': 'CREATE_COMPLETE'}

        :returns: a list of ``openstack.orchestration.v1.stack.Stack``
            containing the stack description.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        stacks = self.list_stacks()
        return _utils._filter_list(stacks, name_or_id, filters)

    def list_stacks(self, **query: Any) -> list[_stack.Stack]:
        """List all stacks.

        :param query: Query parameters to limit stacks.

        :returns: a list of :class:`openstack.orchestration.v1.stack.Stack`
            objects containing the stack description.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.orchestration.stacks(**query))

    def get_stack(
        self,
        name_or_id: str,
        filters: dict[str, Any] | str | None = None,
        resolve_outputs: bool = True,
    ) -> _stack.Stack | None:
        """Get exactly one stack.

        :param name_or_id: Name or ID of the desired stack.
        :param filters: a dict containing additional filters to use. e.g.
                {'stack_status': 'CREATE_COMPLETE'}
        :param resolve_outputs: If True, then outputs for this
                stack will be resolved

        :returns: a :class:`openstack.orchestration.v1.stack.Stack`
            containing the stack description
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call or if multiple matches are
            found.
        """

        # stack names are mandatory and enforced unique in the project
        # so a StackGet can always be used for name or ID.
        try:
            stack = self.orchestration.find_stack(
                name_or_id,
                ignore_missing=False,
                resolve_outputs=resolve_outputs,
            )
        except exceptions.NotFoundException:
            return None
        if stack.status == 'DELETE_COMPLETE':
            return None
        results = _utils._filter_list([stack], name_or_id, filters)
        return results[0] if results else None
