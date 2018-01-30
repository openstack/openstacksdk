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

from openstack import proxy
from openstack.workflow.v2 import execution as _execution
from openstack.workflow.v2 import workflow as _workflow


class Proxy(proxy.Proxy):

    def create_workflow(self, **attrs):
        """Create a new workflow from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.workflow.v2.workflow.Workflow`,
                           comprised of the properties on the Workflow class.

        :returns: The results of workflow creation
        :rtype: :class:`~openstack.workflow.v2.workflow.Workflow`
        """
        return self._create(_workflow.Workflow, **attrs)

    def get_workflow(self, *attrs):
        """Get a workflow

        :param workflow: The value can be the name of a workflow or
             :class:`~openstack.workflow.v2.workflow.Workflow` instance.

        :returns: One :class:`~openstack.workflow.v2.workflow.Workflow`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
             workflow matching the name could be found.
        """
        return self._get(_workflow.Workflow, *attrs)

    def workflows(self, **query):
        """Retrieve a generator of workflows

        :param kwargs \*\*query: Optional query parameters to be sent to
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
        return self._list(_workflow.Workflow, paginated=True, **query)

    def delete_workflow(self, value, ignore_missing=True):
        """Delete a workflow

        :param value: The value can be either the name of a workflow or a
                      :class:`~openstack.workflow.v2.workflow.Workflow`
                      instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will
            be raised when the workflow does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent workflow.

        :returns: ``None``
        """
        return self._delete(_workflow.Workflow, value,
                            ignore_missing=ignore_missing)

    def find_workflow(self, name_or_id, ignore_missing=True):
        """Find a single workflow

        :param name_or_id: The name or ID of an workflow.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.workflow.Extension` or
            None
        """
        return self._find(_workflow.Workflow, name_or_id,
                          ignore_missing=ignore_missing)

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
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            execution matching the criteria could be found.
        """
        return self._get(_execution.Execution, *attrs)

    def executions(self, **query):
        """Retrieve a generator of executions

        :param kwargs \*\*query: Optional query parameters to be sent to
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
        return self._list(_execution.Execution, paginated=True, **query)

    def delete_execution(self, value, ignore_missing=True):
        """Delete an execution

        :param value: The value can be either the name of a execution or a
                      :class:`~openstack.workflow.v2.execute.Execution`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the execution does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent execution.

        :returns: ``None``
        """
        return self._delete(_execution.Execution, value,
                            ignore_missing=ignore_missing)

    def find_execution(self, name_or_id, ignore_missing=True):
        """Find a single execution

        :param name_or_id: The name or ID of an execution.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.execution.Execution` or
            None
        """
        return self._find(_execution.Execution, name_or_id,
                          ignore_missing=ignore_missing)
