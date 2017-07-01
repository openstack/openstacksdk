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

from openstack import proxy2
from openstack.map_reduce.v1 import data_source as _ds
from openstack.map_reduce.v1 import job_binary as _jb


class Proxy(proxy2.BaseProxy):
    def data_sources(self, **query):
        """Retrieve a generator of data-sources

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``sort_by``: sort by attribute, sort_by=name means sort by name
                    attribute asc, sort_by=-name means desc
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of data_source (:class:
                `~openstack.map_reduce.v1.data_source.DataSource`) instances
        """
        return self._list(_ds.DataSource, paginated=True, **query)

    def create_data_source(self, **attrs):
        """Create a new data-source from attributes

        :param dict attrs: Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.data_source.DataSource`,
                comprised of the properties on the DataSource class.
        :returns: The results of data_source creation
        :rtype: :class:`~openstack.map_reduce.v1.data_source.DataSource`
        """
        return self._create(_ds.DataSource, prepend_key=False, **attrs)

    def update_data_source(self, data_source, **attrs):
        """Update an exists data-source from attributes

        :param data_source: value can be the ID of a data_source or an instance
            of :class:`~openstack.map_reduce.v1.data_source.DataSource`
        :param dict attrs: Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.data_source.DataSource`,
                comprised of the properties on the DataSource class.
        :returns: The results of data_source creation
        :rtype: :class:`~openstack.map_reduce.v1.data_source.DataSource`
        """
        return self._update(_ds.DataSource, data_source, prepend_key=False,
                            **attrs)

    def get_data_source(self, data_source):
        """Get a data_source

        :param data_source: value can be the ID of a data_source or an instance
            of :class:`~openstack.map_reduce.v1.data_source.DataSource`
        :returns: DataSource instance
        :rtype: :class:`~openstack.map_reduce.v1.data_source.DataSource`
        """
        return self._get(_ds.DataSource, data_source)

    def delete_data_source(self, data_source, ignore_missing=True):
        """Delete a data_source

        :param data_source: value can be the ID of a data_source or an instance
            of :class:`~openstack.map_reduce.v1.data_source.DataSource`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the data_source does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent data_source.

        :returns: DataSource been deleted
        :rtype: :class:`~openstack.map_reduce.v1.data_source.DataSource`
        """
        return self._delete(_ds.DataSource,
                            data_source,
                            ignore_missing=ignore_missing)

    def find_data_source(self, name_or_id, ignore_missing=True):
        """Find a single data_source

        :param name_or_id: The name or ID of a data_source
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the data_source does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent data_source.

        :returns: ``None``
        """
        return self._find(_ds.DataSource,
                          name_or_id,
                          ignore_missing=ignore_missing)

    def job_binaries(self, **query):
        """Retrieve a generator of job-binaries
        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``sort_by``: sort by attribute, sort_by=name means sort by name
                    attribute asc, sort_by=-name means desc
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of job-binaries (:class:
                `~openstack.map_reduce.v1.job_binary.JobBinary`) instances
        """
        return self._list(_jb.JobBinary, paginated=True, **query)

    def create_job_binary(self, **attrs):
        """Create a new Job-Binary from attributes
        :param dict attrs: Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.job_binary.JobBinary`,
                comprised of the properties on the JobBinary class.
        :returns: The results of Job-Binary creation
        :rtype: :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        """
        return self._create(_jb.JobBinary, prepend_key=False, **attrs)

    def get_job_binary(self, job_binary):
        """Get a Job-Binary
        :param job_binary: value can be the ID of a Job-Binary or an instance
            of :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        :returns: Job-Binary instance
        :rtype: :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        """
        return self._get(_jb.JobBinary, job_binary)

    def delete_job_binary(self, job_binary, ignore_missing=True):
        """Delete a Job-Binary

        :param job_binary: value can be the ID of a Job-Binary or an instance
            of :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the job_binary does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent job_binary.

        :returns: Job-Binary been deleted
        :rtype: :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        """
        return self._delete(_jb.JobBinary,
                            job_binary,
                            ignore_missing=ignore_missing)

    def find_job_binary(self, name_or_id, ignore_missing=True):
        """Find a single Job-Binary

        :param name_or_id: The name or ID of a Job-Binary
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the job_binary does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent job_binary.

        :returns: ``None``
        """
        return self._find(_jb.JobBinary,
                          name_or_id,
                          ignore_missing=ignore_missing)
