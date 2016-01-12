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

import six

from openstack import utils


class MetadataMixin(object):

    def _metadata(self, method, key=None, clear=False, delete=False,
                  **metadata):
        for k, v in metadata.items():
            if not isinstance(v, six.string_types):
                raise ValueError("The value for %s (%s) must be "
                                 "a text string" % (k, v))

        # If we're in a ServerDetail, we need to pop the "detail" portion
        # of the URL off and then everything else will work the same.
        pos = self.base_path.find("detail")
        if pos != -1:
            base = self.base_path[:pos]
        else:
            base = self.base_path

        if key is not None:
            url = utils.urljoin(base, self.id, "metadata", key)
        else:
            url = utils.urljoin(base, self.id, "metadata")

        kwargs = {"endpoint_filter": self.service}
        if metadata or clear:
            # 'meta' is the key for singlular modifications.
            # 'metadata' is the key for mass modifications.
            key = "meta" if key is not None else "metadata"
            kwargs["json"] = {key: metadata}

        headers = {"Accept": ""} if delete else {}

        response = method(url, headers=headers, **kwargs)

        # DELETE doesn't return a JSON body while everything else does.
        return response.json() if not delete else None

    def get_metadata(self, session, key=None):
        """Retrieve metadata

        :param session: The session to use for this request.
        :param key: If specified, retrieve metadata only for this key.
                    If not specified, or ``None`` (the default),
                    retrieve all available metadata.

        :returns: A dictionary of the requested metadata. All keys and values
                  are Unicode text.
        :rtype: dict
        """
        result = self._metadata(session.get, key=key)
        return result["metadata"] if key is None else result["meta"]

    def create_metadata(self, session, **metadata):
        """Create metadata

        NOTE: One PUT call will be made for each key/value pair specified.

        :param session: The session to use for this request.
        :param kwargs metadata: key/value metadata pairs to be created on
                                this server instance. All keys and values
                                are stored as Unicode.

        :returns: A dictionary of the metadata that was created. All keys and
                  values are Unicode text.
        :rtype: dict
        """
        results = {}
        # A PUT to /metadata will entirely replace any existing metadata,
        # so we need to PUT each individual key/value to /metadata/key
        # in order to preserve anything existing and only add new keys.
        for key, value in metadata.items():
            result = self._metadata(session.put, key=key, **{key: value})
            results[key] = result["meta"][key]
        return results

    def replace_metadata(self, session, **metadata):
        """Replace metadata

        This call will replace any existing metadata with the key/value pairs
        given here.

        :param session: The session to use for this request.
        :param kwargs metadata: key/value metadata pairs to be created on
                                this server instance. Any other existing
                                metadata is removed.
                                When metadata is not set, it is effectively
                                cleared out, replacing the metadata
                                with nothing.
                                All keys and values are stored as Unicode.


        :returns: A dictionary of the metadata after being replaced.
                  All keys and values are Unicode text.
        :rtype: dict
        """
        # A PUT with empty metadata will clear anything out.
        clear = True if not metadata else False
        result = self._metadata(session.put, clear=clear, **metadata)
        return result["metadata"]

    def update_metadata(self, session, **metadata):
        """Update metadata

        This call will replace only the metadata with the same keys
        given here. Metadata with other keys will not be modified.

        :param session: The session to use for this request.
        :param kwargs metadata: key/value metadata pairs to be update on
                                this server instance. All keys and values
                                are stored as Unicode.

        :returns: A dictionary of the metadata after being updated.
                  All keys and values are Unicode text.
        :rtype: dict
        """
        result = self._metadata(session.post, **metadata)
        return result["metadata"]

    def delete_metadata(self, session, key):
        """Delete metadata

        :param session: The session to use for this request.
        :param string key: The key to delete.

        :rtype: ``None``
        """
        self._metadata(session.delete, key=key, delete=True)
