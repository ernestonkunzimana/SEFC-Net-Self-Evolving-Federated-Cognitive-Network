"""
Test script for edge resilience capabilities
Validates offline training, connectivity detection, and batch synchronization
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_connectivity_detection():
    """Test connectivity detection capabilities"""
    logger.info("=" * 60)
    logger.info("TEST 1: Connectivity Detection")
    logger.info("=" * 60)
    
    try:
        from edge_resilience.connectivity_detector import get_connectivity_manager
        
        manager = get_connectivity_manager()
        logger.info("✅ Connectivity manager created")
        
        # Detect current connectivity
        mode = await manager.detect_connectivity()
        logger.info(f"✅ Current connectivity mode: {mode.value}")
        
        # Get status report
        status = manager.get_status_report()
        logger.info(f"✅ Status report: {status}")
        
        # Test sync strategy selection
        strategy = manager.select_sync_strategy()
        logger.info(f"✅ Selected sync strategy: {strategy.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Connectivity detection test failed: {e}")
        return False


def test_offline_training():
    """Test offline training capabilities"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Offline Training")
    logger.info("=" * 60)
    
    try:
        from edge_resilience.offline_trainer import OfflineTrainer
        
        # Create trainer
        trainer = OfflineTrainer(
            node_id="test_node_001",
            local_data_path="./test_data",
            checkpoint_dir="./test_checkpoints"
        )
        logger.info("✅ Offline trainer created")
        
        # Run short training session
        results = trainer.train_autonomously(epochs=5, batch_size=32)
        logger.info("✅ Training completed")
        
        # Get training status
        status = trainer.get_training_status()
        logger.info(f"✅ Training status: {status}")
        
        # Prepare sync package
        sync_package = trainer.prepare_sync_package()
        logger.info(f"✅ Sync package prepared: {len(sync_package)} items")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Offline training test failed: {e}")
        return False


def test_batch_synchronization():
    """Test batch synchronization capabilities"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Batch Synchronization")
    logger.info("=" * 60)
    
    try:
        from edge_resilience.batch_synchronizer import BatchSynchronizer
        
        # Create synchronizer
        sync = BatchSynchronizer(
            node_id="test_node_001",
            queue_dir="./test_queue",
            sync_window=3600,
            compression_ratio=10
        )
        logger.info("✅ Batch synchronizer created")
        
        # Queue some model updates
        for i in range(3):
            update_id = sync.queue_model_update(
                local_model_weights={'layer1': [1.0, 2.0, 3.0]},
                training_metadata={'epoch': i, 'loss': 0.5 - i*0.1}
            )
            logger.info(f"✅ Update {i+1} queued: {update_id}")
        
        # Get queue status
        status = sync.get_queue_status()
        logger.info(f"✅ Queue status: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Batch synchronization test failed: {e}")
        return False


async def run_all_tests():
    """Run all edge resilience tests"""
    logger.info("\n" + "=" * 60)
    logger.info("SEFC-Net Edge Resilience Test Suite")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: Connectivity Detection
    result1 = await test_connectivity_detection()
    results.append(("Connectivity Detection", result1))
    
    # Test 2: Offline Training
    result2 = test_offline_training()
    results.append(("Offline Training", result2))
    
    # Test 3: Batch Synchronization
    result3 = test_batch_synchronization()
    results.append(("Batch Synchronization", result3))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All edge resilience tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
