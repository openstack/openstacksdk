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

from openstack.map_reduce.v1 import cluster as _cluster
from openstack.map_reduce.v1 import data_source as _ds
from openstack.map_reduce.v1 import job as _job
from openstack.map_reduce.v1 import job_binary as _jb
from openstack.map_reduce.v1 import job_exe as _exe
from openstack.map_reduce.v1 import job_execution as _execution
from openstack import proxy2


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

    def update_job_binary(self, job_binary, **attrs):
        """Update an exists job-binary from attributes

        :param job_binary: value can be the ID of a Job-Binary or an instance
            of :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        :param dict attrs: Keyword arguments which will be used to create
                a :class: `~openstack.map_reduce.v1.job_binary.JobBinary`
                comprised of the properties on the DataSource class.
        :returns: The results of data_source creation
        :rtype: :class:`~openstack.map_reduce.v1.job_binary.JobBinary`
        """
        return self._update(_jb.JobBinary, job_binary, prepend_key=False,
                            **attrs)

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

    def jobs(self, **query):
        """Retrieve a generator of jobs

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``sort_by``: sort by attribute, sort_by=name means sort by name
                    attribute asc, sort_by=-name means desc
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of jobs (:class:
                `~openstack.map_reduce.v1.job.Job`) instances
        """
        return self._list(_job.Job, paginated=True, **query)

    def exe_job(self, **job_exe):
        """Submit job and exe it (backward compatibility)

        :param dict job_exe: Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.cluster.ExecutableJob`,
                comprised of the properties on the Job class.
        :returns: Job Exe Instance
        :rtype: :class:`~openstack.map_reduce.v1.job_exe.JobExe`
        """
        exe = _exe.JobExe(**job_exe)
        return exe.execute(self._session)

    def create_job(self, **attrs):
        """Create a new Job from attributes

        :param dict attrs: Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.job.Job`,
                comprised of the properties on the Job class.
        :returns: The results of Job creation
        :rtype: :class:`~openstack.map_reduce.v1.job.Job`
        """
        return self._create(_job.Job, prepend_key=False, **attrs)

    def update_job(self, job, **attrs):
        """Update an exists job-binary from attributes

        :param job: value can be the ID of a Job or an instance
            of :class:`~openstack.map_reduce.v1.job.Job`
        :param dict attrs: Keyword arguments which will be used to create
                a :class: `~openstack.map_reduce.v1.job.Job`
                comprised of the properties on the DataSource class.
        :returns: The results of data_source creation
        :rtype: :class:`~openstack.map_reduce.v1.job.Job`
        """
        return self._update(_job.Job, job, prepend_key=False,
                            **attrs)

    def get_job(self, job):
        """Get a Job

        :param job: value can be the ID of a Job or an instance
            of :class:`~openstack.map_reduce.v1.job.Job`
        :returns: Job instance
        :rtype: :class:`~openstack.map_reduce.v1.job.Job`
        """
        return self._get(_job.Job, job)

    def execute_job(self, job, **job_execution):
        """Execute a Job

        :param job: value can be the ID of a Job or an instance
            of :class:`~openstack.map_reduce.v1.job.Job`
        :returns: Job Execution Instance
        :rtype: :class:`~openstack.map_reduce.v1.job_execution.JobExecution`
        """
        job = self._get_resource(_job.Job, job)
        execution = _execution.JobExecution(job_id=job.id, **job_execution)
        return execution.create(self._session)

    def delete_job(self, job, ignore_missing=True):
        """Delete a Job

        :param job: value can be the ID of a Job or an instance
            of :class:`~openstack.map_reduce.v1.job.Job`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the job does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent job.

        :returns: Job been deleted
        :rtype: :class:`~openstack.map_reduce.v1.job.Job`
        """
        return self._delete(_job.Job,
                            job,
                            ignore_missing=ignore_missing)

    def find_job(self, name_or_id, ignore_missing=True):
        """Find a single Job

        :param name_or_id: The name or ID of a Job
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the job does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent job.

        :returns: ``None``
        """
        return self._find(_job.Job,
                          name_or_id,
                          ignore_missing=ignore_missing)

    def job_executions(self, **query):
        """Retrieve a generator of Job-Executions

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``sort_by``: sort by attribute, sort_by=name means sort by name
                    attribute asc, sort_by=-name means desc
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of Job-Executions (:class: `~openstack.
            map_reduce.v1.job_execution.JobExecution`) instances
        """
        return self._list(_execution.JobExecution, paginated=True, **query)

    def get_job_execution(self, job_execution):
        """Get a Job-Executions

        :param job_execution: value can be the ID of a JobExecution or an
                instance of :class:`~openstack.map_reduce.v1.
                job_execution.JobExecution`
        :returns: JobExecution instance
        :rtype: :class:`~openstack.map_reduce.v1.job_execution.JobExecution`
        """
        return self._get(_execution.JobExecution, job_execution)

    def delete_job_execution(self, job_execution, ignore_missing=True):
        """Delete a JobExecution

        :param job_execution: value can be the ID of a JobExecution or an
                instance of :class:`~openstack.map_reduce.v1.
                job_execution.JobExecution`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the job does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent job.

        :returns: JobExecution been deleted
        :rtype: :class:`~openstack.map_reduce.v1.job_execution.JobExecution`
        """
        return self._delete(_execution.JobExecution,
                            job_execution,
                            ignore_missing=ignore_missing)

    def cancel_job_execution(self, job_execution):
        """Cancel a JobExecution

        :param job_execution: value can be the ID of a JobExecution or an
                instance of :class:`~openstack.map_reduce.v1.
                job_execution.JobExecution`

        :returns: JobExecution been cancel
        :rtype: :class:`~openstack.map_reduce.v1.job_execution.JobExecution`
        """
        execution = self._get_resource(_execution.JobExecution, job_execution)
        return execution.cancel(self._session)

    def find_job_execution(self, name_or_id, ignore_missing=True):
        """Find a single JobExecution

        :param name_or_id: The name or ID of a JobExecution
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the job does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent job-execution.

        :returns: Job-Execution instance or None
        :rtype: :class:`~openstack.map_reduce.v1.job_execution.JobExecution`
        """
        return self._find(_execution.JobExecution,
                          name_or_id,
                          ignore_missing=ignore_missing)

    def job_exes(self, **query):
        """Retrieve a generator of Job-Exes

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``sort_by``: sort by attribute, sort_by=name means sort by name
                    attribute asc, sort_by=-name means desc
            * ``id``:  job execution id
            * ``job_name``:  job name
            * ``cluster_id``:  cluster of the execution run on
            * ``state``:  job execution state, includes: -1: Terminated,
                1: Starting, 2: Running, 3: Completed, 4: Abnormal, 5: Error
            * ``page_size``:  pagination size
            * ``current_page``: pagination number

        :returns: A generator of Job-Exe
            (:class: `~openstack.map_reduce.v1.job_exe.JobExe`) instances
        """
        return self._list(_exe.JobExe, paginated=True, **query)

    def get_job_exe(self, job_exe):
        """Get a Job-Exe

        :param job_exe: value can be the ID of a JobExe or an
                instance of :class:`~openstack.map_reduce.v1.job_exe.JobExe`
        :returns: JobExe instance
        :rtype: :class:`~openstack.map_reduce.v1.job_execution.JobExe`
        """
        return self._get(_exe.JobExe, job_exe)

    def create_cluster_and_run_job(self, cluster, job):
        """Create a new cluster and run a job on the created cluster

        :param dict cluster:  Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.cluster.Cluster`,
                comprised of the properties on the Cluster class.
        :param dict job:  Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.cluster.ExecutableJob`,
                comprised of the properties on the ExecutableJob class.
        :return:
        """
        instance = _cluster.ClusterInfo.new(**dict(cluster))
        return instance.create_and_run(self._session, job)

    def reduce_cluster(self, cluster, amount, includes=[], excludes=[]):
        """Reduce node amount of the cluster

        :param cluster: value can be the ID of a cluster or an instance
            of :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        :param amount: the node amount to reduce
        :param includes: instance id list which should be reduced
        :param excludes: instance id list which should be excluded

        :returns: Cluster been reduced
        :rtype: :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        """
        # in case of user pass ClusterInfo as cluster
        if isinstance(cluster, _cluster.Cluster):
            cluster = _cluster.ClusterInfo(id=cluster.id)
        cluster_info = self._get_resource(_cluster.ClusterInfo, cluster)
        return cluster_info.reduce(self._session, amount, includes, excludes)

    def expand_cluster(self, cluster, amount):
        """Reduce node amount of the cluster

        :param cluster: value can be the ID of a cluster or an instance
            of :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        :param amount: the node amount to expand

        :returns: Cluster been expand
        :rtype: :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        """
        # in case of user pass ClusterInfo as cluster
        if isinstance(cluster, _cluster.Cluster):
            cluster = _cluster.ClusterInfo(id=cluster.id)
        cluster_info = self._get_resource(_cluster.ClusterInfo, cluster)
        return cluster_info.expand(self._session, amount)

    def get_cluster(self, cluster):
        """Get a cluster details

        :param cluster: value can be the ID of a cluster or an instance
            of :class:`~openstack.map_reduce.v1.cluster.ClusterDetail`
        :returns: Cluster Detail instance
        :rtype: :class:`~openstack.map_reduce.v1.cluster.ClusterDetail`
        """
        return self._get(_cluster.ClusterDetail, cluster)

    def delete_cluster(self, cluster, ignore_missing=True):
        """Delete a cluster

        :param cluster: value can be the ID of a cluster or an instance
            of :class:`~openstack.map_reduce.v1.cluster.Cluster`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the cluster does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent cluster.

        :returns: Cluster been deleted
        :rtype: :class:`~openstack.map_reduce.v1.cluster.Cluster`
        """
        # in case of user pass ClusterInfo as cluster
        if isinstance(cluster, _cluster.ClusterInfo):
            cluster = cluster.id
        if isinstance(cluster, _cluster.ClusterDetail):
            cluster = cluster.id
        return self._delete(_cluster.Cluster,
                            cluster,
                            ignore_missing=ignore_missing)
