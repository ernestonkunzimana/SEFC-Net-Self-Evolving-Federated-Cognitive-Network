"""
Enterprise-grade service registry and discovery system
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import asyncio
import uuid

from fastapi import HTTPException
import etcd3
import aioredis
from prometheus_client import Counter, Gauge

from ..utils.logger import get_logger
from ..utils.cache import EnterpriseCache
from ..utils.resilience import CircuitBreaker

logger = get_logger(__name__)

class ServiceRegistry:
    """Enterprise-grade service registry and discovery"""
    
    def __init__(
        self,
        etcd_host: str = "localhost",
        etcd_port: int = 2379,
        redis_url: str = "redis://localhost:6379/0",
        ttl: int = 30,
        sync_interval: int = 10
    ):
        """Initialize service registry"""
        self.ttl = ttl
        self.sync_interval = sync_interval
        
        # Setup etcd client
        try:
            self.etcd = etcd3.client(host=etcd_host, port=etcd_port)
            logger.info("ETCD connection established")
        except Exception as e:
            logger.error(f"ETCD connection failed: {str(e)}")
            self.etcd = None
        
        # Setup Redis for fast lookups
        self.cache = EnterpriseCache(redis_url=redis_url)
        
        # Circuit breaker for external calls
        self.circuit_breaker = CircuitBreaker()
        
        # Metrics
        self.services_gauge = Gauge(
            "service_registry_services_total",
            "Total number of registered services",
            ["status"]
        )
        self.registration_counter = Counter(
            "service_registry_registrations_total",
            "Total number of service registrations",
            ["service"]
        )
        self.heartbeat_counter = Counter(
            "service_registry_heartbeats_total",
            "Total number of service heartbeats",
            ["service", "status"]
        )
    
    async def register_service(
        self,
        service_name: str,
        instance_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 8000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a service instance"""
        try:
            instance_id = instance_id or str(uuid.uuid4())
            
            service_data = {
                "instance_id": instance_id,
                "service_name": service_name,
                "host": host,
                "port": port,
                "metadata": metadata or {},
                "status": "healthy",
                "last_heartbeat": datetime.now().isoformat(),
                "registered_at": datetime.now().isoformat()
            }
            
            # Store in etcd with lease
            if self.etcd:
                key = f"/services/{service_name}/{instance_id}"
                lease = self.etcd.lease(ttl=self.ttl)
                self.etcd.put(
                    key,
                    json.dumps(service_data),
                    lease=lease
                )
            
            # Cache service data
            await self.cache.set(
                f"service:{service_name}:{instance_id}",
                service_data,
                ttl=self.ttl
            )
            
            # Update metrics
            self.services_gauge.labels(status="healthy").inc()
            self.registration_counter.labels(service=service_name).inc()
            
            logger.info(f"Service registered: {service_name} ({instance_id})")
            return instance_id
            
        except Exception as e:
            logger.error(f"Service registration failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Service registration failed: {str(e)}"
            )
    
    async def deregister_service(
        self,
        service_name: str,
        instance_id: str
    ) -> bool:
        """Deregister a service instance"""
        try:
            # Remove from etcd
            if self.etcd:
                key = f"/services/{service_name}/{instance_id}"
                self.etcd.delete(key)
            
            # Remove from cache
            await self.cache.delete(f"service:{service_name}:{instance_id}")
            
            # Update metrics
            self.services_gauge.labels(status="healthy").dec()
            
            logger.info(f"Service deregistered: {service_name} ({instance_id})")
            return True
            
        except Exception as e:
            logger.error(f"Service deregistration failed: {str(e)}")
            return False
    
    async def heartbeat(
        self,
        service_name: str,
        instance_id: str
    ) -> bool:
        """Update service heartbeat"""
        try:
            # Get existing service data
            key = f"service:{service_name}:{instance_id}"
            service_data = await self.cache.get(key)
            
            if not service_data:
                raise ValueError("Service not found")
            
            # Update heartbeat
            service_data["last_heartbeat"] = datetime.now().isoformat()
            service_data["status"] = "healthy"
            
            # Update etcd
            if self.etcd:
                etcd_key = f"/services/{service_name}/{instance_id}"
                lease = self.etcd.lease(ttl=self.ttl)
                self.etcd.put(
                    etcd_key,
                    json.dumps(service_data),
                    lease=lease
                )
            
            # Update cache
            await self.cache.set(key, service_data, ttl=self.ttl)
            
            # Update metrics
            self.heartbeat_counter.labels(
                service=service_name,
                status="success"
            ).inc()
            
            return True
            
        except Exception as e:
            logger.error(f"Heartbeat failed: {str(e)}")
            self.heartbeat_counter.labels(
                service=service_name,
                status="failed"
            ).inc()
            return False
    
    async def get_service(
        self,
        service_name: str,
        instance_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get service instance details"""
        try:
            if instance_id:
                # Get specific instance
                key = f"service:{service_name}:{instance_id}"
                service_data = await self.cache.get(key)
                
                if not service_data:
                    raise ValueError("Service instance not found")
                
                return service_data
            else:
                # Get all instances of the service
                if self.etcd:
                    instances = []
                    prefix = f"/services/{service_name}/"
                    
                    for value, _ in self.etcd.get_prefix(prefix):
                        if value:
                            instances.append(json.loads(value))
                    
                    return {
                        "service_name": service_name,
                        "instances": instances
                    }
                else:
                    raise ValueError("Service registry unavailable")
                
        except Exception as e:
            logger.error(f"Error getting service details: {str(e)}")
            raise HTTPException(
                status_code=404,
                detail=f"Service not found: {str(e)}"
            )
    
    async def list_services(self) -> List[Dict[str, Any]]:
        """List all registered services"""
        try:
            services = []
            
            if self.etcd:
                prefix = "/services/"
                for value, _ in self.etcd.get_prefix(prefix):
                    if value:
                        services.append(json.loads(value))
            
            return services
            
        except Exception as e:
            logger.error(f"Error listing services: {str(e)}")
            return []
    
    async def start_health_check(self) -> None:
        """Start health check loop"""
        while True:
            try:
                services = await self.list_services()
                
                for service in services:
                    last_heartbeat = datetime.fromisoformat(
                        service["last_heartbeat"]
                    )
                    
                    if (datetime.now() - last_heartbeat).total_seconds() > self.ttl:
                        # Service is unhealthy
                        service["status"] = "unhealthy"
                        
                        # Update metrics
                        self.services_gauge.labels(
                            status="healthy"
                        ).dec()
                        self.services_gauge.labels(
                            status="unhealthy"
                        ).inc()
                        
                        # Update service data
                        await self.cache.set(
                            f"service:{service['service_name']}:{service['instance_id']}",
                            service,
                            ttl=self.ttl
                        )
                
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
            
            await asyncio.sleep(self.sync_interval)