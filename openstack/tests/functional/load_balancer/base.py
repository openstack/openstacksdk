# Copyright 2017 Rackspace, US Inc.
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

import time

from openstack import exceptions
from openstack.tests.functional import base


class BaseLBFunctionalTest(base.BaseFunctionalTest):

    def lb_wait_for_status(self, lb, status, failures, interval=1, wait=120):
        """Wait for load balancer to be in a particular provisioning status.

        :param lb: The load balancer to wait on to reach the status.
        :type lb: :class:`~openstack.load_blanacer.v2.load_balancer
        :param status: Desired status of the resource.
        :param list failures: Statuses that would indicate the transition
                              failed such as 'ERROR'.
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
                     Note, most actions should easily finish in 120 seconds,
                     but for load balancer create slow hosts can take up to
                     ten minutes for nova to fully boot a VM.
        :return: None
        :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
                 to status failed to occur in wait seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` resource
                 transitioned to one of the failure states.
        """

        total_sleep = 0
        if failures is None:
            failures = []

        while total_sleep < wait:
            lb = self.conn.load_balancer.get_load_balancer(lb.id)
            if lb.provisioning_status == status:
                return None
            if lb.provisioning_status in failures:
                msg = ("Load Balancer %s transitioned to failure state %s" %
                       (lb.id, lb.provisioning_status))
                raise exceptions.ResourceFailure(msg)
            time.sleep(interval)
            total_sleep += interval
        msg = "Timeout waiting for Load Balancer %s to transition to %s" % (
            lb.id, status)
        raise exceptions.ResourceTimeout(msg)
