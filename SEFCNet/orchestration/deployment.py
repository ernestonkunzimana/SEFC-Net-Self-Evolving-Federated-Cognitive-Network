"""
Enterprise-grade deployment management system
"""
from typing import Dict, List, Optional, Any, Union
import os
import asyncio
import yaml
import json
from datetime import datetime

import docker
from kubernetes import client, config
import helm
from prometheus_client import Counter, Gauge, Histogram

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector
from ..core.service_registry import ServiceRegistry

logger = get_logger(__name__)

class DeploymentManager:
    """Enterprise-grade deployment manager"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        k8s_context: Optional[str] = None
    ):
        """Initialize deployment manager"""
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
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {str(e)}")
            self.docker_client = None
        
        # Initialize Helm client
        try:
            self.helm_client = helm.Client()
            logger.info("Helm client initialized")
        except Exception as e:
            logger.warning(f"Helm client initialization failed: {str(e)}")
            self.helm_client = None
        
        # Metrics
        self.deployment_counter = Counter(
            "deployments_total",
            "Number of deployments",
            ["status"]
        )
        self.resource_gauge = Gauge(
            "resource_usage",
            "Resource usage",
            ["resource_type"]
        )
        self.deployment_latency = Histogram(
            "deployment_latency_seconds",
            "Deployment latency in seconds"
        )
    
    async def deploy_infrastructure(
        self,
        infrastructure_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy complete infrastructure"""
        try:
            deployment_info = {
                "start_time": datetime.now().isoformat(),
                "components": [],
                "status": "deploying"
            }
            
            # Deploy monitoring stack
            monitoring_info = await self._deploy_monitoring()
            deployment_info["components"].append({
                "type": "monitoring",
                "info": monitoring_info
            })
            
            # Deploy message broker
            broker_info = await self._deploy_message_broker()
            deployment_info["components"].append({
                "type": "message_broker",
                "info": broker_info
            })
            
            # Deploy cache
            cache_info = await self._deploy_cache()
            deployment_info["components"].append({
                "type": "cache",
                "info": cache_info
            })
            
            # Deploy database
            db_info = await self._deploy_database()
            deployment_info["components"].append({
                "type": "database",
                "info": db_info
            })
            
            deployment_info["status"] = "deployed"
            deployment_info["end_time"] = datetime.now().isoformat()
            
            # Update metrics
            self.deployment_counter.labels(status="success").inc()
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"Infrastructure deployment failed: {str(e)}")
            self.deployment_counter.labels(status="failed").inc()
            raise
    
    async def _deploy_monitoring(self) -> Dict[str, Any]:
        """Deploy monitoring stack (Prometheus, Grafana, etc.)"""
        try:
            if self.helm_client:
                # Deploy using Helm
                monitoring_values = {
                    "prometheus": {
                        "enabled": True,
                        "server": {
                            "persistentVolume": {
                                "size": "10Gi"
                            }
                        }
                    },
                    "grafana": {
                        "enabled": True,
                        "persistence": {
                            "enabled": True,
                            "size": "5Gi"
                        }
                    },
                    "alertmanager": {
                        "enabled": True
                    }
                }
                
                # Install monitoring stack
                self.helm_client.install(
                    name="monitoring",
                    chart="prometheus-community/kube-prometheus-stack",
                    values=monitoring_values
                )
                
                return {
                    "type": "helm",
                    "release": "monitoring",
                    "components": ["prometheus", "grafana", "alertmanager"],
                    "status": "deployed"
                }
            else:
                # Deploy using Docker Compose
                compose_config = {
                    "version": "3",
                    "services": {
                        "prometheus": {
                            "image": "prom/prometheus:latest",
                            "ports": ["9090:9090"],
                            "volumes": ["./prometheus:/etc/prometheus"]
                        },
                        "grafana": {
                            "image": "grafana/grafana:latest",
                            "ports": ["3000:3000"],
                            "volumes": ["./grafana:/var/lib/grafana"]
                        }
                    }
                }
                
                # Write compose file
                with open("docker-compose.monitoring.yml", "w") as f:
                    yaml.dump(compose_config, f)
                
                # Deploy using Docker Compose
                os.system(
                    "docker-compose -f docker-compose.monitoring.yml up -d"
                )
                
                return {
                    "type": "docker-compose",
                    "file": "docker-compose.monitoring.yml",
                    "components": ["prometheus", "grafana"],
                    "status": "deployed"
                }
                
        except Exception as e:
            logger.error(f"Monitoring deployment failed: {str(e)}")
            raise
    
    async def _deploy_message_broker(self) -> Dict[str, Any]:
        """Deploy message broker (RabbitMQ/Kafka)"""
        try:
            if self.helm_client:
                # Deploy RabbitMQ using Helm
                rabbitmq_values = {
                    "auth": {
                        "username": "admin",
                        "password": "changeme"
                    },
                    "persistence": {
                        "enabled": True,
                        "size": "8Gi"
                    },
                    "metrics": {
                        "enabled": True
                    }
                }
                
                self.helm_client.install(
                    name="rabbitmq",
                    chart="bitnami/rabbitmq",
                    values=rabbitmq_values
                )
                
                return {
                    "type": "helm",
                    "release": "rabbitmq",
                    "status": "deployed"
                }
            else:
                # Deploy using Docker
                self.docker_client.containers.run(
                    "rabbitmq:3-management",
                    name="rabbitmq",
                    ports={
                        "5672/tcp": 5672,
                        "15672/tcp": 15672
                    },
                    environment={
                        "RABBITMQ_DEFAULT_USER": "admin",
                        "RABBITMQ_DEFAULT_PASS": "changeme"
                    },
                    detach=True
                )
                
                return {
                    "type": "docker",
                    "container": "rabbitmq",
                    "status": "deployed"
                }
                
        except Exception as e:
            logger.error(f"Message broker deployment failed: {str(e)}")
            raise
    
    async def _deploy_cache(self) -> Dict[str, Any]:
        """Deploy cache (Redis)"""
        try:
            if self.helm_client:
                # Deploy Redis using Helm
                redis_values = {
                    "architecture": "replication",
                    "auth": {
                        "enabled": True,
                        "password": "changeme"
                    },
                    "master": {
                        "persistence": {
                            "enabled": True,
                            "size": "8Gi"
                        }
                    },
                    "replica": {
                        "replicaCount": 2,
                        "persistence": {
                            "enabled": True,
                            "size": "8Gi"
                        }
                    }
                }
                
                self.helm_client.install(
                    name="redis",
                    chart="bitnami/redis",
                    values=redis_values
                )
                
                return {
                    "type": "helm",
                    "release": "redis",
                    "status": "deployed"
                }
            else:
                # Deploy using Docker
                self.docker_client.containers.run(
                    "redis:latest",
                    name="redis",
                    ports={"6379/tcp": 6379},
                    command="redis-server --requirepass changeme",
                    detach=True
                )
                
                return {
                    "type": "docker",
                    "container": "redis",
                    "status": "deployed"
                }
                
        except Exception as e:
            logger.error(f"Cache deployment failed: {str(e)}")
            raise
    
    async def _deploy_database(self) -> Dict[str, Any]:
        """Deploy database (PostgreSQL)"""
        try:
            if self.helm_client:
                # Deploy PostgreSQL using Helm
                postgres_values = {
                    "auth": {
                        "username": "admin",
                        "password": "changeme",
                        "database": "sefcnet"
                    },
                    "primary": {
                        "persistence": {
                            "enabled": True,
                            "size": "10Gi"
                        }
                    },
                    "metrics": {
                        "enabled": True
                    }
                }
                
                self.helm_client.install(
                    name="postgresql",
                    chart="bitnami/postgresql",
                    values=postgres_values
                )
                
                return {
                    "type": "helm",
                    "release": "postgresql",
                    "status": "deployed"
                }
            else:
                # Deploy using Docker
                self.docker_client.containers.run(
                    "postgres:latest",
                    name="postgres",
                    ports={"5432/tcp": 5432},
                    environment={
                        "POSTGRES_USER": "admin",
                        "POSTGRES_PASSWORD": "changeme",
                        "POSTGRES_DB": "sefcnet"
                    },
                    detach=True
                )
                
                return {
                    "type": "docker",
                    "container": "postgres",
                    "status": "deployed"
                }
                
        except Exception as e:
            logger.error(f"Database deployment failed: {str(e)}")
            raise
    
    async def monitor_resources(self) -> None:
        """Monitor infrastructure resources"""
        try:
            while True:
                if self.k8s_api:
                    # Monitor Kubernetes resources
                    nodes = self.k8s_api.list_node()
                    for node in nodes.items:
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
                        
                        self.resource_gauge.labels(
                            resource_type="cpu"
                        ).set(cpu_percent)
                        self.resource_gauge.labels(
                            resource_type="memory"
                        ).set(memory_percent)
                
                elif self.docker_client:
                    # Monitor Docker resources
                    containers = self.docker_client.containers.list()
                    for container in containers:
                        stats = container.stats(stream=False)
                        
                        cpu_percent = stats["cpu_stats"]["cpu_usage"]["total_usage"]
                        memory_percent = stats["memory_stats"]["usage"]
                        
                        self.resource_gauge.labels(
                            resource_type="cpu"
                        ).set(cpu_percent)
                        self.resource_gauge.labels(
                            resource_type="memory"
                        ).set(memory_percent)
                
                await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"Resource monitoring failed: {str(e)}")
            raise
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load deployment configuration"""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Config loading failed: {str(e)}")
            return {}