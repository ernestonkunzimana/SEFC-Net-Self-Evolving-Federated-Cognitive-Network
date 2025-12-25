"""
Enterprise-grade infrastructure deployment system
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
import json
from pathlib import Path

import yaml
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import docker
import prometheus_client
from prometheus_api_client import PrometheusConnect

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector
from ..utils.network_utils import validate_network_config

logger = get_logger(__name__)

class InfrastructureManager:
    """Enterprise-grade infrastructure management system"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        environment: str = "production"
    ):
        """Initialize infrastructure manager"""
        self.config = config or {}
        self.environment = environment
        self.metrics = MetricsCollector()
        
        # Initialize clients
        self._init_kubernetes()
        self._init_docker()
        self._init_prometheus()
        
        # Deployment tracking
        self.deployments = {}
        self.services = {}
        
        # Metrics
        self.deployment_gauge = prometheus_client.Gauge(
            "deployment_status",
            "Deployment status by service",
            ["service", "status"]
        )
        self.resource_usage = prometheus_client.Gauge(
            "infrastructure_resource_usage",
            "Resource usage by type",
            ["resource_type", "service"]
        )
    
    def _init_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            config.load_kube_config()
            self.k8s_apps = client.AppsV1Api()
            self.k8s_core = client.CoreV1Api()
            self.k8s_networking = client.NetworkingV1Api()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.error(f"Kubernetes client initialization failed: {str(e)}")
            raise
    
    def _init_docker(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Docker client initialization failed: {str(e)}")
            raise
    
    def _init_prometheus(self):
        """Initialize Prometheus client"""
        try:
            prom_url = self.config.get("prometheus_url", "http://localhost:9090")
            self.prom_client = PrometheusConnect(url=prom_url)
            logger.info("Prometheus client initialized")
        except Exception as e:
            logger.error(f"Prometheus client initialization failed: {str(e)}")
            raise
    
    async def deploy_service(
        self,
        service_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy a service to the infrastructure"""
        try:
            service_name = service_config["name"]
            service_type = service_config["type"]
            
            # Validate config
            self._validate_service_config(service_config)
            
            deployment_result = None
            
            if service_type == "kubernetes":
                deployment_result = await self._deploy_to_kubernetes(
                    service_config
                )
            elif service_type == "docker":
                deployment_result = await self._deploy_to_docker(
                    service_config
                )
            else:
                raise ValueError(f"Unsupported service type: {service_type}")
            
            # Update tracking
            self.deployments[service_name] = deployment_result
            
            # Update metrics
            self.deployment_gauge.labels(
                service=service_name,
                status="active"
            ).set(1)
            
            return deployment_result
            
        except Exception as e:
            logger.error(f"Service deployment failed: {str(e)}")
            if service_name:
                self.deployment_gauge.labels(
                    service=service_name,
                    status="failed"
                ).set(1)
            raise
    
    async def _deploy_to_kubernetes(
        self,
        service_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy service to Kubernetes"""
        try:
            name = service_config["name"]
            image = service_config["image"]
            replicas = service_config.get("replicas", 1)
            
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels={"app": name}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": name}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=name,
                                    image=image
                                )
                            ]
                        )
                    )
                )
            )
            
            # Create deployment
            self.k8s_apps.create_namespaced_deployment(
                body=deployment,
                namespace="default"
            )
            
            # Create service if needed
            if service_config.get("expose", False):
                service = client.V1Service(
                    metadata=client.V1ObjectMeta(name=name),
                    spec=client.V1ServiceSpec(
                        selector={"app": name},
                        ports=[
                            client.V1ServicePort(
                                port=service_config["port"]
                            )
                        ]
                    )
                )
                
                self.k8s_core.create_namespaced_service(
                    body=service,
                    namespace="default"
                )
            
            return {
                "status": "deployed",
                "platform": "kubernetes",
                "name": name
            }
            
        except ApiException as e:
            logger.error(f"Kubernetes deployment failed: {str(e)}")
            raise
    
    async def _deploy_to_docker(
        self,
        service_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy service to Docker"""
        try:
            name = service_config["name"]
            image = service_config["image"]
            
            # Pull image
            self.docker_client.images.pull(image)
            
            # Create container
            container = self.docker_client.containers.run(
                image,
                name=name,
                detach=True,
                ports=service_config.get("ports", {}),
                environment=service_config.get("environment", {})
            )
            
            return {
                "status": "deployed",
                "platform": "docker",
                "name": name,
                "container_id": container.id
            }
            
        except Exception as e:
            logger.error(f"Docker deployment failed: {str(e)}")
            raise
    
    def _validate_service_config(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Validate service configuration"""
        required_fields = ["name", "type", "image"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        if config["type"] not in ["kubernetes", "docker"]:
            raise ValueError(f"Unsupported service type: {config['type']}")
            
class NetworkPolicyManager:
    """Enterprise-grade network policy management"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize network policy manager"""
        self.config = config or {}
        self.metrics = MetricsCollector()
        
        # Initialize Kubernetes client
        config.load_kube_config()
        self.k8s_networking = client.NetworkingV1Api()
        
        # Policy tracking
        self.policies = {}
        
        # Metrics
        self.policy_gauge = prometheus_client.Gauge(
            "network_policy_status",
            "Network policy status",
            ["policy", "status"]
        )
    
    async def apply_policy(
        self,
        policy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply network policy"""
        try:
            policy_name = policy_config["name"]
            
            # Create policy object
            policy = client.V1NetworkPolicy(
                metadata=client.V1ObjectMeta(name=policy_name),
                spec=self._create_policy_spec(policy_config)
            )
            
            # Apply policy
            self.k8s_networking.create_namespaced_network_policy(
                body=policy,
                namespace="default"
            )
            
            # Update tracking
            self.policies[policy_name] = policy_config
            
            # Update metrics
            self.policy_gauge.labels(
                policy=policy_name,
                status="active"
            ).set(1)
            
            return {
                "status": "applied",
                "name": policy_name
            }
            
        except Exception as e:
            logger.error(f"Network policy application failed: {str(e)}")
            if policy_name:
                self.policy_gauge.labels(
                    policy=policy_name,
                    status="failed"
                ).set(1)
            raise
    
    def _create_policy_spec(
        self,
        config: Dict[str, Any]
    ) -> client.V1NetworkPolicySpec:
        """Create network policy specification"""
        return client.V1NetworkPolicySpec(
            pod_selector=client.V1LabelSelector(
                match_labels=config["selector"]
            ),
            ingress=self._create_ingress_rules(
                config.get("ingress", [])
            ),
            egress=self._create_egress_rules(
                config.get("egress", [])
            ),
            policy_types=config.get(
                "policy_types",
                ["Ingress", "Egress"]
            )
        )
    
    def _create_ingress_rules(
        self,
        rules: List[Dict[str, Any]]
    ) -> List[client.V1NetworkPolicyIngressRule]:
        """Create ingress rules"""
        return [
            client.V1NetworkPolicyIngressRule(
                from_=self._create_peer_rules(rule.get("from", [])),
                ports=self._create_port_rules(rule.get("ports", []))
            )
            for rule in rules
        ]
    
    def _create_egress_rules(
        self,
        rules: List[Dict[str, Any]]
    ) -> List[client.V1NetworkPolicyEgressRule]:
        """Create egress rules"""
        return [
            client.V1NetworkPolicyEgressRule(
                to=self._create_peer_rules(rule.get("to", [])),
                ports=self._create_port_rules(rule.get("ports", []))
            )
            for rule in rules
        ]
    
    def _create_peer_rules(
        self,
        peers: List[Dict[str, Any]]
    ) -> List[client.V1NetworkPolicyPeer]:
        """Create peer rules"""
        return [
            client.V1NetworkPolicyPeer(
                ip_block=self._create_ip_block(peer.get("ipBlock")),
                namespace_selector=self._create_label_selector(
                    peer.get("namespaceSelector")
                ),
                pod_selector=self._create_label_selector(
                    peer.get("podSelector")
                )
            )
            for peer in peers
        ]
    
    def _create_port_rules(
        self,
        ports: List[Dict[str, Any]]
    ) -> List[client.V1NetworkPolicyPort]:
        """Create port rules"""
        return [
            client.V1NetworkPolicyPort(
                port=port.get("port"),
                protocol=port.get("protocol", "TCP")
            )
            for port in ports
        ]
    
    def _create_ip_block(
        self,
        ip_block: Optional[Dict[str, Any]]
    ) -> Optional[client.V1IPBlock]:
        """Create IP block"""
        if not ip_block:
            return None
            
        return client.V1IPBlock(
            cidr=ip_block["cidr"],
            except_=ip_block.get("except", [])
        )
    
    def _create_label_selector(
        self,
        selector: Optional[Dict[str, Any]]
    ) -> Optional[client.V1LabelSelector]:
        """Create label selector"""
        if not selector:
            return None
            
        return client.V1LabelSelector(
            match_labels=selector.get("matchLabels", {}),
            match_expressions=[
                client.V1LabelSelectorRequirement(
                    key=exp["key"],
                    operator=exp["operator"],
                    values=exp.get("values", [])
                )
                for exp in selector.get("matchExpressions", [])
            ]
        )