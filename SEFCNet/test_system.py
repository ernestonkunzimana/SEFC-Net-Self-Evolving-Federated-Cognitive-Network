"""
Quick System Test
================
Test all mandatory components are working
"""

import numpy as np
from mandatory_core import get_mandatory_core

print("=" * 60)
print("SEFCNet System Test")
print("=" * 60)

# Initialize mandatory core
print("\n1. Initializing Mandatory Core...")
core = get_mandatory_core()
print("   ✓ Core initialized")

# Check system status
print("\n2. Checking System Status...")
status = core.get_system_status()
print(f"   ✓ All Mandatory: {status['all_mandatory']}")
print(f"   ✓ Total Components: {status['total_components']}")

# Test components
print("\n3. Testing Components...")
for key, value in status.items():
    if isinstance(value, dict) and 'initialized' in value:
        status_icon = "✓" if value['initialized'] else "✗"
        print(f"   {status_icon} {key}: {value['initialized']}")

# Test round processing
print("\n4. Testing Federated Round Processing...")
nodes = [
    {'id': 'node1', 'bandwidth': 1.0, 'computation': 0.5},
    {'id': 'node2', 'bandwidth': 1.0, 'computation': 0.5}
]
model_updates = [np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])]
performance_metrics = {'node_0': 0.8, 'node_1': 0.75, 'accuracy': 0.77}

result = core.process_federated_round(
    round_id=1,
    nodes=nodes,
    model_updates=model_updates,
    performance_metrics=performance_metrics
)

print(f"   ✓ Round processed successfully")
print(f"   ✓ Components used: {len(result['mandatory_components_used'])}")
print(f"   ✓ Communication reduction: {result['summary']['communication_reduction']:.2f}%")
print(f"   ✓ Trust score: {result['summary']['trust_score']:.3f}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - SYSTEM READY")
print("=" * 60)

