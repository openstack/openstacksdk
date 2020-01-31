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

from openstack.accelerator.v2 import _proxy
from openstack.accelerator.v2 import deployable
from openstack.accelerator.v2 import device_profile
from openstack.accelerator.v2 import accelerator_request
from openstack.tests.unit import test_proxy_base as test_proxy_base


class TestAcceleratorProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestAcceleratorProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_list_deployables(self):
        self.verify_list(self.proxy.deployables, deployable.Deployable)

    def test_list_device_profile(self):
        self.verify_list(self.proxy.device_profiles,
                         device_profile.DeviceProfile)

    def test_create_device_profile(self):
        self.verify_create(self.proxy.create_device_profile,
                           device_profile.DeviceProfile)

    def test_delete_device_profile(self):
        self.verify_delete(self.proxy.delete_device_profile,
                           device_profile.DeviceProfile, False)

    def test_delete_device_profile_ignore(self):
        self.verify_delete(self.proxy.delete_device_profile,
                           device_profile.DeviceProfile, True)

    def test_get_device_profile(self):
        self.verify_get(self.proxy.get_device_profile,
                        device_profile.DeviceProfile)

    def test_list_accelerator_request(self):
        self.verify_list(self.proxy.accelerator_requests,
                         accelerator_request.AcceleratorRequest)

    def test_create_accelerator_request(self):
        self.verify_create(self.proxy.create_accelerator_request,
                           accelerator_request.AcceleratorRequest)

    def test_delete_accelerator_request(self):
        self.verify_delete(self.proxy.delete_accelerator_request,
                           accelerator_request.AcceleratorRequest, False)

    def test_delete_accelerator_request_ignore(self):
        self.verify_delete(self.proxy.delete_accelerator_request,
                           accelerator_request.AcceleratorRequest, True)

    def test_get_accelerator_request(self):
        self.verify_get(self.proxy.get_accelerator_request,
                        accelerator_request.AcceleratorRequest)
