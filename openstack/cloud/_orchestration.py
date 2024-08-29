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

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack.orchestration.util import event_utils


class OrchestrationCloudMixin(openstackcloud._OpenStackCloudMixin):
    def get_template_contents(
        self,
        template_file=None,
        template_url=None,
        template_object=None,
        files=None,
    ):
        return self.orchestration.get_template_contents(
            template_file=template_file,
            template_url=template_url,
            template_object=template_object,
            files=files,
        )

    def create_stack(
        self,
        name,
        tags=None,
        template_file=None,
        template_url=None,
        template_object=None,
        files=None,
        rollback=True,
        wait=False,
        timeout=3600,
        environment_files=None,
        **parameters,
    ):
        """Create a stack.

        :param string name: Name of the stack.
        :param tags: List of tag(s) of the stack. (optional)
        :param string template_file: Path to the template.
        :param string template_url: URL of template.
        :param string template_object: URL to retrieve template object.
        :param dict files: dict of additional file content to include.
        :param boolean rollback: Enable rollback on create failure.
        :param boolean wait: Whether to wait for the delete to finish.
        :param int timeout: Stack create timeout in seconds.
        :param environment_files: Paths to environment files to apply.

        Other arguments will be passed as stack parameters which will take
        precedence over any parameters specified in the environments.

        Only one of template_file, template_url, template_object should be
        specified.

        :returns: a dict containing the stack description
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        params = dict(
            tags=tags,
            is_rollback_disabled=not rollback,
            timeout_mins=timeout // 60,
            parameters=parameters,
        )
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
        name_or_id,
        template_file=None,
        template_url=None,
        template_object=None,
        files=None,
        rollback=True,
        tags=None,
        wait=False,
        timeout=3600,
        environment_files=None,
        **parameters,
    ):
        """Update a stack.

        :param string name_or_id: Name or ID of the stack to update.
        :param string template_file: Path to the template.
        :param string template_url: URL of template.
        :param string template_object: URL to retrieve template object.
        :param dict files: dict of additional file content to include.
        :param boolean rollback: Enable rollback on update failure.
        :param boolean wait: Whether to wait for the delete to finish.
        :param int timeout: Stack update timeout in seconds.
        :param environment_files: Paths to environment files to apply.

        Other arguments will be passed as stack parameters which will take
        precedence over any parameters specified in the environments.

        Only one of template_file, template_url, template_object should be
        specified.

        :returns: a dict containing the stack description
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API calls
        """
        params = dict(
            tags=tags,
            is_rollback_disabled=not rollback,
            timeout_mins=timeout // 60,
            parameters=parameters,
        )
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

        # Not to cause update of ID field pass stack as dict
        self.orchestration.update_stack(stack={'id': name_or_id}, **params)

        if wait:
            event_utils.poll_for_events(
                self, name_or_id, action='UPDATE', marker=marker
            )
        return self.get_stack(name_or_id)

    def delete_stack(self, name_or_id, wait=False):
        """Delete a stack

        :param string name_or_id: Stack name or ID.
        :param boolean wait: Whether to wait for the delete to finish

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

    def search_stacks(self, name_or_id=None, filters=None):
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

    def list_stacks(self, **query):
        """List all stacks.

        :param dict query: Query parameters to limit stacks.

        :returns: a list of :class:`openstack.orchestration.v1.stack.Stack`
            objects containing the stack description.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.orchestration.stacks(**query))

    def get_stack(self, name_or_id, filters=None, resolve_outputs=True):
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

        def _search_one_stack(name_or_id=None, filters=None):
            # stack names are mandatory and enforced unique in the project
            # so a StackGet can always be used for name or ID.
            try:
                stack = self.orchestration.find_stack(
                    name_or_id,
                    ignore_missing=False,
                    resolve_outputs=resolve_outputs,
                )
                if stack.status == 'DELETE_COMPLETE':
                    return []
            except exceptions.NotFoundException:
                return []
            return _utils._filter_list([stack], name_or_id, filters)

        return _utils._get_entity(self, _search_one_stack, name_or_id, filters)
