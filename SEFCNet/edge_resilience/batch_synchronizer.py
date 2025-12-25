"""
Batch Synchronizer
==================

Smart batching system for intermittent connectivity environments.

Features:
- Queue model updates locally until connectivity available
- Compress updates using quantization + pruning
- Calculate differential (only send changes)
- Opportunistic upload when network detected
- Resume interrupted transfers

Used for:
- Rural clinics with 2G/3G connectivity
- Agricultural sensors with daily sync windows
- Mobile nodes (vehicles, field workers)
"""

import os
import json
import time
import gzip
import hashlib
import logging
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ModelUpdate:
    """Represents a queued model update"""
    update_id: str
    node_id: str
    timestamp: float
    model_delta: bytes  # Compressed differential
    metadata: Dict
    size_bytes: int
    compressed: bool


class BatchSynchronizer:
    """
    Manages batched synchronization for intermittent connectivity
    """
    
    def __init__(
        self,
        node_id: str,
        queue_dir: str = "./sync_queue",
        sync_window: int = 3600,  # 1 hour default sync window
        compression_ratio: int = 10,  # Target 10x compression
        max_queue_size_mb: int = 100,  # Max 100MB queue
    ):
        self.node_id = node_id
        self.queue_dir = Path(queue_dir)
        self.sync_window = sync_window
        self.compression_ratio = compression_ratio
        self.max_queue_size_mb = max_queue_size_mb
        
        # Create queue directory
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
        # Pending updates queue
        self.pending_updates: List[ModelUpdate] = []
        self.last_synced_weights = None
        self.last_sync_time: Optional[float] = None
        
        # Statistics
        self.total_uploads = 0
        self.total_bytes_uploaded = 0
        self.failed_uploads = 0
        
        # Load existing queue from disk
        self._load_queue_from_disk()
        
        logger.info(f"Batch synchronizer initialized for node {node_id}")
    
    def queue_model_update(
        self,
        local_model_weights: Dict,
        training_metadata: Dict
    ) -> str:
        """
        Store model update locally until connectivity window opens
        
        Args:
            local_model_weights: Current model weights
            training_metadata: Training session metadata
        
        Returns:
            update_id: Unique identifier for this update
        """
        # Generate unique update ID
        update_id = self._generate_update_id()
        
        logger.info(f"Queueing model update {update_id}")
        
        # Compress weights
        compressed = self._compress_weights(local_model_weights)
        
        # Calculate differential (only changes since last sync)
        delta = self._calculate_delta(compressed)
        
        # Create update object
        update = ModelUpdate(
            update_id=update_id,
            node_id=self.node_id,
            timestamp=time.time(),
            model_delta=delta,
            metadata=training_metadata,
            size_bytes=len(delta),
            compressed=True,
        )
        
        # Add to queue
        self.pending_updates.append(update)
        
        # Persist to disk
        self._save_update_to_disk(update)
        
        # Check queue size
        self._enforce_queue_limits()
        
        logger.info(
            f"Update queued: {update.size_bytes / 1024:.2f} KB "
            f"({len(self.pending_updates)} pending)"
        )
        
        return update_id
    
    def _compress_weights(self, weights: Dict) -> bytes:
        """
        Compress model weights using multiple techniques:
        1. Quantization: Float32 → Int8 (4x reduction)
        2. Pruning: Remove small weights (2-5x reduction)
        3. Gzip: Lossless compression (2-3x reduction)
        
        Target: 10-100x compression
        """
        # TODO: Implement actual quantization and pruning
        # For now, just serialize and compress
        
        # Serialize weights to JSON
        weights_json = json.dumps(weights, default=str)
        weights_bytes = weights_json.encode('utf-8')
        
        # Gzip compression
        compressed = gzip.compress(weights_bytes, compresslevel=9)
        
        compression_ratio = len(weights_bytes) / len(compressed)
        logger.debug(f"Compression ratio: {compression_ratio:.2f}x")
        
        return compressed
    
    def _calculate_delta(self, current_weights: bytes) -> bytes:
        """
        Calculate differential between current and last synced weights
        Only send the changes, not full model
        """
        if self.last_synced_weights is None:
            # First sync - send full model
            logger.debug("First sync - sending full model")
            return current_weights
        
        # TODO: Implement actual differential calculation
        # For now, just return current weights
        # In production, use techniques like:
        # - XOR difference for binary data
        # - Weight-wise subtraction
        # - Sparse representation of changes
        
        return current_weights
    
    def _generate_update_id(self) -> str:
        """Generate unique update identifier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"{self.node_id}_{timestamp}_{random_suffix}"
    
    def _save_update_to_disk(self, update: ModelUpdate):
        """Persist update to disk for crash recovery"""
        update_file = self.queue_dir / f"{update.update_id}.json"
        
        update_data = {
            'update_id': update.update_id,
            'node_id': update.node_id,
            'timestamp': update.timestamp,
            'metadata': update.metadata,
            'size_bytes': update.size_bytes,
            'compressed': update.compressed,
        }
        
        # Save metadata
        with open(update_file, 'w') as f:
            json.dump(update_data, f, indent=2)
        
        # Save delta separately (binary)
        delta_file = self.queue_dir / f"{update.update_id}.delta"
        with open(delta_file, 'wb') as f:
            f.write(update.model_delta)
    
    def _load_queue_from_disk(self):
        """Load existing queue from disk on startup"""
        update_files = list(self.queue_dir.glob("*.json"))
        
        for update_file in update_files:
            try:
                with open(update_file, 'r') as f:
                    update_data = json.load(f)
                
                # Load delta
                delta_file = self.queue_dir / f"{update_data['update_id']}.delta"
                if delta_file.exists():
                    with open(delta_file, 'rb') as f:
                        delta = f.read()
                    
                    # Reconstruct update object
                    update = ModelUpdate(
                        update_id=update_data['update_id'],
                        node_id=update_data['node_id'],
                        timestamp=update_data['timestamp'],
                        model_delta=delta,
                        metadata=update_data['metadata'],
                        size_bytes=update_data['size_bytes'],
                        compressed=update_data['compressed'],
                    )
                    
                    self.pending_updates.append(update)
            
            except Exception as e:
                logger.error(f"Failed to load update {update_file}: {e}")
        
        logger.info(f"Loaded {len(self.pending_updates)} pending updates from disk")
    
    def _enforce_queue_limits(self):
        """Ensure queue doesn't exceed size limits"""
        total_size_mb = sum(u.size_bytes for u in self.pending_updates) / (1024 * 1024)
        
        if total_size_mb > self.max_queue_size_mb:
            # Remove oldest updates
            updates_to_remove = []
            while total_size_mb > self.max_queue_size_mb and self.pending_updates:
                oldest = self.pending_updates.pop(0)
                updates_to_remove.append(oldest)
                total_size_mb -= oldest.size_bytes / (1024 * 1024)
            
            # Clean up disk
            for update in updates_to_remove:
                self._remove_update_from_disk(update.update_id)
            
            logger.warning(f"Queue limit exceeded - removed {len(updates_to_remove)} old updates")
    
    def _remove_update_from_disk(self, update_id: str):
        """Remove update files from disk"""
        update_file = self.queue_dir / f"{update_id}.json"
        delta_file = self.queue_dir / f"{update_id}.delta"
        
        update_file.unlink(missing_ok=True)
        delta_file.unlink(missing_ok=True)
    
    async def opportunistic_sync(self, connectivity_manager) -> Dict:
        """
        When connectivity detected, batch upload all pending updates
        
        Args:
            connectivity_manager: Connectivity detection service
        
        Returns:
            Sync results (success count, failed count, bytes uploaded)
        """
        if not self.pending_updates:
            logger.info("No pending updates to sync")
            return {'success': 0, 'failed': 0, 'bytes': 0}
        
        # Check if we have connectivity
        if not connectivity_manager.current_mode.value in ['online', 'intermittent']:
            logger.warning("No connectivity - deferring sync")
            return {'success': 0, 'failed': 0, 'bytes': 0}
        
        logger.info(f"Starting opportunistic sync of {len(self.pending_updates)} updates")
        
        success_count = 0
        failed_count = 0
        bytes_uploaded = 0
        
        # Upload each pending update
        for update in self.pending_updates[:]:  # Copy list to allow modification
            try:
                # Simulate upload
                # TODO: Implement actual HTTP/gRPC upload to server
                success = await self._upload_update(update)
                
                if success:
                    success_count += 1
                    bytes_uploaded += update.size_bytes
                    
                    # Remove from queue
                    self.pending_updates.remove(update)
                    self._remove_update_from_disk(update.update_id)
                    
                    logger.info(f"Update {update.update_id} uploaded successfully")
                else:
                    failed_count += 1
                    logger.warning(f"Update {update.update_id} upload failed")
            
            except Exception as e:
                logger.error(f"Upload error for {update.update_id}: {e}")
                failed_count += 1
        
        # Update statistics
        self.total_uploads += success_count
        self.total_bytes_uploaded += bytes_uploaded
        self.failed_uploads += failed_count
        self.last_sync_time = time.time()
        
        logger.info(
            f"Sync complete: {success_count} success, {failed_count} failed, "
            f"{bytes_uploaded / 1024:.2f} KB uploaded"
        )
        
        return {
            'success': success_count,
            'failed': failed_count,
            'bytes': bytes_uploaded,
        }
    
    async def _upload_update(self, update: ModelUpdate) -> bool:
        """
        Upload single update to server
        Returns True if successful
        """
        # TODO: Implement actual HTTP/gRPC upload
        # Should handle:
        # - Retries on transient failures
        # - Resume interrupted transfers
        # - Verify upload integrity
        
        # Placeholder: simulate upload
        import asyncio
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # 90% success rate for simulation
        return np.random.random() > 0.1
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        total_size = sum(u.size_bytes for u in self.pending_updates)
        
        return {
            'pending_updates': len(self.pending_updates),
            'queue_size_mb': total_size / (1024 * 1024),
            'oldest_update': min(
                (u.timestamp for u in self.pending_updates),
                default=None
            ),
            'total_uploads': self.total_uploads,
            'total_bytes_uploaded': self.total_bytes_uploaded,
            'failed_uploads': self.failed_uploads,
            'last_sync_time': self.last_sync_time,
        }
