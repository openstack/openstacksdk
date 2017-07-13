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
from openstack import resource2 as resource
from openstack import utils
from openstack.map_reduce import map_reduce_service


class Component(resource.Resource):
    """Cluster Component Resource"""
    id = resource.Body("component_id")
    name = resource.Body("component_name")
    version = resource.Body("component_version")
    desc = resource.Body("component_desc")


class ExecutableJob(resource.Resource):
    """Executable Job

    The executable job indicates for a job and job-execution(I do not know why
    the attributes is so different with job and job-execution...)
    """

    #: Properties
    #: Job name
    job_name = resource.Body("job_name")
    #: Job type, supports: ``MapReduce``, ``Spark``, ``Hive``, ``hql``,
    #: ``DistCp``, ``SparkScript``, ``SparkSql``
    job_type = resource.Body("job_type")
    #: Path of the .jar package or .sql file for job execution
    jar_path = resource.Body("jar_path")
    #: Key parameter for job execution
    arguments = resource.Body("arguments")
    #: Path for inputting data which must start with ``/`` or ``s3a://``
    input = resource.Body("input")
    #: Path for outputting data, which must start with / or s3a://
    output = resource.Body("output")
    #: Path for storing job logs that record job running status.
    #: This path must start with / or s3a://
    job_log = resource.Body("job_log")
    #: Whether to delete the cluster after the jobs are complete
    shutdown_cluster = resource.Body("shutdown_cluster")
    #: Data import and export
    file_action = resource.Body("file_action")
    #: whether to submit the job when the cluster is ready.
    submit_job_once_cluster_run = resource.Body(
        "submit_job_once_cluster_run", type=bool)
    #: HiveQL statement
    hql = resource.Body("hql")
    #: SQL program path
    hive_script_path = resource.Body("hive_script_path")
    #: the cluster this job run on
    cluster_id = resource.Body("cluster_id")
    #: Reserved attribute, is data-source protected
    is_protected = resource.Body("is_protected", type=bool)
    #: Reserved attribute, is data-source public
    is_public = resource.Body("is_public", type=bool)


