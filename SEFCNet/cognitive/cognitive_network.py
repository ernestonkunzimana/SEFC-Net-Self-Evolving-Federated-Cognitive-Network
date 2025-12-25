"""
Cognitive Network Architecture for SEFCNet
==========================================
Multi-level cognitive hierarchy for self-aware federated learning
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .memory_systems import EpisodicMemory, SemanticMemory, ProceduralMemory
from .meta_cognition import MetaCognition

logger = logging.getLogger(__name__)


class CognitiveNetwork:
    """
    Cognitive Network Architecture
    Implements multi-level cognitive hierarchy:
    - Perception Layer: Input processing
    - Reasoning Layer: Pattern recognition and decision making
    - Action Layer: Execution and feedback
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cognitive network"""
        self.config = config or {}
        
        # Initialize mandatory memory systems
        self.episodic_memory = EpisodicMemory(self.config.get('episodic', {}))
        self.semantic_memory = SemanticMemory(self.config.get('semantic', {}))
        self.procedural_memory = ProceduralMemory(self.config.get('procedural', {}))
        self.meta_cognition = MetaCognition(self.config.get('meta', {}))
        
        # Cognitive layers
        self.perception_weights = np.random.randn(100, 50)  # Simplified
        self.reasoning_weights = np.random.randn(50, 25)
        self.action_weights = np.random.randn(25, 10)
        
        logger.info("Cognitive Network initialized (MANDATORY)")
    
    def process_federated_round(
        self,
        round_data: Dict[str, Any],
        model_updates: List[np.ndarray],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Process a federated learning round through cognitive hierarchy.
        
        This is MANDATORY for all federated learning operations.
        """
        logger.info("Processing federated round through cognitive network")
        
        # Perception Layer: Process inputs
        perception_output = self._perception_layer(round_data, model_updates)
        
        # Reasoning Layer: Make decisions using memory
        reasoning_output = self._reasoning_layer(perception_output, performance_metrics)
        
        # Action Layer: Execute decisions
        action_output = self._action_layer(reasoning_output, round_data)
        
        # Meta-Cognition: Assess and improve
        meta_state = self.meta_cognition.assess_knowledge(
            performance_metrics,
            [round_data]
        )
        
        # Store in episodic memory
        self.episodic_memory.store_episode(
            event=f"federated_round_{round_data.get('round_id', 0)}",
            context=round_data,
            outcome=performance_metrics,
            importance=self._calculate_importance(performance_metrics)
        )
        
        # Update semantic memory with patterns
        if performance_metrics.get('improvement', 0) > 0.1:
            pattern_features = self._extract_pattern_features(round_data, performance_metrics)
            self.semantic_memory.store_pattern(
                pattern_type='successful_round',
                features=pattern_features
            )
        
        # Update procedural memory
        if action_output.get('action_taken'):
            self.procedural_memory.store_rule(
                condition=perception_output,
                action=action_output['action'],
                parameters=action_output.get('parameters', {}),
                success=performance_metrics.get('success', False)
            )
        
        return {
            'perception': perception_output,
            'reasoning': reasoning_output,
            'action': action_output,
            'meta_cognition': {
                'confidence': meta_state.confidence,
                'uncertainty': meta_state.uncertainty,
                'strategy': meta_state.strategy,
                'should_adapt': self.meta_cognition.should_adapt(),
                'recommendations': self.meta_cognition.get_adaptation_recommendations()
            },
            'memory_updates': {
                'episodic': len(self.episodic_memory.episodes),
                'semantic': len(self.semantic_memory.patterns),
                'procedural': len(self.procedural_memory.rules)
            }
        }
    
    def _perception_layer(
        self,
        round_data: Dict[str, Any],
        model_updates: List[np.ndarray]
    ) -> Dict[str, Any]:
        """Perception layer: Process and encode inputs"""
        # Extract features from round data
        features = np.array([
            round_data.get('num_nodes', 0),
            round_data.get('round_id', 0),
            len(model_updates),
            np.mean([len(u) for u in model_updates]) if model_updates else 0
        ])
        
        # Process through perception network (simplified)
        # perception_weights shape is (output_dim, input_dim)
        # We need input_dim features for the matrix multiplication
        input_dim = self.perception_weights.shape[1]
        
        # Pad or truncate features to match input dimension
        if len(features) > input_dim:
            features = features[:input_dim]
        elif len(features) < input_dim:
            features = np.pad(features, (0, input_dim - len(features)), mode='constant')
        
        # Reshape features to column vector for matrix multiplication: (input_dim, 1)
        features = features.reshape(-1, 1)
        # Matrix multiplication: (output_dim, input_dim) @ (input_dim, 1) = (output_dim, 1)
        perception_output = np.tanh(self.perception_weights @ features).flatten()
        
        return {
            'features': features.tolist(),
            'encoded': perception_output.tolist(),
            'num_updates': len(model_updates),
            'update_sizes': [len(u) for u in model_updates]
        }
    
    def _reasoning_layer(
        self,
        perception_output: Dict[str, Any],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Reasoning layer: Make decisions using memory"""
        # Retrieve relevant episodic memories
        similar_episodes = self.episodic_memory.retrieve_similar_episodes(
            perception_output,
            top_k=3
        )
        
        # Retrieve relevant semantic patterns
        pattern_features = np.array(perception_output.get('encoded', [0.0] * 50))
        similar_patterns = self.semantic_memory.retrieve_patterns(
            pattern_features,
            top_k=3
        )
        
        # Retrieve relevant procedural rules
        procedural_rule = self.procedural_memory.retrieve_rule(perception_output)
        
        # Make decision based on memories
        decision = self._make_decision(
            similar_episodes,
            similar_patterns,
            procedural_rule,
            performance_metrics
        )
        
        return {
            'decision': decision,
            'episodes_used': len(similar_episodes),
            'patterns_used': len(similar_patterns),
            'rule_used': procedural_rule is not None,
            'reasoning_path': self._explain_reasoning(similar_episodes, similar_patterns, procedural_rule)
        }
    
    def _action_layer(
        self,
        reasoning_output: Dict[str, Any],
        round_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Action layer: Execute decisions"""
        decision = reasoning_output.get('decision', {})
        action = decision.get('action', 'continue')
        
        if action == 'adapt':
            # Adapt learning parameters
            parameters = {
                'learning_rate': decision.get('learning_rate', 0.01),
                'aggregation_weight': decision.get('aggregation_weight', 1.0)
            }
            return {
                'action_taken': True,
                'action': 'adapt',
                'parameters': parameters
            }
        elif action == 'explore':
            # Explore new strategies
            return {
                'action_taken': True,
                'action': 'explore',
                'parameters': {'exploration_rate': 0.1}
            }
        else:
            return {
                'action_taken': False,
                'action': 'continue',
                'parameters': {}
            }
    
    def _make_decision(
        self,
        episodes: List,
        patterns: List,
        rule: Optional[Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Make decision based on cognitive memories"""
        # If we have a successful procedural rule, use it
        if rule and rule.success_rate > 0.7:
            return {
                'action': rule.action,
                'learning_rate': rule.parameters.get('learning_rate', 0.01),
                'aggregation_weight': rule.parameters.get('aggregation_weight', 1.0),
                'confidence': rule.success_rate
            }
        
        # If we have similar successful episodes, learn from them
        if episodes:
            best_episode = max(episodes, key=lambda e: e.importance)
            if best_episode.outcome.get('success', False):
                return {
                    'action': 'adapt',
                    'learning_rate': best_episode.context.get('learning_rate', 0.01),
                    'aggregation_weight': 1.0,
                    'confidence': best_episode.importance
                }
        
        # Default: continue with current strategy
        return {
            'action': 'continue',
            'learning_rate': 0.01,
            'aggregation_weight': 1.0,
            'confidence': 0.5
        }
    
    def _explain_reasoning(
        self,
        episodes: List,
        patterns: List,
        rule: Optional[Any]
    ) -> str:
        """Generate human-readable explanation of reasoning"""
        explanations = []
        
        if rule:
            explanations.append(f"Using procedural rule: {rule.action} (success rate: {rule.success_rate:.2f})")
        
        if episodes:
            explanations.append(f"Retrieved {len(episodes)} similar past episodes")
        
        if patterns:
            explanations.append(f"Found {len(patterns)} relevant semantic patterns")
        
        return "; ".join(explanations) if explanations else "No relevant memories found"
    
    def _calculate_importance(self, metrics: Dict[str, float]) -> float:
        """Calculate importance of a round"""
        improvement = metrics.get('improvement', 0.0)
        performance = metrics.get('performance', 0.5)
        return min(1.0, max(0.0, 0.6 * abs(improvement) + 0.4 * performance))
    
    def _extract_pattern_features(
        self,
        round_data: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> np.ndarray:
        """Extract features for semantic pattern storage"""
        return np.array([
            round_data.get('num_nodes', 0) / 100.0,
            metrics.get('performance', 0.0),
            metrics.get('improvement', 0.0),
            metrics.get('convergence_rate', 0.0)
        ])

