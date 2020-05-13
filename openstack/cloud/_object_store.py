# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import collections
import concurrent.futures
import hashlib
import json
import os
import types  # noqa
import urllib.parse

import keystoneauth1.exceptions

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import exceptions
from openstack import proxy


DEFAULT_OBJECT_SEGMENT_SIZE = 1073741824  # 1GB
# This halves the current default for Swift
DEFAULT_MAX_FILE_SIZE = (5 * 1024 * 1024 * 1024 + 2) / 2


OBJECT_CONTAINER_ACLS = {
    'public': '.r:*,.rlistings',
    'private': '',
}


class ObjectStoreCloudMixin(_normalize.Normalizer):

    @property
    def _object_store_client(self):
        if 'object-store' not in self._raw_clients:
            raw_client = self._get_raw_client('object-store')
            self._raw_clients['object-store'] = raw_client
        return self._raw_clients['object-store']

    def list_containers(self, full_listing=True, prefix=None):
        """List containers.

        :param full_listing: Ignored. Present for backwards compat

        :returns: list of Munch of the container objects

        :raises: OpenStackCloudException on operation error.
        """
        params = dict(format='json', prefix=prefix)
        response = self.object_store.get('/', params=params)
        return self._get_and_munchify(None, proxy._json_response(response))

    def search_containers(self, name=None, filters=None):
        """Search containers.

        :param string name: container name.
        :param filters: a dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of ``munch.Munch`` containing the containers.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        containers = self.list_containers()
        return _utils._filter_list(containers, name, filters)

    def get_container(self, name, skip_cache=False):
        """Get metadata about a container.

        :param str name:
            Name of the container to get metadata for.
        :param bool skip_cache:
            Ignore the cache of container metadata for this container.o
            Defaults to ``False``.
        """
        if skip_cache or name not in self._container_cache:
            try:
                response = self.object_store.head(
                    self._get_object_endpoint(name)
                )
                exceptions.raise_from_response(response)
                self._container_cache[name] = response.headers
            except exc.OpenStackCloudHTTPError as e:
                if e.response.status_code == 404:
                    return None
                raise
        return self._container_cache[name]

    def create_container(self, name, public=False):
        """Create an object-store container.

        :param str name:
            Name of the container to create.
        :param bool public:
            Whether to set this container to be public. Defaults to ``False``.
        """
        container = self.get_container(name)
        if container:
            return container
        exceptions.raise_from_response(self.object_store.put(
            self._get_object_endpoint(name)
        ))
        if public:
            self.set_container_access(name, 'public')
        return self.get_container(name, skip_cache=True)

    def delete_container(self, name):
        """Delete an object-store container.

        :param str name: Name of the container to delete.
        """
        try:
            exceptions.raise_from_response(self.object_store.delete(
                self._get_object_endpoint(name)
            ))
            self._container_cache.pop(name, None)
            return True
        except exc.OpenStackCloudHTTPError as e:
            if e.response.status_code == 404:
                return False
            if e.response.status_code == 409:
                raise exc.OpenStackCloudException(
                    'Attempt to delete container {container} failed. The'
                    ' container is not empty. Please delete the objects'
                    ' inside it before deleting the container'.format(
                        container=name))
            raise

    def update_container(self, name, headers):
        """Update the metadata in a container.

        :param str name:
            Name of the container to create.
        :param dict headers:
            Key/Value headers to set on the container.
        """
        """Update the metadata in a container.

        :param str name:
            Name of the container to update.
        :param dict headers:
            Key/Value headers to set on the container.
        """
        exceptions.raise_from_response(
            self.object_store.post(
                self._get_object_endpoint(name), headers=headers)
        )

    def set_container_access(self, name, access):
        """Set the access control list on a container.

        :param str name:
            Name of the container.
        :param str access:
            ACL string to set on the container. Can also be ``public``
            or ``private`` which will be translated into appropriate ACL
            strings.
        """
        if access not in OBJECT_CONTAINER_ACLS:
            raise exc.OpenStackCloudException(
                "Invalid container access specified: %s.  Must be one of %s"
                % (access, list(OBJECT_CONTAINER_ACLS.keys())))
        header = {'x-container-read': OBJECT_CONTAINER_ACLS[access]}
        self.update_container(name, header)

    def get_container_access(self, name):
        """Get the control list from a container.

        :param str name: Name of the container.
        """
        container = self.get_container(name, skip_cache=True)
        if not container:
            raise exc.OpenStackCloudException("Container not found: %s" % name)
        acl = container.get('x-container-read', '')
        for key, value in OBJECT_CONTAINER_ACLS.items():
            # Convert to string for the comparison because swiftclient
            # returns byte values as bytes sometimes and apparently ==
            # on bytes doesn't work like you'd think
            if str(acl) == str(value):
                return key
        raise exc.OpenStackCloudException(
            "Could not determine container access for ACL: %s." % acl)

    def _get_file_hashes(self, filename):
        file_key = "{filename}:{mtime}".format(
            filename=filename,
            mtime=os.stat(filename).st_mtime)
        if file_key not in self._file_hash_cache:
            self.log.debug(
                'Calculating hashes for %(filename)s', {'filename': filename})
            (md5, sha256) = (None, None)
            with open(filename, 'rb') as file_obj:
                (md5, sha256) = self._calculate_data_hashes(file_obj)
            self._file_hash_cache[file_key] = dict(
                md5=md5, sha256=sha256)
            self.log.debug(
                "Image file %(filename)s md5:%(md5)s sha256:%(sha256)s",
                {'filename': filename,
                 'md5': self._file_hash_cache[file_key]['md5'],
                 'sha256': self._file_hash_cache[file_key]['sha256']})
        return (self._file_hash_cache[file_key]['md5'],
                self._file_hash_cache[file_key]['sha256'])

    def _calculate_data_hashes(self, data):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()

        if hasattr(data, 'read'):
            for chunk in iter(lambda: data.read(8192), b''):
                md5.update(chunk)
                sha256.update(chunk)
        else:
            md5.update(data)
            sha256.update(data)
        return (md5.hexdigest(), sha256.hexdigest())

    @_utils.cache_on_arguments()
    def get_object_capabilities(self):
        """Get infomation about the object-storage service

        The object-storage service publishes a set of capabilities that
        include metadata about maximum values and thresholds.
        """
        # The endpoint in the catalog has version and project-id in it
        # To get capabilities, we have to disassemble and reassemble the URL
        # This logic is taken from swiftclient
        endpoint = urllib.parse.urlparse(self.object_store.get_endpoint())
        url = "{scheme}://{netloc}/info".format(
            scheme=endpoint.scheme, netloc=endpoint.netloc)

        return proxy._json_response(self.object_store.get(url))

    def get_object_segment_size(self, segment_size):
        """Get a segment size that will work given capabilities"""
        if segment_size is None:
            segment_size = DEFAULT_OBJECT_SEGMENT_SIZE
        min_segment_size = 0
        try:
            caps = self.get_object_capabilities()
        except exc.OpenStackCloudHTTPError as e:
            if e.response.status_code in (404, 412):
                server_max_file_size = DEFAULT_MAX_FILE_SIZE
                self.log.info(
                    "Swift capabilities not supported. "
                    "Using default max file size.")
            else:
                raise
        else:
            server_max_file_size = caps.get('swift', {}).get('max_file_size',
                                                             0)
            min_segment_size = caps.get('slo', {}).get('min_segment_size', 0)

        if segment_size > server_max_file_size:
            return server_max_file_size
        if segment_size < min_segment_size:
            return min_segment_size
        return segment_size

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
        metadata = self.get_object_metadata(container, name)
        if not metadata:
            self.log.debug(
                "swift stale check, no object: {container}/{name}".format(
                    container=container, name=name))
            return True

        if not (file_md5 or file_sha256):
            (file_md5, file_sha256) = self._get_file_hashes(filename)
        md5_key = metadata.get(
            self._OBJECT_MD5_KEY, metadata.get(self._SHADE_OBJECT_MD5_KEY, ''))
        sha256_key = metadata.get(
            self._OBJECT_SHA256_KEY, metadata.get(
                self._SHADE_OBJECT_SHA256_KEY, ''))
        up_to_date = self._hashes_up_to_date(
            md5=file_md5, sha256=file_sha256,
            md5_key=md5_key, sha256_key=sha256_key)

        if not up_to_date:
            self.log.debug(
                "swift checksum mismatch: "
                " %(filename)s!=%(container)s/%(name)s",
                {'filename': filename, 'container': container, 'name': name})
            return True

        self.log.debug(
            "swift object up to date: %(container)s/%(name)s",
            {'container': container, 'name': name})
        return False

    def create_directory_marker_object(self, container, name, **headers):
        """Create a zero-byte directory marker object

        .. note::

          This method is not needed in most cases. Modern swift does not
          require directory marker objects. However, some swift installs may
          need these.

        When using swift Static Web and Web Listings to serve static content
        one may need to create a zero-byte object to represent each
        "directory". Doing so allows Web Listings to generate an index of the
        objects inside of it, and allows Static Web to render index.html
        "files" that are "inside" the directory.

        :param container: The name of the container.
        :param name: Name for the directory marker object within the container.
        :param headers: These will be passed through to the object creation
            API as HTTP Headers.
        """
        headers['content-type'] = 'application/directory'

        return self.create_object(
            container,
            name,
            data='',
            generate_checksums=False,
            **headers)

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
            many bytes. (Optional) Shade will attempt to discover the maximum
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
            (md5, sha256) = self._get_file_hashes(filename)
        if md5:
            headers[self._OBJECT_MD5_KEY] = md5 or ''
        if sha256:
            headers[self._OBJECT_SHA256_KEY] = sha256 or ''
        for (k, v) in metadata.items():
            if not k.lower().startswith('x-object-meta-'):
                headers['x-object-meta-' + k] = v
            else:
                headers[k] = v

        endpoint = self._get_object_endpoint(container, name)

        if data is not None:
            self.log.debug(
                "swift uploading data to %(endpoint)s",
                {'endpoint': endpoint})

            return self._upload_object_data(endpoint, data, headers)

        # segment_size gets used as a step value in a range call, so needs
        # to be an int
        if segment_size:
            segment_size = int(segment_size)
        segment_size = self.get_object_segment_size(segment_size)
        file_size = os.path.getsize(filename)

        if self.is_object_stale(container, name, filename, md5, sha256):

            self.log.debug(
                "swift uploading %(filename)s to %(endpoint)s",
                {'filename': filename, 'endpoint': endpoint})

            if file_size <= segment_size:
                self._upload_object(endpoint, filename, headers)
            else:
                self._upload_large_object(
                    endpoint, filename, headers,
                    file_size, segment_size, use_slo)

    def _upload_object_data(self, endpoint, data, headers):
        return proxy._json_response(self.object_store.put(
            endpoint, headers=headers, data=data))

    def _upload_object(self, endpoint, filename, headers):
        return proxy._json_response(self.object_store.put(
            endpoint, headers=headers, data=open(filename, 'rb')))

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

    def _object_name_from_url(self, url):
        '''Get container_name/object_name from the full URL called.

        Remove the Swift endpoint from the front of the URL, and remove
        the leaving / that will leave behind.'''
        endpoint = self.object_store.get_endpoint()
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
            segment_future = self._pool_executor.submit(
                self.object_store.put,
                name, headers=headers, data=segment,
                raise_exc=False)
            segment_futures.append(segment_future)
            # TODO(mordred) Collect etags from results to add to this manifest
            # dict. Then sort the list of dicts by path.
            manifest.append(dict(
                path='/{name}'.format(name=name),
                size_bytes=segment.length))

        # Try once and collect failed results to retry
        segment_results, retry_results = self._wait_for_futures(
            segment_futures, raise_on_error=False)

        self._add_etag_to_manifest(segment_results, manifest)

        for result in retry_results:
            # Grab the FileSegment for the failed upload so we can retry
            name = self._object_name_from_url(result.url)
            segment = segments[name]
            segment.seek(0)
            # Async call to put - schedules execution and returns a future
            segment_future = self._pool_executor.submit(
                self.object_store.put,
                name, headers=headers, data=segment)
            # TODO(mordred) Collect etags from results to add to this manifest
            # dict. Then sort the list of dicts by path.
            retry_futures.append(segment_future)

        # If any segments fail the second time, just throw the error
        segment_results, retry_results = self._wait_for_futures(
            retry_futures, raise_on_error=True)

        self._add_etag_to_manifest(segment_results, manifest)

        # If the final manifest upload fails, remove the segments we've
        # already uploaded.
        try:
            if use_slo:
                return self._finish_large_object_slo(endpoint, headers,
                                                     manifest)
            else:
                return self._finish_large_object_dlo(endpoint, headers)
        except Exception:
            try:
                segment_prefix = endpoint.split('/')[-1]
                self.log.debug(
                    "Failed to upload large object manifest for %s. "
                    "Removing segment uploads.", segment_prefix)
                self.delete_autocreated_image_objects(
                    segment_prefix=segment_prefix)
            except Exception:
                self.log.exception(
                    "Failed to cleanup image objects for %s:",
                    segment_prefix)
            raise

    def _finish_large_object_slo(self, endpoint, headers, manifest):
        # TODO(mordred) send an etag of the manifest, which is the md5sum
        # of the concatenation of the etags of the results
        headers = headers.copy()
        retries = 3
        while True:
            try:
                return self._object_store_client.put(
                    endpoint,
                    params={'multipart-manifest': 'put'},
                    headers=headers, data=json.dumps(manifest))
            except Exception:
                retries -= 1
                if retries == 0:
                    raise

    def _finish_large_object_dlo(self, endpoint, headers):
        headers = headers.copy()
        headers['X-Object-Manifest'] = endpoint
        retries = 3
        while True:
            try:
                return self._object_store_client.put(endpoint, headers=headers)
            except Exception:
                retries -= 1
                if retries == 0:
                    raise

    def update_object(self, container, name, metadata=None, **headers):
        """Update the metadata of an object

        :param container: The name of the container the object is in
        :param name: Name for the object within the container.
        :param metadata: This dict will get changed into headers that set
            metadata of the object
        :param headers: These will be passed through to the object update
            API as HTTP Headers.

        :raises: ``OpenStackCloudException`` on operation error.
        """
        if not metadata:
            metadata = {}

        metadata_headers = {}

        for (k, v) in metadata.items():
            metadata_headers['x-object-meta-' + k] = v

        headers = dict(headers, **metadata_headers)

        return self._object_store_client.post(
            self._get_object_endpoint(container, name),
            headers=headers)

    def list_objects(self, container, full_listing=True, prefix=None):
        """List objects.

        :param container: Name of the container to list objects in.
        :param full_listing: Ignored. Present for backwards compat
        :param string prefix:
            only objects with this prefix will be returned.
            (optional)

        :returns: list of Munch of the objects

        :raises: OpenStackCloudException on operation error.
        """
        params = dict(format='json', prefix=prefix)
        data = self._object_store_client.get(container, params=params)
        return self._get_and_munchify(None, data)

    def search_objects(self, container, name=None, filters=None):
        """Search objects.

        :param string name: object name.
        :param filters: a dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of ``munch.Munch`` containing the objects.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        objects = self.list_objects(container)
        return _utils._filter_list(objects, name, filters)

    def delete_object(self, container, name, meta=None):
        """Delete an object from a container.

        :param string container: Name of the container holding the object.
        :param string name: Name of the object to delete.
        :param dict meta: Metadata for the object in question. (optional, will
                          be fetched if not provided)

        :returns: True if delete succeeded, False if the object was not found.

        :raises: OpenStackCloudException on operation error.
        """
        # TODO(mordred) DELETE for swift returns status in text/plain format
        # like so:
        #   Number Deleted: 15
        #   Number Not Found: 0
        #   Response Body:
        #   Response Status: 200 OK
        #   Errors:
        # We should ultimately do something with that
        try:
            if not meta:
                meta = self.get_object_metadata(container, name)
            if not meta:
                return False
            params = {}
            if meta.get('X-Static-Large-Object', None) == 'True':
                params['multipart-manifest'] = 'delete'
            self._object_store_client.delete(
                self._get_object_endpoint(container, name),
                params=params)
            return True
        except exc.OpenStackCloudHTTPError:
            return False

    def delete_autocreated_image_objects(self, container=None,
                                         segment_prefix=None):
        """Delete all objects autocreated for image uploads.

        This method should generally not be needed, as shade should clean up
        the objects it uses for object-based image creation. If something
        goes wrong and it is found that there are leaked objects, this method
        can be used to delete any objects that shade has created on the user's
        behalf in service of image uploads.

        :param str container: Name of the container. Defaults to 'images'.
        :param str segment_prefix: Prefix for the image segment names to
            delete. If not given, all image upload segments present are
            deleted.
        """
        if container is None:
            container = self._OBJECT_AUTOCREATE_CONTAINER
        # This method only makes sense on clouds that use tasks
        if not self.image_api_use_tasks:
            return False

        deleted = False
        for obj in self.list_objects(container, prefix=segment_prefix):
            meta = self.get_object_metadata(container, obj['name'])
            if meta.get(
                    self._OBJECT_AUTOCREATE_KEY, meta.get(
                        self._SHADE_OBJECT_AUTOCREATE_KEY)) == 'true':
                if self.delete_object(container, obj['name'], meta):
                    deleted = True
        return deleted

    def get_object_metadata(self, container, name):
        try:
            return self._object_store_client.head(
                self._get_object_endpoint(container, name)).headers
        except exc.OpenStackCloudException as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_object_raw(self, container, obj, query_string=None, stream=False):
        """Get a raw response object for an object.

        :param string container: name of the container.
        :param string obj: name of the object.
        :param string query_string:
            query args for uri. (delimiter, prefix, etc.)
        :param bool stream:
            Whether to stream the response or not.

        :returns: A `requests.Response`
        :raises: OpenStackCloudException on operation error.
        """
        endpoint = self._get_object_endpoint(container, obj, query_string)
        return self._object_store_client.get(endpoint, stream=stream)

    def _get_object_endpoint(self, container, obj=None, query_string=None):
        endpoint = urllib.parse.quote(container)
        if obj:
            endpoint = '{endpoint}/{object}'.format(
                endpoint=endpoint,
                object=urllib.parse.quote(obj)
            )
        if query_string:
            endpoint = '{endpoint}?{query_string}'.format(
                endpoint=endpoint, query_string=query_string)
        return endpoint

    def stream_object(
            self, container, obj, query_string=None, resp_chunk_size=1024):
        """Download the content via a streaming iterator.

        :param string container: name of the container.
        :param string obj: name of the object.
        :param string query_string:
            query args for uri. (delimiter, prefix, etc.)
        :param int resp_chunk_size:
            chunk size of data to read. Only used if the results are

        :returns:
            An iterator over the content or None if the object is not found.
        :raises: OpenStackCloudException on operation error.
        """
        try:
            with self.get_object_raw(
                    container, obj, query_string=query_string) as response:
                for ret in response.iter_content(chunk_size=resp_chunk_size):
                    yield ret
        except exc.OpenStackCloudHTTPError as e:
            if e.response.status_code == 404:
                return
            raise

    def get_object(self, container, obj, query_string=None,
                   resp_chunk_size=1024, outfile=None, stream=False):
        """Get the headers and body of an object

        :param string container: name of the container.
        :param string obj: name of the object.
        :param string query_string:
            query args for uri. (delimiter, prefix, etc.)
        :param int resp_chunk_size:
            chunk size of data to read. Only used if the results are
            being written to a file or stream is True.
            (optional, defaults to 1k)
        :param outfile:
            Write the object to a file instead of returning the contents.
            If this option is given, body in the return tuple will be None.
            outfile can either be a file path given as a string, or a
            File like object.

        :returns: Tuple (headers, body) of the object, or None if the object
                  is not found (404).
        :raises: OpenStackCloudException on operation error.
        """
        # TODO(mordred) implement resp_chunk_size
        endpoint = self._get_object_endpoint(container, obj, query_string)
        try:
            get_stream = (outfile is not None)
            with self._object_store_client.get(
                    endpoint, stream=get_stream) as response:
                response_headers = {
                    k.lower(): v for k, v in response.headers.items()}
                if outfile:
                    if isinstance(outfile, str):
                        outfile_handle = open(outfile, 'wb')
                    else:
                        outfile_handle = outfile
                    for chunk in response.iter_content(
                            resp_chunk_size, decode_unicode=False):
                        outfile_handle.write(chunk)
                    if isinstance(outfile, str):
                        outfile_handle.close()
                    else:
                        outfile_handle.flush()
                    return (response_headers, None)
                else:
                    return (response_headers, response.text)
        except exc.OpenStackCloudHTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def _wait_for_futures(self, futures, raise_on_error=True):
        '''Collect results or failures from a list of running future tasks.'''

        results = []
        retries = []

        # Check on each result as its thread finishes
        for completed in concurrent.futures.as_completed(futures):
            try:
                result = completed.result()
                exceptions.raise_from_response(result)
                results.append(result)
            except (keystoneauth1.exceptions.RetriableConnectionFailure,
                    exceptions.HttpException) as e:
                error_text = "Exception processing async task: {}".format(
                    str(e))
                if raise_on_error:
                    self.log.exception(error_text)
                    raise
                else:
                    self.log.debug(error_text)
                # If we get an exception, put the result into a list so we
                # can try again
                retries.append(completed.result())
        return results, retries

    def _hashes_up_to_date(self, md5, sha256, md5_key, sha256_key):
        '''Compare md5 and sha256 hashes for being up to date

        md5 and sha256 are the current values.
        md5_key and sha256_key are the previous values.
        '''
        up_to_date = False
        if md5 and md5_key == md5:
            up_to_date = True
        if sha256 and sha256_key == sha256:
            up_to_date = True
        if md5 and md5_key != md5:
            up_to_date = False
        if sha256 and sha256_key != sha256:
            up_to_date = False
        return up_to_date
