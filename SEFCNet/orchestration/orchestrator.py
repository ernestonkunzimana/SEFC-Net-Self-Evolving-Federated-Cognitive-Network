"""
Enterprise-grade orchestration system for distributed federated learning
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
from datetime import datetime
import json

from kubernetes import client, config, watch
from kubernetes.client import ApiException
import ray
from ray import serve
import docker
from prometheus_client import Counter, Gauge, Histogram

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector
from ..core.service_registry import ServiceRegistry
from ..core.framework_integration import FrameworkManager
from ..utils.resilience import CircuitBreaker

logger = get_logger(__name__)

class FederatedOrchestrator:
    """Enterprise-grade federated learning orchestrator"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        k8s_context: Optional[str] = None
    ):
        """Initialize orchestrator"""
        self.config = self._load_config(config_path) if config_path else {}
        self.metrics = MetricsCollector()
        self.service_registry = ServiceRegistry()
        self.framework_manager = FrameworkManager()
        self.circuit_breaker = CircuitBreaker()
        
        # Initialize Kubernetes client
        try:
            if k8s_context:
                config.load_kube_config(context=k8s_context)
            else:
                config.load_incluster_config()
            self.k8s_api = client.CoreV1Api()
            self.k8s_apps_api = client.AppsV1Api()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.warning(f"Kubernetes client initialization failed: {str(e)}")
            self.k8s_api = None
            self.k8s_apps_api = None
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {str(e)}")
            self.docker_client = None
        
        # Initialize Ray
        try:
            ray.init(ignore_reinit_error=True)
            serve.start(detached=True)
            logger.info("Ray initialized")
        except Exception as e:
            logger.warning(f"Ray initialization failed: {str(e)}")
        
        # Metrics
        self.node_gauge = Gauge(
            "federated_nodes_total",
            "Number of federated learning nodes",
            ["status"]
        )
        self.job_counter = Counter(
            "federated_jobs_total",
            "Number of federated learning jobs",
            ["status"]
        )
        self.latency_histogram = Histogram(
            "federated_job_latency_seconds",
            "Federated job latency in seconds"
        )
    
    async def deploy_federation(
        self,
        num_nodes: int,
        framework_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy federated learning infrastructure"""
        try:
            deployment_info = {
                "nodes": [],
                "services": [],
                "status": "deploying"
            }
            
            # Deploy central server
            server_info = await self._deploy_server(framework_config)
            deployment_info["server"] = server_info
            
            # Deploy nodes
            for i in range(num_nodes):
                node_info = await self._deploy_node(
                    node_id=f"node-{i}",
                    framework_config=framework_config
                )
                deployment_info["nodes"].append(node_info)
            
            # Register services
            for node in deployment_info["nodes"]:
                service_id = await self.service_registry.register_service(
                    service_name="federated-node",
                    instance_id=node["node_id"],
                    host=node["host"],
                    port=node["port"]
                )
                deployment_info["services"].append(service_id)
            
            deployment_info["status"] = "deployed"
            logger.info(f"Federation deployed with {num_nodes} nodes")
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Federation deployment failed: {str(e)}")
            raise
    
    async def _deploy_server(
        self,
        framework_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy federated learning server"""
        try:
            if self.k8s_api:
                # Deploy on Kubernetes
                return await self._deploy_k8s_server(framework_config)
            elif self.docker_client:
                # Deploy with Docker
                return await self._deploy_docker_server(framework_config)
            else:
                # Local deployment
                return await self._deploy_local_server(framework_config)
        except Exception as e:
            logger.error(f"Server deployment failed: {str(e)}")
            raise
    
    async def _deploy_node(
        self,
        node_id: str,
        framework_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy federated learning node"""
        try:
            if self.k8s_api:
                # Deploy on Kubernetes
                return await self._deploy_k8s_node(node_id, framework_config)
            elif self.docker_client:
                # Deploy with Docker
                return await self._deploy_docker_node(node_id, framework_config)
            else:
                # Local deployment
                return await self._deploy_local_node(node_id, framework_config)
        except Exception as e:
            logger.error(f"Node deployment failed: {str(e)}")
            raise
    
    async def _deploy_k8s_server(
        self,
        framework_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy server on Kubernetes"""
        try:
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name="federated-server"),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "federated-server"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "federated-server"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="federated-server",
                                    image=framework_config["server_image"],
                                    ports=[
                                        client.V1ContainerPort(
                                            container_port=8080
                                        )
                                    ],
                                    env=[
                                        client.V1EnvVar(
                                            name="CONFIG",
                                            value=json.dumps(framework_config)
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
            
            self.k8s_apps_api.create_namespaced_deployment(
                namespace="default",
                body=deployment
            )
            
            # Create service
            service = client.V1Service(
                metadata=client.V1ObjectMeta(name="federated-server"),
                spec=client.V1ServiceSpec(
                    selector={"app": "federated-server"},
                    ports=[
                        client.V1ServicePort(
                            port=8080,
                            target_port=8080
                        )
                    ]
                )
            )
            
            self.k8s_api.create_namespaced_service(
                namespace="default",
                body=service
            )
            
            return {
                "type": "kubernetes",
                "deployment": "federated-server",
                "service": "federated-server",
                "host": "federated-server.default.svc.cluster.local",
                "port": 8080
            }
            
        except Exception as e:
            logger.error(f"Kubernetes server deployment failed: {str(e)}")
            raise
    
    async def _deploy_k8s_node(
        self,
        node_id: str,
        framework_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy node on Kubernetes"""
        try:
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=f"federated-node-{node_id}"),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": f"federated-node-{node_id}"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": f"federated-node-{node_id}"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=f"federated-node-{node_id}",
                                    image=framework_config["node_image"],
                                    ports=[
                                        client.V1ContainerPort(
                                            container_port=8081
                                        )
                                    ],
                                    env=[
                                        client.V1EnvVar(
                                            name="NODE_ID",
                                            value=node_id
                                        ),
                                        client.V1EnvVar(
                                            name="CONFIG",
                                            value=json.dumps(framework_config)
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
            
            self.k8s_apps_api.create_namespaced_deployment(
                namespace="default",
                body=deployment
            )
            
            # Create service
            service = client.V1Service(
                metadata=client.V1ObjectMeta(name=f"federated-node-{node_id}"),
                spec=client.V1ServiceSpec(
                    selector={"app": f"federated-node-{node_id}"},
                    ports=[
                        client.V1ServicePort(
                            port=8081,
                            target_port=8081
                        )
                    ]
                )
            )
            
            self.k8s_api.create_namespaced_service(
                namespace="default",
                body=service
            )
            
            return {
                "node_id": node_id,
                "type": "kubernetes",
                "deployment": f"federated-node-{node_id}",
                "service": f"federated-node-{node_id}",
                "host": f"federated-node-{node_id}.default.svc.cluster.local",
                "port": 8081
            }
            
        except Exception as e:
            logger.error(f"Kubernetes node deployment failed: {str(e)}")
            raise
    
    async def monitor_federation(self) -> None:
        """Monitor federated learning infrastructure"""
        try:
            while True:
                # Get all services
                services = await self.service_registry.list_services()
                
                healthy_count = 0
                unhealthy_count = 0
                
                for service in services:
                    if service["status"] == "healthy":
                        healthy_count += 1
                    else:
                        unhealthy_count += 1
                
                # Update metrics
                self.node_gauge.labels(status="healthy").set(healthy_count)
                self.node_gauge.labels(status="unhealthy").set(unhealthy_count)
                
                # Check for alerts
                if unhealthy_count > 0:
                    logger.warning(
                        f"{unhealthy_count} nodes are unhealthy"
                    )
                
                await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"Federation monitoring failed: {str(e)}")
            raise
    
    async def scale_federation(
        self,
        target_nodes: int
    ) -> Dict[str, Any]:
        """Scale federated learning infrastructure"""
        try:
            current_nodes = len(await self.service_registry.list_services())
            
            if target_nodes > current_nodes:
                # Scale up
                nodes_to_add = target_nodes - current_nodes
                logger.info(f"Scaling up by {nodes_to_add} nodes")
                
                for i in range(nodes_to_add):
                    node_id = f"node-{current_nodes + i}"
                    await self._deploy_node(
                        node_id=node_id,
                        framework_config=self.config
                    )
            else:
                # Scale down
                nodes_to_remove = current_nodes - target_nodes
                logger.info(f"Scaling down by {nodes_to_remove} nodes")
                
                services = await self.service_registry.list_services()
                for service in services[-nodes_to_remove:]:
                    await self.service_registry.deregister_service(
                        service_name="federated-node",
                        instance_id=service["instance_id"]
                    )
            
            return {
                "previous_nodes": current_nodes,
                "target_nodes": target_nodes,
                "status": "scaled"
            }
            
        except Exception as e:
            logger.error(f"Federation scaling failed: {str(e)}")
            raise