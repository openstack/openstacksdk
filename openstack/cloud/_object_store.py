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

import concurrent.futures
import urllib.parse
import warnings

import keystoneauth1.exceptions

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import warnings as os_warnings


OBJECT_CONTAINER_ACLS = {
    'public': '.r:*,.rlistings',
    'private': '',
}


class ObjectStoreCloudMixin(openstackcloud._OpenStackCloudMixin):
    def list_containers(self, full_listing=None, prefix=None):
        """List containers.

        :param full_listing: Ignored. Present for backwards compat
        :param prefix: Only objects with this prefix will be returned.
            (optional)
        :returns: A list of object store ``Container`` objects.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if full_listing is not None:
            warnings.warn(
                "The 'full_listing' field is unnecessary and will be removed "
                "in a future release.",
                os_warnings.RemovedInSDK60Warning,
            )
        return list(self.object_store.containers(prefix=prefix))

    def search_containers(self, name=None, filters=None):
        """Search containers.

        :param string name: Container name.
        :param filters: A dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of object store ``Container`` objects matching the
            search criteria.
        :raises: :class:`~openstack.exceptions.SDKException`: If something goes
            wrong during the OpenStack API call.
        """
        containers = self.list_containers()
        return _utils._filter_list(containers, name, filters)

    # TODO(stephenfin): Remove 'skip_cache' as it no longer does anything
    def get_container(self, name, skip_cache=False):
        """Get metadata about a container.

        :param str name:
            Name of the container to get metadata for.
        :param bool skip_cache: Ignored. Present for backwards compatibility.
        :returns: An object store ``Container`` object if found, else None.
        """
        try:
            return self.object_store.get_container_metadata(name)
        except exceptions.HttpException as ex:
            if ex.response.status_code == 404:
                return None
            raise

    def create_container(self, name, public=False):
        """Create an object-store container.

        :param str name: Name of the container to create.
        :param bool public: Whether to set this container to be public.
            Defaults to ``False``.
        :returns: The created object store ``Container`` object.
        """
        container = self.get_container(name)
        if container:
            return container
        attrs = dict(name=name)
        if public:
            attrs['read_ACL'] = OBJECT_CONTAINER_ACLS['public']
        container = self.object_store.create_container(**attrs)
        return self.get_container(name, skip_cache=True)

    def delete_container(self, name):
        """Delete an object-store container.

        :param str name: Name of the container to delete.
        """
        try:
            self.object_store.delete_container(name, ignore_missing=False)
            return True
        except exceptions.NotFoundException:
            return False
        except exceptions.ConflictException:
            raise exceptions.SDKException(
                f'Attempt to delete container {name} failed. The '
                f'container is not empty. Please delete the objects '
                f'inside it before deleting the container'
            )

    def update_container(self, name, headers):
        """Update the metadata in a container.

        :param str name: Name of the container to update.
        :param dict headers: Key/Value headers to set on the container.
        """
        self.object_store.set_container_metadata(
            name, refresh=False, **headers
        )

    def set_container_access(self, name, access, refresh=False):
        """Set the access control list on a container.

        :param str name: Name of the container.
        :param str access: ACL string to set on the container. Can also be
            ``public`` or ``private`` which will be translated into appropriate
            ACL strings.
        :param refresh: Flag to trigger refresh of the container properties
        """
        if access not in OBJECT_CONTAINER_ACLS:
            raise exceptions.SDKException(
                f"Invalid container access specified: {access}. "
                f"Must be one of {list(OBJECT_CONTAINER_ACLS.keys())}"
            )
        return self.object_store.set_container_metadata(
            name, read_ACL=OBJECT_CONTAINER_ACLS[access], refresh=refresh
        )

    def get_container_access(self, name):
        """Get the control list from a container.

        :param str name: Name of the container.
        :returns: The contol list for the container.
        :raises: :class:`~openstack.exceptions.SDKException` if the container
            was not found or container access could not be determined.
        """
        container = self.get_container(name, skip_cache=True)
        if not container:
            raise exceptions.SDKException(f"Container not found: {name}")
        acl = container.read_ACL or ''
        for key, value in OBJECT_CONTAINER_ACLS.items():
            # Convert to string for the comparison because swiftclient
            # returns byte values as bytes sometimes and apparently ==
            # on bytes doesn't work like you'd think
            if str(acl) == str(value):
                return key
        raise exceptions.SDKException(
            f"Could not determine container access for ACL: {acl}."
        )

    def get_object_capabilities(self):
        """Get infomation about the object-storage service

        The object-storage service publishes a set of capabilities that
        include metadata about maximum values and thresholds.

        :returns: An object store ``Info`` object.
        """
        return self.object_store.get_info()

    def get_object_segment_size(self, segment_size):
        """Get a segment size that will work given capabilities.

        :param segment_size:
        :returns: A segment size.
        """
        return self.object_store.get_object_segment_size(segment_size)

    def is_object_stale(
        self, container, name, filename, file_md5=None, file_sha256=None
    ):
        """Check to see if an object matches the hashes of a file.

        :param container: Name of the container.
        :param name: Name of the object.
        :param filename: Path to the file.
        :param file_md5: Pre-calculated md5 of the file contents. Defaults to
            None which means calculate locally.
        :param file_sha256: Pre-calculated sha256 of the file contents.
            Defaults to None which means calculate locally.
        """
        return self.object_store.is_object_stale(
            container,
            name,
            filename,
            file_md5=file_md5,
            file_sha256=file_sha256,
        )

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
        :returns: The created object store ``Object`` object.
        """
        headers['content-type'] = 'application/directory'

        return self.create_object(
            container, name, data='', generate_checksums=False, **headers
        )

    def create_object(
        self,
        container,
        name,
        filename=None,
        md5=None,
        sha256=None,
        segment_size=None,
        use_slo=True,
        metadata=None,
        generate_checksums=None,
        data=None,
        **headers,
    ):
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

        :returns: The created object store ``Object`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        return self.object_store.create_object(
            container,
            name,
            filename=filename,
            data=data,
            md5=md5,
            sha256=sha256,
            use_slo=use_slo,
            generate_checksums=generate_checksums,
            metadata=metadata,
            **headers,
        )

    def update_object(self, container, name, metadata=None, **headers):
        """Update the metadata of an object

        :param container: The name of the container the object is in
        :param name: Name for the object within the container.
        :param metadata: This dict will get changed into headers that set
            metadata of the object
        :param headers: These will be passed through to the object update
            API as HTTP Headers.

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        meta = metadata.copy() or {}
        meta.update(**headers)
        self.object_store.set_object_metadata(name, container, **meta)

    def list_objects(self, container, full_listing=True, prefix=None):
        """List objects.

        :param container: Name of the container to list objects in.
        :param full_listing: Ignored. Present for backwards compat
        :param prefix: Only objects with this prefix will be returned.
            (optional)

        :returns: A list of object store ``Object`` objects.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        return list(
            self.object_store.objects(container=container, prefix=prefix)
        )

    def search_objects(self, container, name=None, filters=None):
        """Search objects.

        :param string name: Object name.
        :param filters: A dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of object store ``Object`` objects matching the
            search criteria.
        :raises: :class:`~openstack.exceptions.SDKException`: If something goes
            wrong during the OpenStack API call.
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
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        try:
            self.object_store.delete_object(
                name,
                ignore_missing=False,
                container=container,
            )
            return True
        except exceptions.SDKException:
            return False

    def delete_autocreated_image_objects(
        self,
        container=None,
        segment_prefix=None,
    ):
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
        :returns: True if deletion was successful, else False.
        """
        return self.object_store._delete_autocreated_image_objects(
            container, segment_prefix=segment_prefix
        )

    def get_object_metadata(self, container, name):
        """Get object metadata.

        :param container:
        :param name:
        :returns: The object metadata.
        """
        return self.object_store.get_object_metadata(name, container).metadata

    def get_object_raw(self, container, obj, query_string=None, stream=False):
        """Get a raw response object for an object.

        :param string container: Name of the container.
        :param string obj: Name of the object.
        :param string query_string: Query args for uri. (delimiter, prefix,
            etc.)
        :param bool stream: Whether to stream the response or not.

        :returns: A `requests.Response`
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        endpoint = self._get_object_endpoint(container, obj, query_string)
        return self.object_store.get(endpoint, stream=stream)

    def _get_object_endpoint(self, container, obj=None, query_string=None):
        endpoint = urllib.parse.quote(container)
        if obj:
            endpoint = f'{endpoint}/{urllib.parse.quote(obj)}'
        if query_string:
            endpoint = f'{endpoint}?{query_string}'
        return endpoint

    def stream_object(
        self,
        container,
        obj,
        query_string=None,
        resp_chunk_size=1024,
    ):
        """Download the content via a streaming iterator.

        :param string container: Name of the container.
        :param string obj: Name of the object.
        :param string query_string: Query args for uri. (delimiter, prefix,
            etc.)
        :param int resp_chunk_size: Chunk size of data to read. Only used if
            the results are

        :returns: An iterator over the content or None if the object is not
            found.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        try:
            yield from self.object_store.stream_object(
                obj, container, chunk_size=resp_chunk_size
            )
        except exceptions.NotFoundException:
            return

    def get_object(
        self,
        container,
        obj,
        query_string=None,
        resp_chunk_size=1024,
        outfile=None,
        stream=False,
    ):
        """Get the headers and body of an object

        :param string container: Name of the container.
        :param string obj: Name of the object.
        :param string query_string: Query args for uri. (delimiter, prefix,
            etc.)
        :param int resp_chunk_size: Chunk size of data to read. Only used if
            the results are being written to a file or stream is True.
            (optional, defaults to 1k)
        :param outfile: Write the object to a file instead of returning the
            contents. If this option is given, body in the return tuple will be
            None. outfile can either be a file path given as a string, or a
            File like object.

        :returns: Tuple (headers, body) of the object, or None if the object
            is not found (404).
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        try:
            obj = self.object_store.get_object(
                obj,
                container=container,
                resp_chunk_size=resp_chunk_size,
                outfile=outfile,
                remember_content=(outfile is None),
            )
            headers = {k.lower(): v for k, v in obj._last_headers.items()}
            return (headers, obj.data)

        except exceptions.NotFoundException:
            return None

    def _wait_for_futures(self, futures, raise_on_error=True):
        """Collect results or failures from a list of running future tasks."""
        results = []
        retries = []

        # Check on each result as its thread finishes
        for completed in concurrent.futures.as_completed(futures):
            try:
                result = completed.result()
                exceptions.raise_from_response(result)
                results.append(result)
            except (
                keystoneauth1.exceptions.RetriableConnectionFailure,
                exceptions.HttpException,
            ) as e:
                error_text = f"Exception processing async task: {str(e)}"
                if raise_on_error:
                    self.log.exception(error_text)
                    raise
                else:
                    self.log.debug(error_text)
                # If we get an exception, put the result into a list so we
                # can try again
                retries.append(completed.result())
        return results, retries
