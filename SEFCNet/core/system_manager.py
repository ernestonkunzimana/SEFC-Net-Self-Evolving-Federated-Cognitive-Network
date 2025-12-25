"""
Core System Manager for SEFCNet
============================
Enterprise-grade system manager providing:
- High availability management
- Load balancing
- Service discovery
- Health monitoring
- Resource orchestration
- System recovery
- Configuration management
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import socket
import subprocess
import sys
from pathlib import Path
import yaml

import aiohttp
try:
    import docker
except ImportError:
    docker = None
try:
    import kubernetes
    from kubernetes import client, config
except ImportError:
    kubernetes = None
    client = None
    config = None
try:
    import etcd3
except ImportError:
    etcd3 = None
try:
    import consul
except ImportError:
    consul = None
import tenacity
from prometheus_client import Counter, Gauge, Histogram

try:
    from monitoring.metrics_collector import metrics_collector, SystemMetricsCollector
    from monitoring.monitoring_service import monitoring_service
except ImportError:
    metrics_collector = None
    SystemMetricsCollector = None
    monitoring_service = None

try:
    from analytics.analytics_manager import AnalyticsManager, analytics_manager
except ImportError:
    AnalyticsManager = None
    analytics_manager = None

try:
    from rl.reward_engine import RewardEngine, RewardConfig
except ImportError:
    RewardEngine = None
    RewardConfig = None

# Evolution manager is optional; core system should still import without it
try:  # pragma: no cover
    from .evolution_manager import EvolutionManager, EvolutionConfig  # type: ignore
except Exception:  # pragma: no cover
    EvolutionManager = None  # type: ignore
    EvolutionConfig = None  # type: ignore

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Service configuration."""
    name: str
    version: str
    replicas: int
    min_replicas: int
    max_replicas: int
    cpu_limit: str
    memory_limit: str
    environment: Dict[str, str]
    dependencies: List[str]
    healthcheck: Dict[str, Any]

@dataclass
class SystemState:
    """System state tracking"""
    status: str
    active_clients: int
    current_round: int
    global_accuracy: float
    timestamp: datetime

