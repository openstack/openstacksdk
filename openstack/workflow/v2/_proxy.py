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

import typing as ty

from openstack import proxy
from openstack import resource
from openstack.workflow.v2 import cron_trigger as _cron_trigger
from openstack.workflow.v2 import execution as _execution
from openstack.workflow.v2 import workflow as _workflow


class Proxy(proxy.Proxy):
    _resource_registry = {
        "execution": _execution.Execution,
        "workflow": _workflow.Workflow,
    }

    def create_workflow(self, **attrs):
        """Create a new workflow from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.workflow.v2.workflow.Workflow`,
            comprised of the properties on the Workflow class.

        :returns: The results of workflow creation
        :rtype: :class:`~openstack.workflow.v2.workflow.Workflow`
        """
        return self._create(_workflow.Workflow, **attrs)

    def update_workflow(self, workflow, **attrs):
        """Update workflow from attributes

        :param workflow: The value can be either the name of a workflow or a
            :class:`~openstack.workflow.v2.workflow.Workflow`
            instance.
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`~openstack.workflow.v2.workflow.Workflow`,
            comprised of the properties on the Workflow class.

        :returns: The results of workflow update
        :rtype: :class:`~openstack.workflow.v2.workflow.Workflow`
        """
        return self._update(_workflow.Workflow, workflow, **attrs)

    def get_workflow(self, *attrs):
        """Get a workflow

        :param workflow: The value can be the name of a workflow or
            :class:`~openstack.workflow.v2.workflow.Workflow` instance.

        :returns: One :class:`~openstack.workflow.v2.workflow.Workflow`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            workflow matching the name could be found.
        """
        return self._get(_workflow.Workflow, *attrs)

    def workflows(self, **query):
        """Retrieve a generator of workflows

        :param kwargs query: Optional query parameters to be sent to
            restrict the workflows to be returned. Available parameters
            include:

            * limit: Requests at most the specified number of items be
              returned from the query.
            * marker: Specifies the ID of the last-seen workflow. Use the
              limit parameter to make an initial limited request and use
              the ID of the last-seen workflow from the response as the
              marker parameter value in a subsequent limited request.

        :returns: A generator of workflow instances.
        """
        return self._list(_workflow.Workflow, **query)

    def delete_workflow(self, value, ignore_missing=True):
        """Delete a workflow

        :param value: The value can be either the name of a workflow or a
            :class:`~openstack.workflow.v2.workflow.Workflow`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will
            be raised when the workflow does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent workflow.

        :returns: ``None``
        """
        return self._delete(
            _workflow.Workflow, value, ignore_missing=ignore_missing
        )

    def find_workflow(self, name_or_id, ignore_missing=True):
        """Find a single workflow

        :param name_or_id: The name or ID of an workflow.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.workflow.Extension` or
            None
        """
        return self._find(
            _workflow.Workflow, name_or_id, ignore_missing=ignore_missing
        )

    def create_execution(self, **attrs):
        """Create a new execution from attributes

        :param workflow_name: The name of target workflow to execute.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.workflow.v2.execution.Execution`,
            comprised of the properties on the Execution class.

        :returns: The results of execution creation
        :rtype: :class:`~openstack.workflow.v2.execution.Execution`
        """
        return self._create(_execution.Execution, **attrs)

    def get_execution(self, *attrs):
        """Get a execution

        :param workflow_name: The name of target workflow to execute.
        :param execution: The value can be either the ID of a execution or a
            :class:`~openstack.workflow.v2.execution.Execution` instance.

        :returns: One :class:`~openstack.workflow.v2.execution.Execution`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            execution matching the criteria could be found.
        """
        return self._get(_execution.Execution, *attrs)

    def executions(self, **query):
        """Retrieve a generator of executions

        :param kwargs query: Optional query parameters to be sent to
            restrict the executions to be returned. Available parameters
            include:

            * limit: Requests at most the specified number of items be
              returned from the query.
            * marker: Specifies the ID of the last-seen execution. Use the
              limit parameter to make an initial limited request and use
              the ID of the last-seen execution from the response as the
              marker parameter value in a subsequent limited request.

        :returns: A generator of execution instances.
        """
        return self._list(_execution.Execution, **query)

    def delete_execution(self, value, ignore_missing=True):
        """Delete an execution

        :param value: The value can be either the name of a execution or a
            :class:`~openstack.workflow.v2.execute.Execution`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the execution does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent execution.

        :returns: ``None``
        """
        return self._delete(
            _execution.Execution, value, ignore_missing=ignore_missing
        )

    def find_execution(self, name_or_id, ignore_missing=True):
        """Find a single execution

        :param name_or_id: The name or ID of an execution.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.execution.Execution` or
            None
        """
        return self._find(
            _execution.Execution, name_or_id, ignore_missing=ignore_missing
        )

    def create_cron_trigger(self, **attrs):
        """Create a new cron trigger from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.workflow.v2.cron_trigger.CronTrigger`,
            comprised of the properties on the CronTrigger class.

        :returns: The results of cron trigger creation
        :rtype: :class:`~openstack.workflow.v2.cron_trigger.CronTrigger`
        """
        return self._create(_cron_trigger.CronTrigger, **attrs)

    def get_cron_trigger(self, cron_trigger):
        """Get a cron trigger

        :param cron_trigger: The value can be the name of a cron_trigger or
            :class:`~openstack.workflow.v2.cron_trigger.CronTrigger` instance.

        :returns: One :class:`~openstack.workflow.v2.cron_trigger.CronTrigger`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            cron triggers matching the criteria could be found.
        """
        return self._get(_cron_trigger.CronTrigger, cron_trigger)

    def cron_triggers(self, *, all_projects=False, **query):
        """Retrieve a generator of cron triggers

        :param bool all_projects: When set to ``True``, list cron triggers from
            all projects. Admin-only by default.
        :param kwargs query: Optional query parameters to be sent to
            restrict the cron triggers to be returned. Available parameters
            include:

            * limit: Requests at most the specified number of items be
              returned from the query.
            * marker: Specifies the ID of the last-seen cron trigger. Use the
              limit parameter to make an initial limited request and use
              the ID of the last-seen cron trigger from the response as the
              marker parameter value in a subsequent limited request.

        :returns: A generator of CronTrigger instances.
        """
        if all_projects:
            query['all_projects'] = True
        return self._list(_cron_trigger.CronTrigger, **query)

    def delete_cron_trigger(self, value, ignore_missing=True):
        """Delete a cron trigger

        :param value: The value can be either the name of a cron trigger or a
            :class:`~openstack.workflow.v2.cron_trigger.CronTrigger`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the cron trigger does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent cron trigger.

        :returns: ``None``
        """
        return self._delete(
            _cron_trigger.CronTrigger, value, ignore_missing=ignore_missing
        )

    # TODO(stephenfin): Drop 'query' parameter or apply it consistently
    def find_cron_trigger(
        self,
        name_or_id,
        ignore_missing=True,
        *,
        all_projects=False,
        **query,
    ):
        """Find a single cron trigger

        :param name_or_id: The name or ID of a cron trigger.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist. When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param bool all_projects: When set to ``True``, search for cron
            triggers by name across all projects. Note that this will likely
            result in a higher chance of duplicates.
        :param kwargs query: Optional query parameters to be sent to limit
            the cron triggers being returned.

        :returns: One :class:`~openstack.compute.v2.cron_trigger.CronTrigger`
            or None
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _cron_trigger.CronTrigger,
            name_or_id,
            ignore_missing=ignore_missing,
            all_projects=all_projects,
            **query,
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
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

        :return: The updated resource.
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
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
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
