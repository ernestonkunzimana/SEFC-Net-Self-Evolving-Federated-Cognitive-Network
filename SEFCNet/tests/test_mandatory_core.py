"""
Tests for Mandatory Core System
================================
Ensure all mandatory components work together
"""

import pytest
import numpy as np
from mandatory_core import SEFCNetMandatoryCore


def test_mandatory_core_initialization():
    """Test that all mandatory components initialize"""
    core = SEFCNetMandatoryCore()
    
    # All components must be initialized
    assert core.quantum_ris is not None, "Quantum-RIS must be initialized"
    assert core.cognitive_fl is not None, "Cognitive FL must be initialized"
    assert core.biological_evolution is not None, "Biological evolution must be initialized"
    assert core.autonomous_agents is not None, "Autonomous agents must be initialized"
    assert core.privacy_layer is not None, "Privacy layer must be initialized"
    assert core.cross_modal is not None, "Cross-modal must be initialized"
    assert core.explainable is not None, "Explainable must be initialized"
    assert core.sustainable is not None, "Sustainable must be initialized"
    assert core.drift_detector is not None, "Drift detector must be initialized"
    assert core.attention_aggregation is not None, "Attention aggregation must be initialized"


def test_mandatory_round_processing():
    """Test that all components are used in round processing"""
    core = SEFCNetMandatoryCore()
    
    # Prepare test data
    nodes = [
        {'id': 'node1', 'bandwidth': 1.0, 'computation': 0.5},
        {'id': 'node2', 'bandwidth': 1.0, 'computation': 0.5}
    ]
    model_updates = [np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])]
    performance_metrics = {'node_0': 0.8, 'node_1': 0.75, 'accuracy': 0.77}
    
    # Process round
    result = core.process_federated_round(
        round_id=1,
        nodes=nodes,
        model_updates=model_updates,
        performance_metrics=performance_metrics
    )
    
    # All components must be used
    assert 'quantum_ris' in result['mandatory_components_used']
    assert 'cognitive' in result['mandatory_components_used']
    assert 'biological' in result['mandatory_components_used']
    assert 'autonomous' in result['mandatory_components_used']
    assert 'privacy' in result['mandatory_components_used']
    assert 'cross_modal' in result['mandatory_components_used']
    assert 'explainable' in result['mandatory_components_used']
    assert 'sustainable' in result['mandatory_components_used']
    assert 'adaptation' in result['mandatory_components_used']
    assert 'aggregation' in result['mandatory_components_used']
    
    assert len(result['mandatory_components_used']) == 10, "All 10 components must be used"


def test_system_status():
    """Test system status reporting"""
    core = SEFCNetMandatoryCore()
    status = core.get_system_status()
    
    assert status['all_mandatory'] is True
    assert status['total_components'] == 10
    assert all([
        status['quantum_ris']['initialized'],
        status['cognitive']['initialized'],
        status['biological']['initialized'],
        status['autonomous']['initialized'],
        status['privacy']['initialized'],
        status['cross_modal']['initialized'],
        status['explainable']['initialized'],
        status['sustainable']['initialized'],
        status['adaptation']['initialized'],
        status['aggregation']['initialized']
    ]), "All components must be initialized"

