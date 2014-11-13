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

from openstack.image.v1 import image


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def create_image(self, **data):
        return image.Image(data).create(self.session)

    def delete_image(self, **data):
        return image.Image(data).delete(self.session)

    def find_image(self, name_or_id):
        return image.Image.find(self.session, name_or_id)

    def get_image(self, **data):
        return image.Image(data).get(self.session)

    def list_images(self, **params):
        return image.Image.list(self.session, **params)

    def update_image(self, **data):
        return image.Image(data).update(self.session)