class Cluster(resource.Resource):
    """Cluster Resource"""
    resource_key = "cluster"
    resources_key = "cluster"
    base_path = "/clusters"
    service = map_reduce_service.MapReduceService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "sort_by"
    )

    #: Properties
    #: Cluster ID
    id = resource.Body("cluster_id")
    #: Cluster name
    name = resource.Body("cluster_name")
    #: Version of the clusters, Currently, MRS 1.2 and MRS 1.3.0 are supported.
    #: The latest version(MRS 1.3.0 for now) of MRS is used by default.
    version = resource.Body("cluster_version")
    #: Cluster type, ``0`` indicate for analysis and ``1`` for streaming.
    #: 0 is used by default.
    type = resource.Body("cluster_type")

    #: Cluster billing type, The value is 12, indicating on-demand payment.
    billing_type = resource.Body("billing_type", type=int, default=12)
    #: Number of Master nodes, set to 2
    master_node_num = resource.Body("master_node_num", type=int, default=2)
    #: The Flavor of Master Node, Best match based on several years of
    #: commissioning experience. MRS supports nine specifications of hosts,
    #: and host specifications are determined by CPUs, memory, and disks.
    #: Master nodes support:
    #:  - c2.4xlarge.linux.mrs,
    #:  - s1.4xlarge.linux.mrs and
    #:  - s1.8xlarge.linux.mrs.
    #: Core nodes of a streaming cluster support:
    #:  - s1.xlarge.linux.mrs,
    #:  - c2.2xlarge.linux.mrs,
    #:  - c2.4xlarge.linux.mrs,
    #:  - s1.4xlarge.linux.mrs,
    #:  - s1.8xlarge.linux.mrs,
    #:  - d1.8xlarge.linux.mrs
    #: Core nodes of an analysis cluster support all specifications above.
    master_node_size = resource.Body("master_node_size")
    #: Number of Core nodes, Value range: 3 to 100
    core_node_num = resource.Body("core_node_num", type=int)
    #: Instance specification of a Core node Configuration method of this
    #: parameter is identical to that of master_node_size.
    core_node_size = resource.Body("core_node_size")

    #: Cluster region information, Obtain the value from
    #: https://docs.otc.t-systems.com/en-us/endpoint/index.html
    data_center = resource.Body("data_center")
    #: ID of an available zone. Obtain the value from
    #: https://docs.otc.t-systems.com/en-us/endpoint/index.html
    availability_zone_id = resource.Body("available_zone_id")

    #: VPC reference of cluster nodes networking
    vpc_id = resource.Body("vpc_id")
    #: Name of the VPC
    vpc_name = resource.Body("vpc")
    #: Subnet reference of cluster nodes networking
    subnet_id = resource.Body("subnet_id")
    #: Name of the subnet
    subnet_name = resource.Body("subnet_name")

    #: Type of volume, ``SATA``, ``SAS`` and ``SSD`` are supported.
    #:  - SATA: common I/O
    #:  - SAS: high-speed I/O
    #:  - SSD: super high-speed I/O
    volume_type = resource.Body("volume_type")
    #: Data volume size of a Core node, Value range: 100 GB to 32000 GB.
    #: Users can add disks to expand storage capacity when creating a cluster.
    #: There are the following scenarios:
    #: - Separation of data storage and computing: Data is stored in the
    #: OBS system. Costs of clusters are relatively low but computing
    #: performance is poor. The clusters can be deleted at any time. It is
    #: recommended when data computing is not frequently performed.
    #: - Integration of data storage and computing: Data is stored in the HDFS
    #: system. Costs of clusters are relatively high but computing performance
    #: is good. The clusters cannot be deleted in a short term.
    #: It is recommended when data computing is frequently performed.
    volume_size = resource.Body("volume_size")
    #: Name of a key pair used to login to the Master node in the cluster.
    keypair = resource.Body("node_public_cert_name")
    #: MRS cluster running mode, ``0`` indicate for ``Common Mode`` and ``1``
    #: for ``Safe Mode``.
    #: - 0 common mode: The value indicates that the Kerberos authentication
    # is disabled. Users can use all functions provided by the cluster.
    #: - 1: safe mode; The value indicates that the Kerberos authentication is
    #: enabled. Common users cannot use the file management or job; management
    #: functions of an MRS cluster and cannot view cluster resource usage or
    # the job records of Hadoop and Spark. To use these functions, the users
    #: must obtain the relevant permissions from the MRS Manager administrator
    safe_mode = resource.Body("safe_mode")
    #: Indicates the password of the MRS Manager administrator.
    cluster_admin_secret = resource.Body("cluster_admin_secret")
    #: Service component list to be used by the cluster.
    #: Component IDs supported by 1.3.0 include:
    #: - MRS 1.3.0_001: Hadoop
    #: - MRS 1.3.0_002: Spark
    #: - MRS 1.3.0_003: HBase
    #: - MRS 1.3.0_004: Hive
    #: - MRS 1.3.0_005: Hue
    #: - MRS 1.3.0_006: Kafka
    #: - MRS 1.3.0_007: Storm
    # Component IDs supported by MRS 1.2 include:
    #: - MRS 1.2_001: Hadoop
    #: - MRS 1.2_002: Spark
    #: - MRS 1.2_003: HBase
    #: - MRS 1.2_004: Hive
    #: - MRS 1.2_005: Hue
    component_list = resource.Body("component_list", type=list)
    #: job to be executed after cluster is ready
    jobs = resource.Body("add_jobs", type=list)


