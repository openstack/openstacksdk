# Generated file, to change, run tools/print-services.py
from openstack import service_description
from openstack.baremetal import baremetal_service
from openstack.baremetal_introspection import baremetal_introspection_service
from openstack.block_storage import block_storage_service
from openstack.clustering import clustering_service
from openstack.compute import compute_service
from openstack.database import database_service
from openstack.dns import dns_service
from openstack.identity import identity_service
from openstack.image import image_service
from openstack.instance_ha import instance_ha_service
from openstack.key_manager import key_manager_service
from openstack.load_balancer import load_balancer_service
from openstack.message import message_service
from openstack.network import network_service
from openstack.object_store import object_store_service
from openstack.orchestration import orchestration_service
from openstack.workflow import workflow_service


class ServicesMixin(object):

    identity = identity_service.IdentityService(service_type='identity')

    compute = compute_service.ComputeService(service_type='compute')

    image = image_service.ImageService(service_type='image')

    load_balancer = load_balancer_service.LoadBalancerService(service_type='load-balancer')

    object_store = object_store_service.ObjectStoreService(service_type='object-store')

    clustering = clustering_service.ClusteringService(service_type='clustering')
    resource_cluster = clustering
    cluster = clustering

    data_processing = service_description.ServiceDescription(service_type='data-processing')

    baremetal = baremetal_service.BaremetalService(service_type='baremetal')
    bare_metal = baremetal

    baremetal_introspection = baremetal_introspection_service.BaremetalIntrospectionService(service_type='baremetal-introspection')

    key_manager = key_manager_service.KeyManagerService(service_type='key-manager')

    resource_optimization = service_description.ServiceDescription(service_type='resource-optimization')
    infra_optim = resource_optimization

    message = message_service.MessageService(service_type='message')
    messaging = message

    application_catalog = service_description.ServiceDescription(service_type='application-catalog')

    container_infrastructure_management = service_description.ServiceDescription(service_type='container-infrastructure-management')
    container_infrastructure = container_infrastructure_management
    container_infra = container_infrastructure_management

    search = service_description.ServiceDescription(service_type='search')

    dns = dns_service.DnsService(service_type='dns')

    workflow = workflow_service.WorkflowService(service_type='workflow')

    rating = service_description.ServiceDescription(service_type='rating')

    operator_policy = service_description.ServiceDescription(service_type='operator-policy')
    policy = operator_policy

    shared_file_system = service_description.ServiceDescription(service_type='shared-file-system')
    share = shared_file_system

    data_protection_orchestration = service_description.ServiceDescription(service_type='data-protection-orchestration')

    orchestration = orchestration_service.OrchestrationService(service_type='orchestration')

    block_storage = block_storage_service.BlockStorageService(service_type='block-storage')
    block_store = block_storage
    volume = block_storage

    alarm = service_description.ServiceDescription(service_type='alarm')
    alarming = alarm

    meter = service_description.ServiceDescription(service_type='meter')
    metering = meter
    telemetry = meter

    event = service_description.ServiceDescription(service_type='event')
    events = event

    application_deployment = service_description.ServiceDescription(service_type='application-deployment')
    application_deployment = application_deployment

    multi_region_network_automation = service_description.ServiceDescription(service_type='multi-region-network-automation')
    tricircle = multi_region_network_automation

    database = database_service.DatabaseService(service_type='database')

    application_container = service_description.ServiceDescription(service_type='application-container')
    container = application_container

    root_cause_analysis = service_description.ServiceDescription(service_type='root-cause-analysis')
    rca = root_cause_analysis

    nfv_orchestration = service_description.ServiceDescription(service_type='nfv-orchestration')

    network = network_service.NetworkService(service_type='network')

    backup = service_description.ServiceDescription(service_type='backup')

    monitoring_logging = service_description.ServiceDescription(service_type='monitoring-logging')
    monitoring_log_api = monitoring_logging

    monitoring = service_description.ServiceDescription(service_type='monitoring')

    monitoring_events = service_description.ServiceDescription(service_type='monitoring-events')

    placement = service_description.ServiceDescription(service_type='placement')

    instance_ha = instance_ha_service.InstanceHaService(service_type='instance-ha')
    ha = instance_ha

    reservation = service_description.ServiceDescription(service_type='reservation')

    function_engine = service_description.ServiceDescription(service_type='function-engine')

    accelerator = service_description.ServiceDescription(service_type='accelerator')

    admin_logic = service_description.ServiceDescription(service_type='admin-logic')
    registration = admin_logic

