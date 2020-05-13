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

from calendar import timegm
import collections
from hashlib import sha1
import hmac
import json
import os
import time
from urllib import parse

from openstack.object_store.v1 import account as _account
from openstack.object_store.v1 import container as _container
from openstack.object_store.v1 import obj as _obj
from openstack.object_store.v1 import info as _info
from openstack import exceptions
from openstack import _log
from openstack import proxy
from openstack.cloud import _utils

DEFAULT_OBJECT_SEGMENT_SIZE = 1073741824  # 1GB
DEFAULT_MAX_FILE_SIZE = (5 * 1024 * 1024 * 1024 + 2) / 2
EXPIRES_ISO8601_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
SHORT_EXPIRES_ISO8601_FORMAT = '%Y-%m-%d'


class Proxy(proxy.Proxy):

    skip_discovery = True

    Account = _account.Account
    Container = _container.Container
    Object = _obj.Object

    log = _log.setup_logging('openstack')

    def _extract_name(self, url, service_type=None, project_id=None):
        url_path = parse.urlparse(url).path.strip()
        # Remove / from the beginning to keep the list indexes of interesting
        # things consistent
        if url_path.startswith('/'):
            url_path = url_path[1:]

        # Split url into parts and exclude potential project_id in some urls
        url_parts = [
            x for x in url_path.split('/') if (
                x != project_id
                and (
                    not project_id
                    or (project_id and x != 'AUTH_' + project_id)
                ))
        ]
        # Strip leading version piece so that
        # GET /v1/AUTH_xxx
        # returns ['AUTH_xxx']
        if (url_parts[0]
                and url_parts[0][0] == 'v'
                and url_parts[0][1] and url_parts[0][1].isdigit()):
            url_parts = url_parts[1:]

        # Strip out anything that's empty or None
        parts = [part for part in url_parts if part]

        # Getting the root of an endpoint is doing version discovery
        if not parts:
            return ['account']

        if len(parts) == 1:
            if 'endpoints' in parts:
                return ['endpoints']
            else:
                return ['container']
        else:
            return ['object']

    def get_account_metadata(self):
        """Get metadata for this account.

        :rtype:
            :class:`~openstack.object_store.v1.account.Account`
        """
        return self._head(_account.Account)

    def set_account_metadata(self, **metadata):
        """Set metadata for this account.

        :param kwargs metadata: Key/value pairs to be set as metadata
                                on the container. Custom  metadata can be set.
                                Custom metadata are keys and values defined
                                by the user.
        """
        account = self._get_resource(_account.Account, None)
        account.set_metadata(self, metadata)

    def delete_account_metadata(self, keys):
        """Delete metadata for this account.

        :param keys: The keys of metadata to be deleted.
        """
        account = self._get_resource(_account.Account, None)
        account.delete_metadata(self, keys)

    def containers(self, **query):
        """Obtain Container objects for this account.

        :param kwargs query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :rtype: A generator of
            :class:`~openstack.object_store.v1.container.Container` objects.
        """
        return self._list(_container.Container, paginated=True, **query)

    def create_container(self, name, **attrs):
        """Create a new container from attributes

        :param container: Name of the container to create.
        :param dict attrs: Keyword arguments which will be used to create
               a :class:`~openstack.object_store.v1.container.Container`,
               comprised of the properties on the Container class.

        :returns: The results of container creation
        :rtype: :class:`~openstack.object_store.v1.container.Container`
        """
        return self._create(_container.Container, name=name, **attrs)

    def delete_container(self, container, ignore_missing=True):
        """Delete a container

        :param container: The value can be either the name of a container or a
                      :class:`~openstack.object_store.v1.container.Container`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the container does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(_container.Container, container,
                     ignore_missing=ignore_missing)

    def get_container_metadata(self, container):
        """Get metadata for a container

        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: One :class:`~openstack.object_store.v1.container.Container`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._head(_container.Container, container)

    def set_container_metadata(self, container, refresh=True, **metadata):
        """Set metadata for a container.

        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param refresh: Flag to trigger refresh of container object re-fetch.
        :param kwargs metadata: Key/value pairs to be set as metadata
                                on the container. Both custom and system
                                metadata can be set. Custom metadata are keys
                                and values defined by the user. System
                                metadata are keys defined by the Object Store
                                and values defined by the user. The system
                                metadata keys are:

                                - `content_type`
                                - `is_content_type_detected`
                                - `versions_location`
                                - `read_ACL`
                                - `write_ACL`
                                - `sync_to`
                                - `sync_key`
        """
        res = self._get_resource(_container.Container, container)
        res.set_metadata(self, metadata, refresh=refresh)
        return res

    def delete_container_metadata(self, container, keys):
        """Delete metadata for a container.

        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param keys: The keys of metadata to be deleted.
        """
        res = self._get_resource(_container.Container, container)
        res.delete_metadata(self, keys)
        return res

    def objects(self, container, **query):
        """Return a generator that yields the Container's objects.

        :param container: A container object or the name of a container
            that you want to retrieve objects from.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        :param kwargs query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :rtype: A generator of
            :class:`~openstack.object_store.v1.obj.Object` objects.
        """
        container = self._get_container_name(container=container)

        for obj in self._list(
                _obj.Object, container=container,
                paginated=True, format='json', **query):
            obj.container = container
            yield obj

    def _get_container_name(self, obj=None, container=None):
        if obj is not None:
            obj = self._get_resource(_obj.Object, obj)
            if obj.container is not None:
                return obj.container
        if container is not None:
            container = self._get_resource(_container.Container, container)
            return container.name

        raise ValueError("container must be specified")

    def get_object(self, obj, container=None):
        """Get the data associated with an object

        :param obj: The value can be the name of an object or a
                       :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: The contents of the object.  Use the
                  :func:`~get_object_metadata`
                  method if you want an object resource.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(
            obj=obj, container=container)
        return self._get(_obj.Object, obj, container=container_name)

    def download_object(self, obj, container=None, **attrs):
        """Download the data contained inside an object.

        :param obj: The value can be the name of an object or a
                       :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(
            obj=obj, container=container)
        obj = self._get_resource(
            _obj.Object, obj, container=container_name, **attrs)
        return obj.download(self)

    def stream_object(self, obj, container=None, chunk_size=1024, **attrs):
        """Stream the data contained inside an object.

        :param obj: The value can be the name of an object or a
                       :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        :returns: An iterator that iterates over chunk_size bytes
        """
        container_name = self._get_container_name(
            obj=obj, container=container)
        container_name = self._get_container_name(container=container)
        obj = self._get_resource(
            _obj.Object, obj, container=container_name, **attrs)
        return obj.stream(self, chunk_size=chunk_size)

    def create_object(
            self, container, name, filename=None,
            md5=None, sha256=None, segment_size=None,
            use_slo=True, metadata=None,
            generate_checksums=None, data=None,
            **headers):
        """Create a file object.

        Automatically uses large-object segments if needed.

        :param container: The name of the container to store the file in.
            This container will be created if it does not exist already.
        :param name: Name for the object within the container.
        :param filename: The path to the local file whose contents will be
            uploaded. Mutually exclusive with data.
        :param data: The content to upload to the object. Mutually exclusive
           with filename.
        :param md5: A hexadecimal md5 of the file. (Optional), if it is known
            and can be passed here, it will save repeating the expensive md5
            process. It is assumed to be accurate.
        :param sha256: A hexadecimal sha256 of the file. (Optional) See md5.
        :param segment_size: Break the uploaded object into segments of this
            many bytes. (Optional) SDK will attempt to discover the maximum
            value for this from the server if it is not specified, or will use
            a reasonable default.
        :param headers: These will be passed through to the object creation
            API as HTTP Headers.
        :param use_slo: If the object is large enough to need to be a Large
            Object, use a static rather than dynamic object. Static Objects
            will delete segment objects when the manifest object is deleted.
            (optional, defaults to True)
        :param generate_checksums: Whether to generate checksums on the client
            side that get added to headers for later prevention of double
            uploads of identical data. (optional, defaults to True)
        :param metadata: This dict will get changed into headers that set
            metadata of the object

        :raises: ``OpenStackCloudException`` on operation error.
        """
        if data is not None and filename:
            raise ValueError(
                "Both filename and data given. Please choose one.")
        if data is not None and not name:
            raise ValueError(
                "name is a required parameter when data is given")
        if data is not None and generate_checksums:
            raise ValueError(
                "checksums cannot be generated with data parameter")
        if generate_checksums is None:
            if data is not None:
                generate_checksums = False
            else:
                generate_checksums = True

        if not metadata:
            metadata = {}

        if not filename and data is None:
            filename = name

        if generate_checksums and (md5 is None or sha256 is None):
            (md5, sha256) = self._connection._get_file_hashes(filename)
        if md5:
            headers[self._connection._OBJECT_MD5_KEY] = md5 or ''
        if sha256:
            headers[self._connection._OBJECT_SHA256_KEY] = sha256 or ''
        for (k, v) in metadata.items():
            if not k.lower().startswith('x-object-meta-'):
                headers['x-object-meta-' + k] = v
            else:
                headers[k] = v

        container_name = self._get_container_name(container=container)
        endpoint = '{container}/{name}'.format(container=container_name,
                                               name=name)

        if data is not None:
            self.log.debug(
                "swift uploading data to %(endpoint)s",
                {'endpoint': endpoint})
            # TODO(gtema): custom headers need to be somehow injected
            return self._create(
                _obj.Object, container=container_name,
                name=name, data=data, **headers)

        # segment_size gets used as a step value in a range call, so needs
        # to be an int
        if segment_size:
            segment_size = int(segment_size)
        segment_size = self.get_object_segment_size(segment_size)
        file_size = os.path.getsize(filename)

        if self.is_object_stale(container_name, name, filename, md5, sha256):

            self._connection.log.debug(
                "swift uploading %(filename)s to %(endpoint)s",
                {'filename': filename, 'endpoint': endpoint})

            if file_size <= segment_size:
                # TODO(gtema): replace with regular resource put, but
                # custom headers need to be somehow injected
                self._upload_object(endpoint, filename, headers)
            else:
                self._upload_large_object(
                    endpoint, filename, headers,
                    file_size, segment_size, use_slo)

    # Backwards compat
    upload_object = create_object

    def copy_object(self):
        """Copy an object."""
        raise NotImplementedError

    def delete_object(self, obj, ignore_missing=True, container=None):
        """Delete an object

        :param obj: The value can be either the name of an object or a
                       :class:`~openstack.object_store.v1.container.Container`
                       instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the object does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        container_name = self._get_container_name(obj, container)

        self._delete(_obj.Object, obj, ignore_missing=ignore_missing,
                     container=container_name)

    def get_object_metadata(self, obj, container=None):
        """Get metadata for an object.

        :param obj: The value can be the name of an object or a
                    :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: One :class:`~openstack.object_store.v1.obj.Object`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(obj, container)

        return self._head(_obj.Object, obj, container=container_name)

    def set_object_metadata(self, obj, container=None, **metadata):
        """Set metadata for an object.

        Note: This method will do an extra HEAD call.

        :param obj: The value can be the name of an object or a
                    :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param kwargs metadata: Key/value pairs to be set as metadata
                                on the container. Both custom and system
                                metadata can be set. Custom metadata are keys
                                and values defined by the user. System
                                metadata are keys defined by the Object Store
                                and values defined by the user. The system
                                metadata keys are:

                                - `content_type`
                                - `content_encoding`
                                - `content_disposition`
                                - `delete_after`
                                - `delete_at`
                                - `is_content_type_detected`
        """
        container_name = self._get_container_name(obj, container)
        res = self._get_resource(_obj.Object, obj, container=container_name)
        res.set_metadata(self, metadata)
        return res

    def delete_object_metadata(self, obj, container=None, keys=None):
        """Delete metadata for an object.

        :param obj: The value can be the name of an object or a
                    :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param keys: The keys of metadata to be deleted.
        """
        container_name = self._get_container_name(obj, container)
        res = self._get_resource(_obj.Object, obj, container=container_name)
        res.delete_metadata(self, keys)
        return res

    def is_object_stale(
            self, container, name, filename, file_md5=None, file_sha256=None):
        """Check to see if an object matches the hashes of a file.

        :param container: Name of the container.
        :param name: Name of the object.
        :param filename: Path to the file.
        :param file_md5:
            Pre-calculated md5 of the file contents. Defaults to None which
            means calculate locally.
        :param file_sha256:
            Pre-calculated sha256 of the file contents. Defaults to None which
            means calculate locally.
        """
        metadata = self._connection.get_object_metadata(container, name)
        if not metadata:
            self._connection.log.debug(
                "swift stale check, no object: {container}/{name}".format(
                    container=container, name=name))
            return True

        if not (file_md5 or file_sha256):
            (file_md5, file_sha256) = \
                self._connection._get_file_hashes(filename)
        md5_key = metadata.get(
            self._connection._OBJECT_MD5_KEY,
            metadata.get(self._connection._SHADE_OBJECT_MD5_KEY, ''))
        sha256_key = metadata.get(
            self._connection._OBJECT_SHA256_KEY, metadata.get(
                self._connection._SHADE_OBJECT_SHA256_KEY, ''))
        up_to_date = self._connection._hashes_up_to_date(
            md5=file_md5, sha256=file_sha256,
            md5_key=md5_key, sha256_key=sha256_key)

        if not up_to_date:
            self._connection.log.debug(
                "swift checksum mismatch: "
                " %(filename)s!=%(container)s/%(name)s",
                {'filename': filename, 'container': container, 'name': name})
            return True

        self._connection.log.debug(
            "swift object up to date: %(container)s/%(name)s",
            {'container': container, 'name': name})
        return False

    def _upload_large_object(
            self, endpoint, filename,
            headers, file_size, segment_size, use_slo):
        # If the object is big, we need to break it up into segments that
        # are no larger than segment_size, upload each of them individually
        # and then upload a manifest object. The segments can be uploaded in
        # parallel, so we'll use the async feature of the TaskManager.

        segment_futures = []
        segment_results = []
        retry_results = []
        retry_futures = []
        manifest = []

        # Get an OrderedDict with keys being the swift location for the
        # segment, the value a FileSegment file-like object that is a
        # slice of the data for the segment.
        segments = self._get_file_segments(
            endpoint, filename, file_size, segment_size)

        # Schedule the segments for upload
        for name, segment in segments.items():
            # Async call to put - schedules execution and returns a future
            segment_future = self._connection._pool_executor.submit(
                self.put,
                name, headers=headers, data=segment,
                raise_exc=False)
            segment_futures.append(segment_future)
            # TODO(mordred) Collect etags from results to add to this manifest
            # dict. Then sort the list of dicts by path.
            manifest.append(dict(
                path='/{name}'.format(name=name),
                size_bytes=segment.length))

        # Try once and collect failed results to retry
        segment_results, retry_results = self._connection._wait_for_futures(
            segment_futures, raise_on_error=False)

        self._add_etag_to_manifest(segment_results, manifest)

        for result in retry_results:
            # Grab the FileSegment for the failed upload so we can retry
            name = self._object_name_from_url(result.url)
            segment = segments[name]
            segment.seek(0)
            # Async call to put - schedules execution and returns a future
            segment_future = self._connection._pool_executor.submit(
                self.put,
                name, headers=headers, data=segment)
            # TODO(mordred) Collect etags from results to add to this manifest
            # dict. Then sort the list of dicts by path.
            retry_futures.append(segment_future)

        # If any segments fail the second time, just throw the error
        segment_results, retry_results = self._connection._wait_for_futures(
            retry_futures, raise_on_error=True)

        self._add_etag_to_manifest(segment_results, manifest)

        if use_slo:
            return self._finish_large_object_slo(endpoint, headers, manifest)
        else:
            return self._finish_large_object_dlo(endpoint, headers)

    def _finish_large_object_slo(self, endpoint, headers, manifest):
        # TODO(mordred) send an etag of the manifest, which is the md5sum
        # of the concatenation of the etags of the results
        headers = headers.copy()
        return self.put(
            endpoint,
            params={'multipart-manifest': 'put'},
            headers=headers, data=json.dumps(manifest))

    def _finish_large_object_dlo(self, endpoint, headers):
        headers = headers.copy()
        headers['X-Object-Manifest'] = endpoint
        return self.put(endpoint, headers=headers)

    def _upload_object(self, endpoint, filename, headers):
        with open(filename, 'rb') as dt:
            return proxy._json_response(self.put(
                endpoint, headers=headers, data=dt))

    def _get_file_segments(self, endpoint, filename, file_size, segment_size):
        # Use an ordered dict here so that testing can replicate things
        segments = collections.OrderedDict()
        for (index, offset) in enumerate(range(0, file_size, segment_size)):
            remaining = file_size - (index * segment_size)
            segment = _utils.FileSegment(
                filename, offset,
                segment_size if segment_size < remaining else remaining)
            name = '{endpoint}/{index:0>6}'.format(
                endpoint=endpoint, index=index)
            segments[name] = segment
        return segments

    def get_object_segment_size(self, segment_size):
        """Get a segment size that will work given capabilities"""
        if segment_size is None:
            segment_size = DEFAULT_OBJECT_SEGMENT_SIZE
        min_segment_size = 0
        try:
            # caps = self.get_object_capabilities()
            caps = self.get_info()
        except exceptions.SDKException as e:
            if e.response.status_code in (404, 412):
                server_max_file_size = DEFAULT_MAX_FILE_SIZE
                self._connection.log.info(
                    "Swift capabilities not supported. "
                    "Using default max file size.")
            else:
                raise
        else:
            server_max_file_size = caps.swift.get('max_file_size', 0)
            min_segment_size = caps.slo.get('min_segment_size', 0)

        if segment_size > server_max_file_size:
            return server_max_file_size
        if segment_size < min_segment_size:
            return min_segment_size
        return segment_size

    def _object_name_from_url(self, url):
        '''Get container_name/object_name from the full URL called.

        Remove the Swift endpoint from the front of the URL, and remove
        the leaving / that will leave behind.'''
        endpoint = self.get_endpoint()
        object_name = url.replace(endpoint, '')
        if object_name.startswith('/'):
            object_name = object_name[1:]
        return object_name

    def _add_etag_to_manifest(self, segment_results, manifest):
        for result in segment_results:
            if 'Etag' not in result.headers:
                continue
            name = self._object_name_from_url(result.url)
            for entry in manifest:
                if entry['path'] == '/{name}'.format(name=name):
                    entry['etag'] = result.headers['Etag']

    def get_info(self):
        """Get infomation about the object-storage service

        The object-storage service publishes a set of capabilities that
        include metadata about maximum values and thresholds.
        """
        return self._get(_info.Info)

    def set_account_temp_url_key(self, key, secondary=False):
        """Set the temporary URL key for the account.

        :param key:
          Text of the key to use.
        :param bool secondary:
          Whether this should set the secondary key. (defaults to False)
        """
        account = self._get_resource(_account.Account, None)
        account.set_temp_url_key(self, key, secondary)

    def set_container_temp_url_key(self, container, key, secondary=False):
        """Set the temporary URL key for a container.

        :param container:
          The value can be the name of a container or a
          :class:`~openstack.object_store.v1.container.Container` instance.
        :param key:
          Text of the key to use.
        :param bool secondary:
          Whether this should set the secondary key. (defaults to False)
        """
        res = self._get_resource(_container.Container, container)
        res.set_temp_url_key(self, key, secondary)

    def get_temp_url_key(self, container=None):
        """Get the best temporary url key for a given container.

        Will first try to return Temp-URL-Key-2 then Temp-URL-Key for
        the container, and if neither exist, will attempt to return
        Temp-URL-Key-2 then Temp-URL-Key for the account. If neither
        exist, will return None.

        :param container:
          The value can be the name of a container or a
          :class:`~openstack.object_store.v1.container.Container` instance.
        """
        temp_url_key = None
        if container:
            container_meta = self.get_container_metadata(container)
            temp_url_key = (container_meta.meta_temp_url_key_2
                            or container_meta.meta_temp_url_key)
        if not temp_url_key:
            account_meta = self.get_account_metadata()
            temp_url_key = (account_meta.meta_temp_url_key_2
                            or account_meta.meta_temp_url_key)
        if temp_url_key and not isinstance(temp_url_key, bytes):
            temp_url_key = temp_url_key.encode('utf8')
        return temp_url_key

    def _check_temp_url_key(self, container=None, temp_url_key=None):
        if temp_url_key:
            if not isinstance(temp_url_key, bytes):
                temp_url_key = temp_url_key.encode('utf8')
        else:
            temp_url_key = self.get_temp_url_key(container)
        if not temp_url_key:
            raise exceptions.SDKException(
                'temp_url_key was not given, nor was a temporary url key'
                ' found for the account or the container.')
        return temp_url_key

    def generate_form_signature(
            self, container, object_prefix, redirect_url, max_file_size,
            max_upload_count, timeout, temp_url_key=None):
        """Generate a signature for a FormPost upload.

        :param container:
          The value can be the name of a container or a
          :class:`~openstack.object_store.v1.container.Container` instance.
        :param object_prefix:
          Prefix to apply to limit all object names created using this
          signature.
        :param redirect_url:
          The URL to redirect the browser to after the uploads have
          completed.
        :param max_file_size:
          The maximum file size per file uploaded.
        :param max_upload_count:
          The maximum number of uploaded files allowed.
        :param timeout:
          The number of seconds from now to allow the form post to begin.
        :param temp_url_key:
          The X-Account-Meta-Temp-URL-Key for the account. Optional, if
          omitted, the key will be fetched from the container or the account.
        """
        max_file_size = int(max_file_size)
        if max_file_size < 1:
            raise exceptions.SDKException(
                'Please use a positive max_file_size value.')
        max_upload_count = int(max_upload_count)
        if max_upload_count < 1:
            raise exceptions.SDKException(
                'Please use a positive max_upload_count value.')
        if timeout < 1:
            raise exceptions.SDKException(
                'Please use a positive <timeout> value.')
        expires = int(time.time() + int(timeout))

        temp_url_key = self._check_temp_url_key(container=container,
                                                temp_url_key=temp_url_key)

        res = self._get_resource(_container.Container, container)
        endpoint = parse.urlparse(self.get_endpoint())
        path = '/'.join([endpoint.path, res.name, object_prefix])

        data = '%s\n%s\n%s\n%s\n%s' % (path, redirect_url, max_file_size,
                                       max_upload_count, expires)
        data = data.encode('utf8')
        sig = hmac.new(temp_url_key, data, sha1).hexdigest()

        return (expires, sig)

    def generate_temp_url(
            self, path, seconds, method, absolute=False, prefix=False,
            iso8601=False, ip_range=None, temp_url_key=None):
        """Generates a temporary URL that gives unauthenticated access to the
        Swift object.

        :param path: The full path to the Swift object or prefix if
            a prefix-based temporary URL should be generated. Example:
            /v1/AUTH_account/c/o or /v1/AUTH_account/c/prefix.
        :param seconds: time in seconds or ISO 8601 timestamp.
            If absolute is False and this is the string representation of an
            integer, then this specifies the amount of time in seconds for
            which the temporary URL will be valid.
            If absolute is True then this specifies an absolute time at which
            the temporary URL will expire.
        :param method: A HTTP method, typically either GET or PUT, to allow
            for this temporary URL.
        :param absolute: if True then the seconds parameter is interpreted as a
            Unix timestamp, if seconds represents an integer.
        :param prefix: if True then a prefix-based temporary URL will be
            generated.
        :param iso8601: if True, a URL containing an ISO 8601 UTC timestamp
            instead of a UNIX timestamp will be created.
        :param ip_range: if a valid ip range, restricts the temporary URL to
            the range of ips.
        :param temp_url_key:
          The X-Account-Meta-Temp-URL-Key for the account. Optional, if
          omitted, the key will be fetched from the container or the account.
        :raises ValueError: if timestamp or path is not in valid format.
        :return: the path portion of a temporary URL
        """
        try:
            try:
                timestamp = float(seconds)
            except ValueError:
                formats = (
                    EXPIRES_ISO8601_FORMAT,
                    EXPIRES_ISO8601_FORMAT[:-1],
                    SHORT_EXPIRES_ISO8601_FORMAT)
                for f in formats:
                    try:
                        t = time.strptime(seconds, f)
                    except ValueError:
                        t = None
                    else:
                        if f == EXPIRES_ISO8601_FORMAT:
                            timestamp = timegm(t)
                        else:
                            # Use local time if UTC designator is missing.
                            timestamp = int(time.mktime(t))

                        absolute = True
                        break

                if t is None:
                    raise ValueError()
            else:
                if not timestamp.is_integer():
                    raise ValueError()
                timestamp = int(timestamp)
                if timestamp < 0:
                    raise ValueError()
        except ValueError:
            raise ValueError('time must either be a whole number '
                             'or in specific ISO 8601 format.')

        if isinstance(path, bytes):
            try:
                path_for_body = path.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError('path must be representable as UTF-8')
        else:
            path_for_body = path

        parts = path_for_body.split('/', 4)
        if len(parts) != 5 or parts[0] or not all(
                parts[1:(4 if prefix else 5)]):
            if prefix:
                raise ValueError('path must at least contain /v1/a/c/')
            else:
                raise ValueError('path must be full path to an object'
                                 ' e.g. /v1/a/c/o')

        standard_methods = ['GET', 'PUT', 'HEAD', 'POST', 'DELETE']
        if method.upper() not in standard_methods:
            self.log.warning('Non default HTTP method %s for tempurl '
                             'specified, possibly an error', method.upper())

        if not absolute:
            expiration = int(time.time() + timestamp)
        else:
            expiration = timestamp

        hmac_parts = [method.upper(), str(expiration),
                      ('prefix:' if prefix else '') + path_for_body]

        if ip_range:
            if isinstance(ip_range, bytes):
                try:
                    ip_range = ip_range.decode('utf-8')
                except UnicodeDecodeError:
                    raise ValueError(
                        'ip_range must be representable as UTF-8'
                    )
            hmac_parts.insert(0, "ip=%s" % ip_range)

        hmac_body = u'\n'.join(hmac_parts)

        temp_url_key = self._check_temp_url_key(temp_url_key=temp_url_key)

        sig = hmac.new(temp_url_key, hmac_body.encode('utf-8'),
                       sha1).hexdigest()

        if iso8601:
            expiration = time.strftime(
                EXPIRES_ISO8601_FORMAT, time.gmtime(expiration))

        temp_url = u'{path}?temp_url_sig={sig}&temp_url_expires={exp}'.format(
            path=path_for_body, sig=sig, exp=expiration)

        if ip_range:
            temp_url += u'&temp_url_ip_range={}'.format(ip_range)

        if prefix:
            temp_url += u'&temp_url_prefix={}'.format(parts[4])
        # Have return type match path from caller
        if isinstance(path, bytes):
            return temp_url.encode('utf-8')
        else:
            return temp_url