class ClusterInfo(Cluster):
    """HuaWei Cluster extends"""
    base_path = "/cluster_infos"

    def create_and_run(self, session, job):
        """Create a new cluster and run a job on the created cluster

        :param session: the openstack session
        :param dict job:  Keyword arguments which will be used to create
                a :class:`~openstack.map_reduce.v1.cluster.ExecutableJob`,
                comprised of the properties on the ExecutableJob class.
        :return:
        """
        body = dict(self._body.dirty)
        job = ExecutableJob.new(**dict(job))
        body["add_jobs"] = [dict(job._body.dirty)]
        endpoint_override = self.service.get_endpoint_override()
        response = session.post("/run-job-flow",
                                headers={},
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=dict(body))
        self._translate_response(response)
        return self

    def reduce(self, session, amount, includes, excludes):
        """Reduce node amount of the cluster

        :param session: the openstack session
        :param cluster: value can be the ID of a cluster or an instance
            of :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        :param amount: the node amount to expand
        :param includes: instance id list which should be reduced
        :param excludes: instance id list which should be excluded

        :returns: Cluster been expand
        :rtype: :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        """
        uri = utils.urljoin(self.base_path, self.id)
        endpoint_override = self.service.get_endpoint_override()
        body = {
            "service_id": "",
            "plan_id": "",
            "parameters": {
                "order_id": "",
                "scale_type": "scale_in",
                "node_id": "node_orderadd",
                "instances": amount,
                "include_instances": includes,
                "exclude_instances": excludes
            },
            "previous_values": {
                "plan_id": ""
            }
        }

        response = session.put(uri,
                               endpoint_filter=self.service,
                               endpoint_override=endpoint_override,
                               json=body)
        self._translate_response(response)
        return self

    def expand(self, session, amount):
        """Reduce node amount of the cluster

        :param session: the openstack session
        :param cluster: value can be the ID of a cluster or an instance
            of :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        :param amount: the node amount to expand

        :returns: Cluster been expand
        :rtype: :class:`~openstack.map_reduce.v1.cluster.ClusterInfo`
        """
        uri = utils.urljoin(self.base_path, self.id)
        endpoint_override = self.service.get_endpoint_override()
        body = {
            "service_id": "",
            "plan_id": "",
            "parameters": {
                "order_id": "",
                "scale_type": "scale_out",
                "node_id": "node_orderadd",
                "instances": amount,
                "include_instances": [],
                "exclude_instances": []
            },
            "previous_values": {
                "plan_id": ""
            }
        }

        response = session.put(uri,
                               endpoint_filter=self.service,
                               endpoint_override=endpoint_override,
                               json=body)
        self._translate_response(response)
        return self


