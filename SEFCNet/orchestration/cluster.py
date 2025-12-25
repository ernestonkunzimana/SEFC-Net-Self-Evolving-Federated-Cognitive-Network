"""
Enterprise-grade cluster management system
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
from datetime import datetime

from kubernetes import client, config, watch
import ray
from ray import serve
from prometheus_client import Counter, Gauge, Histogram

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector
from ..core.service_registry import ServiceRegistry

logger = get_logger(__name__)

class ClusterManager:
    """Enterprise-grade cluster management system"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        k8s_context: Optional[str] = None
    ):
        """Initialize cluster manager"""
        self.config = self._load_config(config_path) if config_path else {}
        self.metrics = MetricsCollector()
        self.service_registry = ServiceRegistry()
        
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
        
        # Initialize Ray cluster
        try:
            ray.init(address="auto", ignore_reinit_error=True)
            serve.start(detached=True)
            logger.info("Ray cluster initialized")
        except Exception as e:
            logger.warning(f"Ray cluster initialization failed: {str(e)}")
        
        # Metrics
        self.node_gauge = Gauge(
            "cluster_nodes_total",
            "Number of cluster nodes",
            ["status"]
        )
        self.job_counter = Counter(
            "cluster_jobs_total",
            "Number of cluster jobs",
            ["status"]
        )
        self.resource_gauge = Gauge(
            "cluster_resources",
            "Cluster resource usage",
            ["resource_type"]
        )
    
    async def deploy_cluster(
        self,
        cluster_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy distributed cluster"""
        try:
            deployment_info = {
                "start_time": datetime.now().isoformat(),
                "nodes": [],
                "status": "deploying"
            }
            
            if self.k8s_api:
                # Deploy on Kubernetes
                deployment_info = await self._deploy_k8s_cluster(cluster_config)
            else:
                # Deploy using Ray
                deployment_info = await self._deploy_ray_cluster(cluster_config)
            
            deployment_info["end_time"] = datetime.now().isoformat()
            logger.info("Cluster deployment completed")
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Cluster deployment failed: {str(e)}")
            raise
    
    async def _deploy_k8s_cluster(
        self,
        cluster_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy cluster on Kubernetes"""
        try:
            deployment_info = {
                "type": "kubernetes",
                "nodes": [],
                "services": []
            }
            
            # Deploy master node
            master_deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name="cluster-master"),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "cluster-master"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "cluster-master"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="cluster-master",
                                    image=cluster_config["master_image"],
                                    ports=[
                                        client.V1ContainerPort(
                                            container_port=8000
                                        )
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        requests={
                                            "cpu": "2",
                                            "memory": "4Gi"
                                        },
                                        limits={
                                            "cpu": "4",
                                            "memory": "8Gi"
                                        }
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            self.k8s_apps_api.create_namespaced_deployment(
                namespace="default",
                body=master_deployment
            )
            
            # Deploy worker nodes
            num_workers = cluster_config.get("num_workers", 3)
            
            for i in range(num_workers):
                worker_deployment = client.V1Deployment(
                    metadata=client.V1ObjectMeta(
                        name=f"cluster-worker-{i}"
                    ),
                    spec=client.V1DeploymentSpec(
                        replicas=1,
                        selector=client.V1LabelSelector(
                            match_labels={"app": f"cluster-worker-{i}"}
                        ),
                        template=client.V1PodTemplateSpec(
                            metadata=client.V1ObjectMeta(
                                labels={"app": f"cluster-worker-{i}"}
                            ),
                            spec=client.V1PodSpec(
                                containers=[
                                    client.V1Container(
                                        name=f"cluster-worker-{i}",
                                        image=cluster_config["worker_image"],
                                        ports=[
                                            client.V1ContainerPort(
                                                container_port=8001
                                            )
                                        ],
                                        resources=client.V1ResourceRequirements(
                                            requests={
                                                "cpu": "1",
                                                "memory": "2Gi"
                                            },
                                            limits={
                                                "cpu": "2",
                                                "memory": "4Gi"
                                            }
                                        )
                                    )
                                ]
                            )
                        )
                    )
                )
                
                self.k8s_apps_api.create_namespaced_deployment(
                    namespace="default",
                    body=worker_deployment
                )
                
                deployment_info["nodes"].append({
                    "type": "worker",
                    "id": i,
                    "name": f"cluster-worker-{i}"
                })
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Kubernetes cluster deployment failed: {str(e)}")
            raise
    
    async def _deploy_ray_cluster(
        self,
        cluster_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy cluster using Ray"""
        try:
            deployment_info = {
                "type": "ray",
                "nodes": [],
                "services": []
            }
            
            # Initialize Ray cluster
            ray.init(
                address=cluster_config.get("ray_address", "auto"),
                runtime_env=cluster_config.get("runtime_env", {})
            )
            
            # Deploy Ray Serve applications
            serve.start(detached=True, http_options={"host": "0.0.0.0"})
            
            # Scale cluster
            num_workers = cluster_config.get("num_workers", 3)
            ray.cluster().scale(num_workers)
            
            # Wait for workers to join
            while len(ray.nodes()) < num_workers:
                await asyncio.sleep(1)
            
            # Register services
            for node in ray.nodes():
                service_id = await self.service_registry.register_service(
                    service_name="ray-node",
                    instance_id=node["NodeID"],
                    host=node["NodeManagerAddress"],
                    port=node["NodeManagerPort"]
                )
                deployment_info["services"].append(service_id)
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Ray cluster deployment failed: {str(e)}")
            raise
    
    async def monitor_cluster(self) -> None:
        """Monitor cluster health and resources"""
        try:
            while True:
                if self.k8s_api:
                    # Monitor Kubernetes cluster
                    nodes = self.k8s_api.list_node()
                    
                    ready_nodes = 0
                    total_cpu = 0
                    total_memory = 0
                    
                    for node in nodes.items:
                        # Check node status
                        for condition in node.status.conditions:
                            if condition.type == "Ready":
                                if condition.status == "True":
                                    ready_nodes += 1
                                break
                        
                        # Get resource usage
                        cpu_percent = float(
                            node.status.capacity["cpu"]
                        ) / float(
                            node.status.allocatable["cpu"]
                        ) * 100
                        memory_percent = float(
                            node.status.capacity["memory"].replace("Ki", "")
                        ) / float(
                            node.status.allocatable["memory"].replace("Ki", "")
                        ) * 100
                        
                        total_cpu += cpu_percent
                        total_memory += memory_percent
                    
                    # Update metrics
                    self.node_gauge.labels(status="ready").set(ready_nodes)
                    self.resource_gauge.labels(
                        resource_type="cpu"
                    ).set(total_cpu / len(nodes.items))
                    self.resource_gauge.labels(
                        resource_type="memory"
                    ).set(total_memory / len(nodes.items))
                
                else:
                    # Monitor Ray cluster
                    nodes = ray.nodes()
                    
                    alive_nodes = 0
                    total_cpu = 0
                    total_memory = 0
                    
                    for node in nodes:
                        if node["Alive"]:
                            alive_nodes += 1
                            
                            # Get resource usage
                            resources = node["Resources"]
                            total_cpu += resources.get("CPU", 0)
                            total_memory += resources.get("memory", 0)
                    
                    # Update metrics
                    self.node_gauge.labels(status="alive").set(alive_nodes)
                    self.resource_gauge.labels(
                        resource_type="cpu"
                    ).set(total_cpu)
                    self.resource_gauge.labels(
                        resource_type="memory"
                    ).set(total_memory)
                
                await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"Cluster monitoring failed: {str(e)}")
            raise
    
    async def scale_cluster(
        self,
        target_nodes: int
    ) -> Dict[str, Any]:
        """Scale cluster to target number of nodes"""
        try:
            scaling_info = {
                "start_time": datetime.now().isoformat(),
                "previous_nodes": 0,
                "target_nodes": target_nodes,
                "status": "scaling"
            }
            
            if self.k8s_api:
                # Scale Kubernetes cluster
                current_nodes = len(
                    self.k8s_api.list_node().items
                )
                scaling_info["previous_nodes"] = current_nodes
                
                if target_nodes > current_nodes:
                    # Scale up
                    for i in range(current_nodes, target_nodes):
                        await self._deploy_k8s_node(i)
                else:
                    # Scale down
                    nodes = self.k8s_api.list_node()
                    for node in nodes.items[target_nodes:]:
                        self.k8s_api.delete_node(node.metadata.name)
            
            else:
                # Scale Ray cluster
                current_nodes = len(ray.nodes())
                scaling_info["previous_nodes"] = current_nodes
                
                ray.cluster().scale(target_nodes)
            
            scaling_info["status"] = "scaled"
            scaling_info["end_time"] = datetime.now().isoformat()
            
            return scaling_info
            
        except Exception as e:
            logger.error(f"Cluster scaling failed: {str(e)}")
            raise
    
    async def _deploy_k8s_node(self, node_id: int) -> None:
        """Deploy additional Kubernetes node"""
        try:
            node_config = client.V1Node(
                metadata=client.V1ObjectMeta(
                    name=f"worker-{node_id}"
                ),
                spec=client.V1NodeSpec(
                    taints=[
                        client.V1Taint(
                            effect="NoSchedule",
                            key="node-role.kubernetes.io/master"
                        )
                    ]
                )
            )
            
            self.k8s_api.create_node(body=node_config)
            
        except Exception as e:
            logger.error(f"Node deployment failed: {str(e)}")
            raise