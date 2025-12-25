"""
SEFC-Net Edge Resilience Module
================================

Offline-first, ultra-resilient federated learning for ANY environment:
- Urban centers (high bandwidth, reliable power)
- Rural villages (intermittent connectivity, solar power)
- Remote areas (zero internet, satellite-only)
- Disaster zones (infrastructure damaged)
- Military/tactical (intentionally offline)

Three-Tier Resilience Model:
- TIER 1: FULLY CONNECTED - Real-time federation, continuous updates
- TIER 2: INTERMITTENT - Batch sync, mesh networking, local training
- TIER 3: ZERO CONNECTIVITY - Autonomous operation, sneakernet sync

Module Components:
- connectivity_detector.py: Detect network state (online/offline/intermittent)
- offline_trainer.py: Continue FL training without central server
- batch_synchronizer.py: Queue updates for opportunistic sync
- mesh_coordinator.py: Peer-to-peer federation between nearby nodes
- compression_engine.py: Extreme model compression for limited bandwidth
- differential_sync.py: Only sync model deltas, not full weights
- sneakernet_manager.py: Physical media transfers (USB/SD)
- power_optimizer.py: Solar/battery-aware training schedules
- local_aggregator.py: Aggregate within local clusters offline
- conflict_resolver.py: Merge models when reconnecting after long offline
- emergency_fallback.py: Pre-trained models for critical services
"""

from enum import Enum

__version__ = "1.0.0"
__author__ = "SEFC-Net Team"

# Connectivity modes
class ConnectivityMode(Enum):
    """Network connectivity states"""
    ONLINE = "online"              # Full internet, low latency
    INTERMITTENT = "intermittent"  # Periodic connection
    OFFLINE = "offline"            # Zero connectivity
    MESH_ONLY = "mesh_only"        # Local peer-to-peer only

# Hardware tiers
class HardwareTier(Enum):
    """Deployment hardware tiers"""
    TIER_1_URBAN = "tier1_urban"       # High resources (GPU, 5G)
    TIER_2_RURAL = "tier2_rural"       # Medium resources (ARM, solar)
    TIER_3_REMOTE = "tier3_remote"     # Minimal resources (embedded, satellite)

# Sync strategies
class SyncStrategy(Enum):
    """Model synchronization strategies"""
    REALTIME = "realtime"          # Continuous sync (Tier 1)
    BATCH = "batch"                # Periodic batch uploads (Tier 2)
    SNEAKERNET = "sneakernet"      # Physical media transfer (Tier 3)
    MESH = "mesh"                  # Peer-to-peer sync (Tier 2/3)
    SATELLITE = "satellite"        # Emergency satellite sync (Tier 3)

__all__ = [
    'ConnectivityMode',
    'HardwareTier',
    'SyncStrategy',
]
