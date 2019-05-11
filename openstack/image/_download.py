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
import io
import hashlib
import six

from openstack import exceptions
from openstack import utils


def _verify_checksum(md5, checksum):
    if checksum:
        digest = md5.hexdigest()
        if digest != checksum:
            raise exceptions.InvalidResponse(
                "checksum mismatch: %s != %s" % (checksum, digest))


class DownloadMixin(object):

    def download(self, session, stream=False, output=None, chunk_size=1024):
        """Download the data contained in an image"""
        # TODO(briancurtin): This method should probably offload the get
        # operation into another thread or something of that nature.
        url = utils.urljoin(self.base_path, self.id, 'file')
        resp = session.get(url, stream=stream)

        # See the following bug report for details on why the checksum
        # code may sometimes depend on a second GET call.
        # https://storyboard.openstack.org/#!/story/1619675
        checksum = resp.headers.get("Content-MD5")

        if checksum is None:
            # If we don't receive the Content-MD5 header with the download,
            # make an additional call to get the image details and look at
            # the checksum attribute.
            details = self.fetch(session)
            checksum = details.checksum

        md5 = hashlib.md5()
        if output:
            try:
                # In python 2 we might get StringIO - delete it as soon as
                # py2 support is dropped
                if isinstance(output, io.IOBase) \
                        or isinstance(output, six.StringIO):
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        output.write(chunk)
                        md5.update(chunk)
                else:
                    with open(output, 'wb') as fd:
                        for chunk in resp.iter_content(
                                chunk_size=chunk_size):
                            fd.write(chunk)
                            md5.update(chunk)
                _verify_checksum(md5, checksum)

                return resp
            except Exception as e:
                raise exceptions.SDKException(
                    "Unable to download image: %s" % e)
        # if we are returning the repsonse object, ensure that it
        # has the content-md5 header so that the caller doesn't
        # need to jump through the same hoops through which we
        # just jumped.
        if stream:
            resp.headers['content-md5'] = checksum
            return resp

        if checksum is not None:
            _verify_checksum(hashlib.md5(resp.content), checksum)
        else:
            session.log.warning(
                "Unable to verify the integrity of image %s", (self.id))

        return resp