class CoreSystemManager:
    """Enterprise-grade system manager."""

    def __init__(self):
        self._load_configuration()
        self._initialize_clients()
        self._setup_metrics()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._service_states: Dict[str, Dict[str, Any]] = {}
        self._resource_states: Dict[str, Dict[str, Any]] = {}
        self._last_system_state: Optional[SystemState] = None
        self._recovery_in_progress: Set[str] = set()
        self._ha_lock = threading.Lock()
        self._is_primary = False
        self._failover_timeout = 30  # seconds

        # Evolution and reward management
        if EvolutionManager is not None and EvolutionConfig is not None:
            try:
                self.evolution_manager = EvolutionManager(EvolutionConfig().__dict__)
            except Exception:
                self.evolution_manager = None
        else:
            self.evolution_manager = None

        self.reward_engine = RewardEngine(RewardConfig())

        # Reuse global analytics manager instance to avoid duplicate metric registration
        try:
            self.analytics_manager = analytics_manager
        except Exception:
            self.analytics_manager = None
        self.active_nodes: List[str] = []
        self.system_state: Dict[str, Any] = {}

    def _load_configuration(self):
        """Load system configuration."""
        config_path = Path(__file__).parent / "config" / "system.yaml"
        try:
            with open(config_path, encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # In test and dev environments we allow the system config to be missing
            logger.warning("System configuration file %s not found; using defaults", config_path)
            self.config = {}
        except Exception as e:
            logger.warning("Failed to load system configuration %s: %s", config_path, e)
            self.config = {}

        # Environment-specific configurations
        self.env = os.getenv("SEFCNET_ENV", "development")
        self.config.update(self._load_env_config())

    def _load_env_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        env_config_path = Path(__file__).parent / 'config' / f'{self.env}.yaml'
        if env_config_path.exists():
            with open(env_config_path) as f:
                return json.load(f)
        return {}

    def _initialize_clients(self):
        """Initialize service clients.

        All external dependencies (k8s, docker, etcd, consul) are treated as optional
        so unit tests can run in lightweight environments.
        """
        # Kubernetes client (optional)
        try:
            try:
                config.load_incluster_config()
            except kubernetes.config.ConfigException:
                config.load_kube_config()
            self.k8s_client = client.CoreV1Api()
            self.k8s_apps = client.AppsV1Api()
        except Exception as e:
            self.k8s_client = None
            self.k8s_apps = None
            logger.warning("Kubernetes client initialization failed; skipping k8s integration: %s", e)

        # Docker client (optional – may not be running)
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            self.docker_client = None
            logger.warning("Docker daemon not available; skipping docker integration: %s", e)

        # Service discovery (optional)
        try:
            if self.config.get('service_discovery') == 'etcd':
                self.discovery_client = etcd3.client()
            else:
                self.discovery_client = consul.Consul()
        except Exception as e:
            self.discovery_client = None
            logger.warning("Service discovery client initialization failed: %s", e)

    def _setup_metrics(self):
        """Setup system metrics."""
        self.metrics = {
            'service_health': Gauge(
                'system_service_health',
                'Service health status',
                ['service_name']
            ),
            'failover_count': Counter(
                'system_failover_count',
                'Number of failover events'
            ),
            'recovery_time': Histogram(
                'system_recovery_time_seconds',
                'Time taken for system recovery',
                ['service_name']
            )
        }

    async def start(self):
        """Start the system manager."""
        await self._elect_leader()
        if self._is_primary:
            await self._start_system_management()

    async def stop(self):
        """Stop the system manager."""
        if self._is_primary:
            await self._stop_system_management()

    async def _elect_leader(self):
        """Perform leader election."""
        while True:
            try:
                if self.config.get('service_discovery') == 'etcd':
                    lease = self.discovery_client.lease(ttl=30)
                    success = self.discovery_client.put(
                        '/sefcnet/leader',
                        socket.gethostname().encode(),
                        lease=lease
                    )
                    self._is_primary = success
                else:
                    session = self.discovery_client.session.create(
                        ttl=30,
                        behavior='delete'
                    )
                    self._is_primary = self.discovery_client.kv.put(
                        'sefcnet/leader',
                        socket.gethostname(),
                        acquire=session
                    )
                if self._is_primary:
                    break
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Leader election error: {str(e)}")
                await asyncio.sleep(1)

    async def _start_system_management(self):
        """Start system management tasks."""
        self.management_tasks = [
            asyncio.create_task(self._monitor_services()),
            asyncio.create_task(self._monitor_resources()),
            asyncio.create_task(self._perform_health_checks()),
            asyncio.create_task(self._manage_scaling())
        ]

    async def _stop_system_management(self):
        """Stop system management tasks."""
        for task in self.management_tasks:
            task.cancel()
        await asyncio.gather(*self.management_tasks, return_exceptions=True)

    async def _monitor_services(self):
        """Monitor service states and health."""
        while True:
            try:
                services = await self._get_service_states()
                for service_name, state in services.items():
                    self._service_states[service_name] = state
                    self.metrics['service_health'].labels(
                        service_name=service_name
                    ).set(1 if state['healthy'] else 0)

                    if not state['healthy'] and service_name not in self._recovery_in_progress:
                        await self._initiate_recovery(service_name)

                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Service monitoring error: {str(e)}")
                await asyncio.sleep(1)

    async def _get_service_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all services."""
        states = {}
        
        # Kubernetes services
        try:
            pods = self.k8s_client.list_namespaced_pod(
                namespace='default'
            )
            for pod in pods.items:
                service_name = pod.metadata.labels.get('app')
                if service_name:
                    states[service_name] = {
                        'healthy': pod.status.phase == 'Running',
                        'pod_name': pod.metadata.name,
                        'node': pod.spec.node_name,
                        'start_time': pod.status.start_time,
                        'restarts': pod.status.container_statuses[0].restart_count
                    }
        except Exception as e:
            logger.error(f"Kubernetes service state error: {str(e)}")

        # Docker services
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                service_name = container.labels.get('app')
                if service_name:
                    states[service_name] = {
                        'healthy': container.status == 'running',
                        'container_id': container.id,
                        'image': container.image.tags[0],
                        'start_time': container.attrs['State']['StartedAt'],
                        'restarts': container.attrs['RestartCount']
                    }
        except Exception as e:
            logger.error(f"Docker service state error: {str(e)}")

        return states

    async def _monitor_resources(self):
        """Monitor system resources."""
        while True:
            try:
                resources = await self._get_resource_states()
                self._resource_states.update(resources)
                await self._check_resource_thresholds()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Resource monitoring error: {str(e)}")
                await asyncio.sleep(1)

    async def _get_resource_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of system resources."""
        states = {}

        # Kubernetes node resources
        try:
            nodes = self.k8s_client.list_node()
            for node in nodes.items:
                states[node.metadata.name] = {
                    'cpu_capacity': node.status.capacity['cpu'],
                    'memory_capacity': node.status.capacity['memory'],
                    'cpu_allocatable': node.status.allocatable['cpu'],
                    'memory_allocatable': node.status.allocatable['memory'],
                    'conditions': {
                        cond.type: cond.status
                        for cond in node.status.conditions
                    }
                }
        except Exception as e:
            logger.error(f"Kubernetes resource state error: {str(e)}")

        # Host resources
        try:
            import psutil
            states['host'] = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {
                    disk.mountpoint: psutil.disk_usage(disk.mountpoint).percent
                    for disk in psutil.disk_partitions()
                },
                'network_io': psutil.net_io_counters()._asdict()
            }
        except Exception as e:
            logger.error(f"Host resource state error: {str(e)}")

        return states

    async def _check_resource_thresholds(self):
        """Check resource usage against thresholds."""
        thresholds = self.config.get('resource_thresholds', {})
        
        for resource, state in self._resource_states.items():
            if 'cpu_percent' in state and state['cpu_percent'] > thresholds.get('cpu', 80):
                await self._handle_resource_threshold_breach(
                    resource, 'CPU', state['cpu_percent']
                )
            
            if 'memory_percent' in state and state['memory_percent'] > thresholds.get('memory', 80):
                await self._handle_resource_threshold_breach(
                    resource, 'Memory', state['memory_percent']
                )

    async def _handle_resource_threshold_breach(
        self,
        resource: str,
        resource_type: str,
        value: float
    ):
        """Handle resource threshold breach."""
        logger.warning(
            f"Resource threshold breach: {resource} {resource_type} at {value}%"
        )
        
        # Trigger autoscaling if enabled
        if self.config.get('autoscaling_enabled'):
            await self._scale_resource(resource, resource_type)

    async def _scale_resource(self, resource: str, resource_type: str):
        """Scale resource based on demand."""
        try:
            if resource_type == 'CPU':
                # Scale compute resources
                await self._scale_compute_resources(resource)
            elif resource_type == 'Memory':
                # Scale memory resources
                await self._scale_memory_resources(resource)
        except Exception as e:
            logger.error(f"Resource scaling error: {str(e)}")

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _scale_compute_resources(self, resource: str):
        """Scale compute resources."""
        deployment = self.k8s_apps.read_namespaced_deployment(
            name=resource,
            namespace='default'
        )
        
        current_replicas = deployment.spec.replicas
        max_replicas = self.config.get('max_replicas', 5)
        
        if current_replicas < max_replicas:
            deployment.spec.replicas = current_replicas + 1
            self.k8s_apps.patch_namespaced_deployment(
                name=resource,
                namespace='default',
                body=deployment
            )
            logger.info(f"Scaled up {resource} to {current_replicas + 1} replicas")

    async def _perform_health_checks(self):
        """Perform system health checks."""
        while True:
            try:
                health_status = await self._check_system_health()
                self._last_system_state = SystemState(
                    timestamp=datetime.utcnow(),
                    services=self._service_states.copy(),
                    resources=self._resource_states.copy(),
                    health=health_status,
                    alerts=monitoring_service.get_active_alerts()
                )
                await asyncio.sleep(15)
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(1)

    async def _check_system_health(self) -> Dict[str, bool]:
        """Check health of all system components."""
        health_status = {}

        # Check service health
        for service_name, state in self._service_states.items():
            health_status[f"service_{service_name}"] = state['healthy']

        # Check resource health
        for resource, state in self._resource_states.items():
            if 'conditions' in state:
                health_status[f"resource_{resource}"] = all(
                    cond == 'True' for cond in state['conditions'].values()
                )

        # Check database connections
        health_status['database'] = await self._check_database_health()

        # Check message queues
        health_status['message_queue'] = await self._check_queue_health()

        # Check cache
        health_status['cache'] = await self._check_cache_health()

        return health_status

    async def _initiate_recovery(self, service_name: str):
        """Initiate service recovery."""
        self._recovery_in_progress.add(service_name)
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Initiating recovery for {service_name}")
            
            # Get service configuration
            service_config = self.config['services'].get(service_name)
            if not service_config:
                raise ValueError(f"No configuration found for {service_name}")

            # Stop the service
            await self._stop_service(service_name)
            
            # Clean up resources
            await self._cleanup_service_resources(service_name)
            
            # Restore service
            await self._restore_service(service_name, service_config)
            
            # Verify recovery
            if await self._verify_service_health(service_name):
                recovery_time = (datetime.utcnow() - start_time).total_seconds()
                self.metrics['recovery_time'].labels(
                    service_name=service_name
                ).observe(recovery_time)
                logger.info(f"Recovery successful for {service_name}")
            else:
                logger.error(f"Recovery failed for {service_name}")
                
        except Exception as e:
            logger.error(f"Recovery error for {service_name}: {str(e)}")
        finally:
            self._recovery_in_progress.remove(service_name)

    async def _manage_scaling(self):
        """Manage system scaling."""
        while True:
            try:
                await self._check_scaling_needs()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Scaling management error: {str(e)}")
                await asyncio.sleep(1)

    async def _check_scaling_needs(self):
        """Check if scaling is needed."""
        for service_name, state in self._service_states.items():
            config = self.config['services'].get(service_name)
            if not config:
                continue

            metrics = await self._get_service_metrics(service_name)
            if await self._needs_scaling(metrics, config):
                await self._scale_service(service_name, metrics, config)

    async def get_system_state(self) -> SystemState:
        """Get current system state."""
        if not self._last_system_state or \
           (datetime.utcnow() - self._last_system_state.timestamp).seconds > 30:
            # Refresh state if it's too old
            health_status = await self._check_system_health()
            self._last_system_state = SystemState(
                timestamp=datetime.utcnow(),
                services=self._service_states.copy(),
                resources=self._resource_states.copy(),
                health=health_status,
                alerts=monitoring_service.get_active_alerts()
            )
        return self._last_system_state

    async def deploy_service(
        self,
        service_config: ServiceConfig
    ) -> Dict[str, Any]:
        """Deploy a new service."""
        try:
            # Validate configuration
            self._validate_service_config(service_config)

            # Create deployment
            deployment = self._create_deployment_object(service_config)
            self.k8s_apps.create_namespaced_deployment(
                body=deployment,
                namespace='default'
            )

            # Create service
            service = self._create_service_object(service_config)
            self.k8s_client.create_namespaced_service(
                body=service,
                namespace='default'
            )

            # Register service
            await self._register_service(service_config)

            return {
                'status': 'success',
                'message': f"Service {service_config.name} deployed successfully"
            }
        except Exception as e:
            logger.error(f"Service deployment error: {str(e)}")
            raise

    def _validate_service_config(self, config: ServiceConfig):
        """Validate service configuration."""
        required_fields = {'name', 'version', 'replicas', 'cpu_limit', 'memory_limit'}
        missing_fields = required_fields - set(config.__dict__.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        if config.replicas < config.min_replicas or config.replicas > config.max_replicas:
            raise ValueError("Invalid replica count")

    async def _register_service(self, config: ServiceConfig):
        """Register service with service discovery."""
        service_data = {
            'name': config.name,
            'version': config.version,
            'endpoints': [f"{config.name}:8080"],
            'metadata': {
                'replicas': config.replicas,
                'cpu_limit': config.cpu_limit,
                'memory_limit': config.memory_limit
            }
        }

        if self.config.get('service_discovery') == 'etcd':
            self.discovery_client.put(
                f'/services/{config.name}',
                json.dumps(service_data).encode()
            )
        else:
            self.discovery_client.agent.service.register(
                name=config.name,
                service_id=f"{config.name}-{config.version}",
                tags=['federated-learning'],
                meta=service_data['metadata']
            )

    async def initialize(self):
        """Initialize system components"""
        try:
            # Initialize core components
            self._components.update({
                'client_manager': await self._init_client_manager(),
                'federation': await self._init_federation(),
                'evolution': await self._init_evolution(),
                'monitoring': await self._init_monitoring()
            })
            
            self.state = SystemState(
                status="initialized",
                active_clients=0,
                current_round=0,
                global_accuracy=0.0,
                timestamp=datetime.now()
            )
            
            self.logger.info("System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise

    def _setup_monitoring(self):
        """Setup monitoring components."""
        pass  # Implementation for setting up monitoring

    def _initialize_analytics(self):
        """Initialize analytics components."""
        pass  # Implementation for initializing analytics

# Initialize global system manager
system_manager = CoreSystemManager()

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional etcd3 / consul clients: guard imports
try:
    import etcd3
except Exception:
    etcd3 = None

try:
    import consul
except Exception:
    consul = None

class SystemManager:
    """Lightweight system manager: loads config and exposes start/stop hooks."""

    def __init__(self, config_source: Union[str, Path, Dict[str, Any], None] = None):
        self.config_path: Optional[Path] = None
        self.config: Dict[str, Any] = {}
        self._initialized = False
        self._components = {}
        self._etcd_client = None
        self._consul_client = None

        if config_source is None:
            config_source = Path("config/evolution_config.yaml")

        if isinstance(config_source, (str, Path)):
            self.config_path = Path(config_source)
        elif isinstance(config_source, dict):
            self.config = dict(config_source)
        else:
            raise TypeError("config_source must be path or dict")

    def initialize(self):
        """Load configuration and initialize components (lazy heavy imports)."""
        if self.config_path:
            try:
                import yaml
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Failed to load config %s: %s", self.config_path, e)
                self.config = self.config or {}

        # Try etcd if configured and available
        if etcd3 is not None and self.config.get("service_discovery", {}).get("use_etcd", False):
            try:
                host = self.config.get("service_discovery", {}).get("etcd_host", "127.0.0.1")
                port = int(self.config.get("service_discovery", {}).get("etcd_port", 2379))
                self._etcd_client = etcd3.client(host=host, port=port)
                logger.info("Connected to etcd at %s:%s", host, port)
            except Exception as e:
                logger.warning("Failed to initialize etcd client: %s", e)
                self._etcd_client = None
        else:
            logger.debug("etcd not used or not installed")

        # Try consul if configured and available
        if consul is not None and self.config.get("service_discovery", {}).get("use_consul", False):
            try:
                consul_host = self.config.get("service_discovery", {}).get("consul_host", "127.0.0.1")
                consul_port = int(self.config.get("service_discovery", {}).get("consul_port", 8500))
                self._consul_client = consul.Consul(host=consul_host, port=consul_port)
                logger.info("Connected to consul at %s:%s", consul_host, consul_port)
            except Exception as e:
                logger.warning("Failed to initialize consul client: %s", e)
                self._consul_client = None
        else:
            logger.debug("consul not used or not installed")

        # Lazy-init optional components (metrics...)
        try:
            from monitoring.metrics.metrics_collector import MetricsCollector  # optional
            self._components["metrics"] = MetricsCollector(self.config.get("monitoring", {}))
        except Exception:
            logger.debug("MetricsCollector not available or failed to import")

        self._initialized = True
        logger.info("SystemManager initialized")

    def initialize_system(self):
        """Compatibility wrapper used by tests."""
        self.initialize()
        return self.config

    def start_federation(self):
        """Start federation loop or delegate to federated coordinator if available."""
        if not self._initialized:
            raise RuntimeError("SystemManager not initialized")

        try:
            from core.federation.coordinator import FederationCoordinator  # optional
            coord = FederationCoordinator(self.config.get("federation", {}))
            coord.start_federation()
            self._components["coordinator"] = coord
            logger.info("FederationCoordinator started")
        except Exception:
            logger.info("FederationCoordinator not available; running no-op federation stub")

    def cleanup(self):
        """Cleanup components."""
        for name, comp in list(self._components.items()):
            try:
                if hasattr(comp, "stop"):
                    comp.stop()
                elif hasattr(comp, "cleanup"):
                    comp.cleanup()
            except Exception as e:
                logger.debug("Error cleaning component %s: %s", name, e)
        if self._etcd_client:
            try:
                self._etcd_client.close()
            except Exception:
                pass
        logger.info("SystemManager cleanup complete")

    def shutdown_system(self):
        """Compatibility wrapper used by tests."""
        self.cleanup()