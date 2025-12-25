"""
Enterprise-grade monitoring and health system
"""
from typing import Dict, List, Optional, Any, Union
import asyncio
from datetime import datetime
import json

from prometheus_client import Counter, Gauge, Histogram
from prometheus_api_client import PrometheusConnect
import aiohttp
import psutil
import py3nvml.nvidia_smi as nvidia_smi

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)

class HealthMonitor:
    """Enterprise-grade health monitoring system"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize health monitor"""
        self.config = config or {}
        self.metrics = MetricsCollector()
        
        # Health check configuration
        self.check_interval = self.config.get("check_interval", 60)
        self.timeout = self.config.get("timeout", 10)
        
        # Initialize Prometheus client
        self._init_prometheus()
        
        # Service health tracking
        self.service_health = {}
        
        # Metrics
        self.health_gauge = Gauge(
            "service_health_status",
            "Service health status",
            ["service", "check_type"]
        )
        self.check_counter = Counter(
            "health_checks_total",
            "Total health checks performed",
            ["service", "status"]
        )
        self.check_latency = Histogram(
            "health_check_latency_seconds",
            "Health check latency",
            ["service"]
        )
    
    def _init_prometheus(self):
        """Initialize Prometheus client"""
        try:
            prom_url = self.config.get("prometheus_url", "http://localhost:9090")
            self.prom_client = PrometheusConnect(url=prom_url)
            logger.info("Prometheus client initialized")
        except Exception as e:
            logger.error(f"Prometheus client initialization failed: {str(e)}")
            raise
    
    async def run_health_checks(
        self,
        services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run health checks for services"""
        try:
            results = {}
            tasks = []
            
            for service in services:
                tasks.append(
                    self._check_service_health(service)
                )
            
            check_results = await asyncio.gather(*tasks)
            
            for service, result in zip(services, check_results):
                service_name = service["name"]
                results[service_name] = result
                
                # Update metrics
                self.health_gauge.labels(
                    service=service_name,
                    check_type="overall"
                ).set(1 if result["status"] == "healthy" else 0)
                
                self.check_counter.labels(
                    service=service_name,
                    status=result["status"]
                ).inc()
            
            return results
            
        except Exception as e:
            logger.error(f"Health check run failed: {str(e)}")
            raise
    
    async def _check_service_health(
        self,
        service: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check health of a single service"""
        start_time = datetime.now()
        service_name = service["name"]
        
        try:
            # Endpoint check
            endpoint_health = await self._check_endpoint(
                service.get("health_endpoint")
            )
            
            # Resource check
            resource_health = await self._check_resources(
                service.get("resource_limits", {})
            )
            
            # Dependency check
            dependency_health = await self._check_dependencies(
                service.get("dependencies", [])
            )
            
            # Calculate overall health
            is_healthy = all([
                endpoint_health["healthy"],
                resource_health["healthy"],
                dependency_health["healthy"]
            ])
            
            result = {
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "endpoint": endpoint_health,
                    "resources": resource_health,
                    "dependencies": dependency_health
                }
            }
            
            # Update service health tracking
            self.service_health[service_name] = result
            
            # Record check latency
            check_duration = (datetime.now() - start_time).total_seconds()
            self.check_latency.labels(service=service_name).observe(
                check_duration
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Health check failed for service {service_name}: {str(e)}"
            )
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_endpoint(
        self,
        endpoint: Optional[str]
    ) -> Dict[str, Any]:
        """Check endpoint health"""
        if not endpoint:
            return {"healthy": True, "skipped": True}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    timeout=self.timeout
                ) as response:
                    return {
                        "healthy": response.status < 400,
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_resources(
        self,
        limits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check resource health"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            cpu_healthy = cpu_percent <= limits.get("cpu_percent", 80)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent <= limits.get("memory_percent", 80)
            
            # Disk usage
            disk = psutil.disk_usage("/")
            disk_healthy = disk.percent <= limits.get("disk_percent", 80)
            
            # GPU usage if available
            gpu_healthy = True
            try:
                nvidia_smi.nvmlInit()
                handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
                info = nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
                gpu_healthy = info.gpu <= limits.get("gpu_percent", 80)
            except Exception:
                pass
            
            return {
                "healthy": all([
                    cpu_healthy,
                    memory_healthy,
                    disk_healthy,
                    gpu_healthy
                ]),
                "metrics": {
                    "cpu": cpu_percent,
                    "memory": memory.percent,
                    "disk": disk.percent
                }
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_dependencies(
        self,
        dependencies: List[str]
    ) -> Dict[str, Any]:
        """Check dependency health"""
        if not dependencies:
            return {"healthy": True, "skipped": True}
        
        results = {}
        healthy = True
        
        for dep in dependencies:
            if dep in self.service_health:
                dep_status = self.service_health[dep]["status"]
                results[dep] = dep_status
                healthy = healthy and dep_status == "healthy"
            else:
                results[dep] = "unknown"
                healthy = False
        
        return {
            "healthy": healthy,
            "dependencies": results
        }

class PerformanceMonitor:
    """Enterprise-grade performance monitoring system"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize performance monitor"""
        self.config = config or {}
        self.metrics = MetricsCollector()
        
        # Performance thresholds
        self.thresholds = self.config.get("thresholds", {
            "latency_ms": 1000,
            "error_rate": 0.01,
            "cpu_percent": 80,
            "memory_percent": 80
        })
        
        # Metrics
        self.latency_histogram = Histogram(
            "request_latency_milliseconds",
            "Request latency in milliseconds",
            ["service", "endpoint"]
        )
        self.error_counter = Counter(
            "request_errors_total",
            "Total request errors",
            ["service", "error_type"]
        )
        self.performance_gauge = Gauge(
            "performance_score",
            "Overall performance score",
            ["service"]
        )
    
    async def monitor_performance(
        self,
        service: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor service performance"""
        try:
            service_name = service["name"]
            
            # Collect metrics
            metrics = await self._collect_metrics(service)
            
            # Analyze performance
            analysis = self._analyze_performance(metrics)
            
            # Update performance score
            self.performance_gauge.labels(
                service=service_name
            ).set(analysis["score"])
            
            return {
                "service": service_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "analysis": analysis,
                "status": "healthy" if analysis["score"] >= 0.8 else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {str(e)}")
            raise
    
    async def _collect_metrics(
        self,
        service: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            # Application metrics
            app_metrics = await self._get_application_metrics(service)
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent
                },
                "application": app_metrics
            }
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {str(e)}")
            raise
    
    async def _get_application_metrics(
        self,
        service: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            metrics = {}
            
            # Query Prometheus for metrics
            for metric in service.get("metrics", []):
                query = metric["query"]
                result = self.prom_client.custom_query(query)
                
                if result:
                    metrics[metric["name"]] = float(result[0]["value"][1])
            
            return metrics
            
        except Exception:
            return {}
    
    def _analyze_performance(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance metrics"""
        try:
            scores = []
            issues = []
            
            # Check system metrics
            system = metrics["system"]
            if system["cpu_percent"] > self.thresholds["cpu_percent"]:
                issues.append("High CPU usage")
                scores.append(0.5)
            else:
                scores.append(1.0)
            
            if system["memory_percent"] > self.thresholds["memory_percent"]:
                issues.append("High memory usage")
                scores.append(0.5)
            else:
                scores.append(1.0)
            
            # Check application metrics
            app = metrics["application"]
            if "latency_ms" in app:
                if app["latency_ms"] > self.thresholds["latency_ms"]:
                    issues.append("High latency")
                    scores.append(0.5)
                else:
                    scores.append(1.0)
            
            if "error_rate" in app:
                if app["error_rate"] > self.thresholds["error_rate"]:
                    issues.append("High error rate")
                    scores.append(0.3)
                else:
                    scores.append(1.0)
            
            # Calculate overall score
            score = sum(scores) / len(scores) if scores else 0
            
            return {
                "score": score,
                "issues": issues,
                "recommendations": self._generate_recommendations(issues)
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return {
                "score": 0,
                "error": str(e)
            }
    
    def _generate_recommendations(
        self,
        issues: List[str]
    ) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        for issue in issues:
            if issue == "High CPU usage":
                recommendations.append(
                    "Consider scaling horizontally or optimizing CPU-intensive operations"
                )
            elif issue == "High memory usage":
                recommendations.append(
                    "Investigate memory leaks or increase memory allocation"
                )
            elif issue == "High latency":
                recommendations.append(
                    "Check network connectivity and optimize database queries"
                )
            elif issue == "High error rate":
                recommendations.append(
                    "Review error logs and implement retry mechanisms"
                )
        
        return recommendations