class ClusterDetail(resource.Resource):
    """Cluster Detail Resource"""
    resource_key = "cluster"
    resources_key = "cluster"
    base_path = "/cluster_infos"
    service = map_reduce_service.MapReduceService()

    # capabilities
    allow_get = True

    #: Properties
    #: Cluster ID
    id = resource.Body("clusterId")
    #: Cluster name
    name = resource.Body("clusterName")
    #: Version of the clusters, Currently, MRS 1.2 and MRS 1.3.0 are supported.
    #: The latest version(MRS 1.3.0 for now) of MRS is used by default.
    version = resource.Body("clusterVersion")
    #: Cluster type, ``0`` indicate for analysis and ``1`` for streaming.
    #: 0 is used by default.
    type = resource.Body("clusterType")
    state = resource.Body("clusterState")

    #: Cluster billing type, The value is 12, indicating on-demand payment.
    billing_type = resource.Body("billingType", default=12)
    #: Number of Master nodes, set to 2
    master_node_num = resource.Body("masterNodeNum", type=int, default=2)
    #: The Flavor of Master Node, Best match based on several years of
    #: commissioning experience. MRS supports nine specifications of hosts,
    #: and host specifications are determined by CPUs, memory, and disks.
    #: Master nodes support:
    #:  - c2.4xlarge.linux.mrs,
    #:  - s1.4xlarge.linux.mrs and
    #:  - s1.8xlarge.linux.mrs.
    #: Core nodes of a streaming cluster support:
    #:  - s1.xlarge.linux.mrs,
    #:  - c2.2xlarge.linux.mrs,
    #:  - c2.4xlarge.linux.mrs,
    #:  - s1.4xlarge.linux.mrs,
    #:  - s1.8xlarge.linux.mrs,
    #:  - d1.8xlarge.linux.mrs
    #: Core nodes of an analysis cluster support all specifications above.
    master_node_size = resource.Body("masterNodeSize")
    #: Number of Core nodes, Value range: 3 to 100
    core_node_num = resource.Body("coreNodeNum", type=int)
    #: Instance specification of a Core node Configuration method of this
    #: parameter is identical to that of master_node_size.
    core_node_size = resource.Body("coreNodeSize")

    #: Cluster region information, Obtain the value from
    #: https://docs.otc.t-systems.com/en-us/endpoint/index.html
    data_center = resource.Body("dataCenter")
    #: ID of an available zone. Obtain the value from
    #: https://docs.otc.t-systems.com/en-us/endpoint/index.html
    availability_zone_id = resource.Body("azId")
    availability_zone = resource.Body("azName")

    #: Name of the VPC
    vpc_name = resource.Body("vpc")
    #: Name of the subnet
    subnet_name = resource.Body("subnetName")

    #: Type of volume, ``SATA``, ``SAS`` and ``SSD`` are supported.
    #:  - SATA: common I/O
    #:  - SAS: high-speed I/O
    #:  - SSD: super high-speed I/O
    volume_type = resource.Body("volumeType")
    #: Data volume size of a Core node, Value range: 100 GB to 32000 GB.
    #: Users can add disks to expand storage capacity when creating a cluster.
    #: There are the following scenarios:
    #: - Separation of data storage and computing: Data is stored in the
    #: OBS system. Costs of clusters are relatively low but computing
    #: performance is poor. The clusters can be deleted at any time. It is
    #: recommended when data computing is not frequently performed.
    #: - Integration of data storage and computing: Data is stored in the HDFS
    #: system. Costs of clusters are relatively high but computing performance
    #: is good. The clusters cannot be deleted in a short term.
    #: It is recommended when data computing is frequently performed.
    volume_size = resource.Body("volumeSize")
    #: Name of a key pair used to login to the Master node in the cluster.
    keypair = resource.Body("nodePublicCertName")
    #: MRS cluster running mode, ``0`` indicate for ``Common Mode`` and ``1``
    #: for ``Safe Mode``.
    #: - 0 common mode: The value indicates that the Kerberos authentication
    # is disabled. Users can use all functions provided by the cluster.
    #: - 1: safe mode; The value indicates that the Kerberos authentication is
    #: enabled. Common users cannot use the file management or job; management
    #: functions of an MRS cluster and cannot view cluster resource usage or
    # the job records of Hadoop and Spark. To use these functions, the users
    #: must obtain the relevant permissions from the MRS Manager administrator
    safe_mode = resource.Body("safeMode")
    #: Service component list to be used by the cluster.
    #: Component IDs supported by 1.3.0 include:
    #: - MRS 1.3.0_001: Hadoop
    #: - MRS 1.3.0_002: Spark
    #: - MRS 1.3.0_003: HBase
    #: - MRS 1.3.0_004: Hive
    #: - MRS 1.3.0_005: Hue
    #: - MRS 1.3.0_006: Kafka
    #: - MRS 1.3.0_007: Storm
    # Component IDs supported by MRS 1.2 include:
    #: - MRS 1.2_001: Hadoop
    #: - MRS 1.2_002: Spark
    #: - MRS 1.2_003: HBase
    #: - MRS 1.2_004: Hive
    #: - MRS 1.2_005: Hue
    component_list = resource.Body("componentList", type=list)

    safe_mode = resource.Body("safeMode")
    create_at = resource.Body("createAt")
    update_at = resource.Body("updateAt")
    duration = resource.Body("duration")
    fee = resource.Body("fee")
    hadoop_version = resource.Body("hadoopVersion")
    external_ip = resource.Body("externalIp")
    external_alternate_ip = resource.Body("externalAlternateIp")
    internal_ip = resource.Body("internalIp")
    deployment_id = resource.Body("deploymentId")
    remark = resource.Body("remark")
    order_id = resource.Body("orderId")
    master_node_product_id = resource.Body("masterNodeProductId")
    master_node_spec_id = resource.Body("masterNodeSpecId")
    core_node_product_id = resource.Body("coreNodeProductId")
    core_node_spec_id = resource.Body("coreNodeSpecId")
    instance_id = resource.Body("instanceId")
    vnc = resource.Body("vnc")
    tenant_id = resource.Body("tenantId")
    security_groups_id = resource.Body("securityGroupsId")
    slave_security_groups_id = resource.Body("slaveSecurityGroupsId")
    master_node_ip = resource.Body("masterNodeIp")
    private_ip_first = resource.Body("privateIpFirst")
    error_info = resource.Body("errorInfo")
    charging_start_time = resource.Body("chargingStartTime")
