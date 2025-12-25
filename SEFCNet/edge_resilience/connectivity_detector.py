"""
Connectivity Detector
====================

Intelligent network state detection and adaptive strategy selection.

Probes:
- Internet reachability (ping Google/Cloudflare DNS)
- Bandwidth estimation (speed test)
- Latency measurement
- Connection stability (jitter, packet loss)

Automatically switches between:
- ONLINE: Full federation with central server
- INTERMITTENT: Batch synchronization mode
- MESH_ONLY: Local peer-to-peer federation
- OFFLINE: Fully autonomous operation
"""

import asyncio
import socket
import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from . import ConnectivityMode, SyncStrategy

logger = logging.getLogger(__name__)


@dataclass
class ConnectivityMetrics:
    """Network connectivity measurements"""
    is_reachable: bool
    latency_ms: Optional[float]
    bandwidth_mbps: Optional[float]
    packet_loss: float
    jitter_ms: Optional[float]
    timestamp: float


class AdaptiveConnectivityManager:
    """
    Continuously monitors network connectivity and adapts FL strategy
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # Check every 60 seconds
        latency_threshold: int = 1000,  # 1000ms = poor connection
        bandwidth_threshold: float = 0.1,  # 100 kbps minimum
    ):
        self.check_interval = check_interval
        self.latency_threshold = latency_threshold
        self.bandwidth_threshold = bandwidth_threshold
        
        self.current_mode: ConnectivityMode = ConnectivityMode.OFFLINE
        self.last_check: Optional[ConnectivityMetrics] = None
        self.connectivity_history = []
        
        logger.info("Connectivity manager initialized")
    
    async def detect_connectivity(self) -> ConnectivityMode:
        """
        Comprehensive connectivity detection
        Returns the current network mode
        """
        # Check internet reachability
        internet_available = await self._check_internet_reachable()
        
        if not internet_available:
            # Check for mesh peers
            has_mesh_peers = await self._check_mesh_available()
            if has_mesh_peers:
                logger.info("No internet, but mesh peers available")
                return ConnectivityMode.MESH_ONLY
            else:
                logger.info("Fully offline - no internet or mesh")
                return ConnectivityMode.OFFLINE
        
        # Internet is available - check quality
        metrics = await self._measure_connection_quality()
        self.last_check = metrics
        self.connectivity_history.append(metrics)
        
        # Determine mode based on quality
        if self._is_stable_connection(metrics):
            logger.info(f"Stable connection - latency: {metrics.latency_ms}ms")
            return ConnectivityMode.ONLINE
        else:
            logger.info(f"Unstable connection - switching to intermittent mode")
            return ConnectivityMode.INTERMITTENT
    
    async def _check_internet_reachable(self) -> bool:
        """
        Test internet connectivity using multiple DNS servers
        """
        dns_servers = [
            ('8.8.8.8', 53),      # Google DNS
            ('1.1.1.1', 53),      # Cloudflare DNS
            ('208.67.222.222', 53) # OpenDNS
        ]
        
        for host, port in dns_servers:
            try:
                # Try to connect with 5 second timeout
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    return True
            except Exception as e:
                logger.debug(f"Failed to reach {host}: {e}")
                continue
        
        return False
    
    async def _measure_connection_quality(self) -> ConnectivityMetrics:
        """
        Measure latency, bandwidth, packet loss
        """
        latency = await self._measure_latency()
        bandwidth = await self._measure_bandwidth()
        packet_loss = await self._measure_packet_loss()
        
        return ConnectivityMetrics(
            is_reachable=True,
            latency_ms=latency,
            bandwidth_mbps=bandwidth,
            packet_loss=packet_loss,
            jitter_ms=None,  # TODO: Implement jitter measurement
            timestamp=time.time()
        )
    
    async def _measure_latency(self) -> float:
        """
        Measure round-trip latency to central server
        """
        try:
            start = time.time()
            
            # Try to connect to server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            # TODO: Replace with actual server address
            sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            
            end = time.time()
            latency_ms = (end - start) * 1000
            return latency_ms
        except Exception as e:
            logger.warning(f"Latency measurement failed: {e}")
            return float('inf')
    
    async def _measure_bandwidth(self) -> float:
        """
        Estimate available bandwidth (simplified)
        """
        # TODO: Implement actual bandwidth test
        # For now, return a placeholder
        return 1.0  # 1 Mbps placeholder
    
    async def _measure_packet_loss(self) -> float:
        """
        Measure packet loss percentage
        """
        # TODO: Implement packet loss measurement
        return 0.0  # Placeholder
    
    def _is_stable_connection(self, metrics: ConnectivityMetrics) -> bool:
        """
        Determine if connection is stable enough for real-time FL
        """
        if metrics.latency_ms is None or metrics.bandwidth_mbps is None:
            return False
        
        # Good connection criteria:
        # - Latency < 1000ms
        # - Bandwidth > 100 kbps
        # - Packet loss < 5%
        return (
            metrics.latency_ms < self.latency_threshold and
            metrics.bandwidth_mbps > self.bandwidth_threshold and
            metrics.packet_loss < 0.05
        )
    
    async def _check_mesh_available(self) -> bool:
        """
        Check if any mesh peers are available
        """
        # TODO: Implement peer discovery
        # Check for Bluetooth, Wi-Fi Direct, LoRaWAN peers
        return False
    
    def select_sync_strategy(self) -> SyncStrategy:
        """
        Choose optimal synchronization strategy based on current mode
        """
        if self.current_mode == ConnectivityMode.ONLINE:
            return SyncStrategy.REALTIME
        elif self.current_mode == ConnectivityMode.INTERMITTENT:
            return SyncStrategy.BATCH
        elif self.current_mode == ConnectivityMode.MESH_ONLY:
            return SyncStrategy.MESH
        else:  # OFFLINE
            return SyncStrategy.SNEAKERNET
    
    async def continuous_monitoring(self):
        """
        Background task that continuously monitors connectivity
        """
        while True:
            try:
                new_mode = await self.detect_connectivity()
                
                if new_mode != self.current_mode:
                    logger.info(f"Connectivity changed: {self.current_mode.value} → {new_mode.value}")
                    self.current_mode = new_mode
                    
                    # Notify system of mode change
                    await self._notify_mode_change(new_mode)
                
            except Exception as e:
                logger.error(f"Connectivity check failed: {e}")
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)
    
    async def _notify_mode_change(self, new_mode: ConnectivityMode):
        """
        Notify other components of connectivity mode change
        """
        # TODO: Implement event broadcasting
        pass
    
    def get_status_report(self) -> Dict:
        """
        Generate connectivity status report
        """
        return {
            'current_mode': self.current_mode.value,
            'last_check': self.last_check.__dict__ if self.last_check else None,
            'sync_strategy': self.select_sync_strategy().value,
            'history_length': len(self.connectivity_history),
        }


# Singleton instance
_connectivity_manager: Optional[AdaptiveConnectivityManager] = None


def get_connectivity_manager() -> AdaptiveConnectivityManager:
    """Get or create the global connectivity manager instance"""
    global _connectivity_manager
    if _connectivity_manager is None:
        _connectivity_manager = AdaptiveConnectivityManager()
    return _connectivity_manager
