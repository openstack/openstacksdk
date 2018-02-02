# -*- coding: utf-8 -*-

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
import datetime
import uuid

from openstack.tests.unit import base


class TestUsage(base.TestCase):

    def test_get_usage(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        start = end = datetime.datetime.now()

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-simple-tenant-usage', project.project_id],
                     qs_elements=[
                         'start={now}'.format(now=start.isoformat()),
                         'end={now}'.format(now=end.isoformat()),
                     ]),
                 json={"tenant_usage": {
                     "server_usages": [
                         {
                             "ended_at": None,
                             "flavor": "m1.tiny",
                             "hours": 1.0,
                             "instance_id": uuid.uuid4().hex,
                             "local_gb": 1,
                             "memory_mb": 512,
                             "name": "instance-2",
                             "started_at": "2012-10-08T20:10:44.541277",
                             "state": "active",
                             "tenant_id": "6f70656e737461636b20342065766572",
                             "uptime": 3600,
                             "vcpus": 1
                         }
                     ],
                     "start": "2012-10-08T20:10:44.587336",
                     "stop": "2012-10-08T21:10:44.587336",
                     "tenant_id": "6f70656e737461636b20342065766572",
                     "total_hours": 1.0,
                     "total_local_gb_usage": 1.0,
                     "total_memory_mb_usage": 512.0,
                     "total_vcpus_usage": 1.0
                 }})
        ])

        self.cloud.get_compute_usage(project.project_id, start, end)

        self.assert_calls()
