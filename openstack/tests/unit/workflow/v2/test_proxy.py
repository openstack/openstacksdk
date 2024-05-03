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

from openstack.tests.unit import test_proxy_base
from openstack.workflow.v2 import _proxy
from openstack.workflow.v2 import cron_trigger
from openstack.workflow.v2 import execution
from openstack.workflow.v2 import workflow


class TestWorkflowProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_workflows(self):
        self.verify_list(self.proxy.workflows, workflow.Workflow)

    def test_executions(self):
        self.verify_list(self.proxy.executions, execution.Execution)

    def test_workflow_get(self):
        self.verify_get(self.proxy.get_workflow, workflow.Workflow)

    def test_execution_get(self):
        self.verify_get(self.proxy.get_execution, execution.Execution)

    def test_workflow_create(self):
        self.verify_create(self.proxy.create_workflow, workflow.Workflow)

    def test_workflow_update(self):
        self.verify_update(self.proxy.update_workflow, workflow.Workflow)

    def test_execution_create(self):
        self.verify_create(self.proxy.create_execution, execution.Execution)

    def test_workflow_delete(self):
        self.verify_delete(self.proxy.delete_workflow, workflow.Workflow, True)

    def test_execution_delete(self):
        self.verify_delete(
            self.proxy.delete_execution, execution.Execution, True
        )

    def test_workflow_find(self):
        self.verify_find(self.proxy.find_workflow, workflow.Workflow)

    def test_execution_find(self):
        self.verify_find(self.proxy.find_execution, execution.Execution)


class TestCronTriggerProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_cron_triggers(self):
        self.verify_list(self.proxy.cron_triggers, cron_trigger.CronTrigger)

    def test_cron_trigger_get(self):
        self.verify_get(self.proxy.get_cron_trigger, cron_trigger.CronTrigger)

    def test_cron_trigger_create(self):
        self.verify_create(
            self.proxy.create_cron_trigger, cron_trigger.CronTrigger
        )

    def test_cron_trigger_delete(self):
        self.verify_delete(
            self.proxy.delete_cron_trigger, cron_trigger.CronTrigger, True
        )

    def test_cron_trigger_find(self):
        self.verify_find(
            self.proxy.find_cron_trigger,
            cron_trigger.CronTrigger,
            expected_kwargs={'all_projects': False},
        )
