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
import abc

import six

from openstack import exceptions
from openstack import proxy


class BaseBlockStorageProxy(six.with_metaclass(abc.ABCMeta, proxy.Proxy)):

    def create_image(
            self, name, volume, allow_duplicates,
            container_format, disk_format, wait, timeout):
        if not disk_format:
            disk_format = self._connection.config.config['image_format']
        if not container_format:
            # https://docs.openstack.org/image-guide/image-formats.html
            container_format = 'bare'

        if 'id' in volume:
            volume_id = volume['id']
        else:
            volume_obj = self.get_volume(volume)
            if not volume_obj:
                raise exceptions.SDKException(
                    "Volume {volume} given to create_image could"
                    " not be found".format(volume=volume))
            volume_id = volume_obj['id']
        data = self.post(
            '/volumes/{id}/action'.format(id=volume_id),
            json={
                'os-volume_upload_image': {
                    'force': allow_duplicates,
                    'image_name': name,
                    'container_format': container_format,
                    'disk_format': disk_format}})
        response = self._connection._get_and_munchify(
            'os-volume_upload_image', data)
        return self._connection.image._existing_image(id=response['image_id'])
