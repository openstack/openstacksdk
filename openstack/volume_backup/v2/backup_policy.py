#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
from openstack import format
from openstack import resource2 as resource
from openstack import utils
from openstack.volume_backup import volume_backup_service


class SchedulePolicy(resource.Resource):
    #: whether keep the first backup of current month
    remain_first_backup_of_curMonth = resource.Body(
        "remain_first_backup_of_curMonth", type=format.YNBool)
    #: the max backup amount, min value is 2
    rentention_num = resource.Body("rentention_num", type=int)
    #: backup period, valid values, 1..14 (days)
    frequency = resource.Body("frequency", type=int)
    #: backup start time of every day, example: 12:00
    start_time = resource.Body("start_time")
    #: backup policy status, ``ON``, ``OFF``
    status = resource.Body("status")


class BackupPolicy(resource.Resource):
    """Cloud Backup"""
    resources_key = "backup_policies"
    base_path = "/backuppolicy"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True
    allow_update = True

    #: Properties
    #: Backup Policy id
    id = resource.Body("backup_policy_id")
    #: Backup Policy name
    name = resource.Body("backup_policy_name")
    #: Backup Policy resource count
    policy_resource_count = resource.Body("policy_resource_count")
    #: Backup Policy schedule detail
    scheduled_policy = resource.Body("scheduled_policy", type=SchedulePolicy)

    def execute(self, session):
        """execute backup policy immediately

        :param session: openstack session
        :return: request response
        """
        url = utils.urljoin(self.base_path, self.id, "action")
        endpoint_override = self.service.get_endpoint_override()
        return session.post(url,
                            endpoint_filter=self.service,
                            endpoint_override=endpoint_override,
                            headers={},
                            json=None)


class BindResource(resource.Resource):
    resources_key = "success_resources"
    base_path = "/backuppolicyresources"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_create = True

    #: Properties
    resource_id = resource.Body("resource_id")
    os_vol_host_attr = resource.Body("os_vol_host_attr")
    availability_zone = resource.Body("availability_zone")
    resource_type = resource.Body("resource_type")

    def bind_resources(self, session, backup_policy_id, resources):
        """bind resources to backup policy

        :param session: openstack session
        :param backup_policy_id: backup policy id
        :param resources: resources to bound, should be a list of volume id
        :return:
        """
        _resources = [dict(resource_id=volume_id, resource_type="volume")
                      for volume_id in resources]
        body = {
            "backup_policy_id": backup_policy_id,
            "resources": _resources
        }
        endpoint_override = self.service.get_endpoint_override()
        response = session.post(self.base_path,
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=body,
                                headers={})
        self._translate_response(response)
        return self


class LindedResource(resource.Resource):
    base_path = "/backuppolicyresources"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_create = True

    #: Properties
    resource_id = resource.Body("resource_id")
    resource_type = resource.Body("resource_type")
    availability_zone = resource.Body("availability_zone")
    os_vol_host_attr = resource.Body("os_vol_host_attr")
    message = resource.Body("message")
    code = resource.Body("code")
    success = resource.Body("success", type=bool)

    def link(self, session, backup_policy_id, resources):
        """link resources to backup policy

        :param session: openstack session
        :param backup_policy_id: backup policy id
        :param resources: resources to bound, should be a list of volume id
        :return:
        """
        _resources = [dict(resource_id=volume_id, resource_type="volume")
                      for volume_id in resources]
        body = {
            "backup_policy_id": backup_policy_id,
            "resources": _resources
        }
        endpoint_override = self.service.get_endpoint_override()
        response = session.post(self.base_path,
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=body,
                                headers={})

        result = []
        response_json = response.json()
        if response_json and response_json["success_resources"]:
            for _resource in response_json["success_resources"]:
                _resource["success"] = True
                result.append(LindedResource.new(**_resource))

        if response_json and response_json["fail_resources"]:
            for _resource in response_json["fail_resources"]:
                _resource["success"] = False
                result.append(LindedResource.new(**_resource))

        return result


class UnlinkedResource(resource.Resource):
    base_path = "/backuppolicyresources"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_create = True

    #: Properties
    resource_id = resource.Body("resource_id")
    message = resource.Body("message")
    code = resource.Body("code")
    success = resource.Body("success", type=bool)

    def unlink(self, session, backup_policy_id, resources):
        """unlink resources of backup policy

        :param session: openstack session
        :param backup_policy_id: backup policy id
        :param resources: resources to bound, should be a list of volume id
        :return:
        """
        _resources = [dict(resource_id=volume_id) for volume_id in resources]
        body = {"resources": _resources}
        endpoint_override = self.service.get_endpoint_override()
        uri = utils.urljoin(self.base_path,
                            backup_policy_id,
                            "deleted_resources")
        response = session.post(uri,
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=body,
                                headers={})

        result = []
        response_json = response.json()
        if response_json and response_json["success_resources"]:
            for _resource in response_json["success_resources"]:
                _resource["success"] = True
                result.append(UnlinkedResource.new(**_resource))

        if response_json and response_json["fail_resources"]:
            for _resource in response_json["fail_resources"]:
                _resource["success"] = False
                result.append(UnlinkedResource.new(**_resource))

        return result
