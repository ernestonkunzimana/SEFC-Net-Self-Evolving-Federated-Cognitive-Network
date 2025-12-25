"""
Meta-Cognition System for SEFCNet
==================================
Self-awareness and self-monitoring for cognitive federated learning
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MetaCognitiveState:
    """Represents meta-cognitive awareness state"""
    confidence: float
    uncertainty: float
    knowledge_gaps: List[str]
    learning_rate: float
    strategy: str
    timestamp: datetime


class MetaCognition:
    """
    Meta-Cognition System
    Monitors and improves its own learning processes.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize meta-cognition system"""
        self.config = config or {}
        self.current_state: Optional[MetaCognitiveState] = None
        self.state_history: List[MetaCognitiveState] = []
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        logger.info("Meta-Cognition initialized (MANDATORY)")
    
    def assess_knowledge(
        self,
        performance_metrics: Dict[str, float],
        learning_history: List[Dict[str, Any]]
    ) -> MetaCognitiveState:
        """
        Assess current knowledge state and learning effectiveness.
        
        Returns meta-cognitive state with confidence, uncertainty, and strategy.
        """
        # Calculate confidence based on performance stability
        confidence = self._calculate_confidence(performance_metrics, learning_history)
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(performance_metrics, learning_history)
        
        # Identify knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps(performance_metrics, learning_history)
        
        # Determine optimal learning rate
        learning_rate = self._determine_learning_rate(confidence, uncertainty)
        
        # Select learning strategy
        strategy = self._select_strategy(confidence, uncertainty, knowledge_gaps)
        
        state = MetaCognitiveState(
            confidence=confidence,
            uncertainty=uncertainty,
            knowledge_gaps=knowledge_gaps,
            learning_rate=learning_rate,
            strategy=strategy,
            timestamp=datetime.now()
        )
        
        self.current_state = state
        self.state_history.append(state)
        
        logger.info(
            f"Meta-cognitive assessment: confidence={confidence:.2f}, "
            f"uncertainty={uncertainty:.2f}, strategy={strategy}"
        )
        
        return state
    
    def _calculate_confidence(
        self,
        metrics: Dict[str, float],
        history: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in current knowledge"""
        if not history:
            return 0.5  # Neutral confidence
        
        # Confidence based on:
        # - Performance stability (low variance)
        # - Recent improvements
        # - Consistency across metrics
        
        recent_performances = [h.get('performance', 0.0) for h in history[-10:]]
        if recent_performances:
            variance = np.var(recent_performances)
            mean_performance = np.mean(recent_performances)
            
            # Low variance + high performance = high confidence
            stability_score = 1.0 / (1.0 + variance)
            performance_score = mean_performance
            
            confidence = 0.6 * stability_score + 0.4 * performance_score
        else:
            confidence = 0.5
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_uncertainty(
        self,
        metrics: Dict[str, float],
        history: List[Dict[str, Any]]
    ) -> float:
        """Calculate uncertainty in predictions"""
        if not history:
            return 0.8  # High uncertainty initially
        
        # Uncertainty based on:
        # - Prediction errors
        # - Model disagreement
        # - Data distribution shifts
        
        prediction_errors = [
            h.get('prediction_error', 0.0) for h in history[-10:]
            if 'prediction_error' in h
        ]
        
        if prediction_errors:
            mean_error = np.mean(prediction_errors)
            uncertainty = min(1.0, mean_error)
        else:
            uncertainty = 0.5
        
        return uncertainty
    
    def _identify_knowledge_gaps(
        self,
        metrics: Dict[str, float],
        history: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify areas where knowledge is lacking"""
        gaps = []
        
        # Check for low performance in specific areas
        if metrics.get('accuracy', 1.0) < 0.7:
            gaps.append('accuracy')
        
        if metrics.get('generalization', 1.0) < 0.7:
            gaps.append('generalization')
        
        if metrics.get('robustness', 1.0) < 0.7:
            gaps.append('robustness')
        
        # Check for high uncertainty
        if self.current_state and self.current_state.uncertainty > 0.7:
            gaps.append('uncertainty')
        
        # Check for distribution shifts
        if history:
            recent_dist = history[-1].get('data_distribution', {})
            if recent_dist.get('shift_detected', False):
                gaps.append('distribution_shift')
        
        return gaps
    
    def _determine_learning_rate(
        self,
        confidence: float,
        uncertainty: float
    ) -> float:
        """Determine optimal learning rate based on meta-cognitive state"""
        base_lr = self.config.get('base_learning_rate', 0.01)
        
        # High uncertainty -> increase learning rate
        # Low confidence -> increase learning rate
        # High confidence + low uncertainty -> decrease learning rate (fine-tuning)
        
        if uncertainty > 0.7 or confidence < 0.5:
            # Exploration phase - higher learning rate
            learning_rate = base_lr * 2.0
        elif confidence > 0.8 and uncertainty < 0.3:
            # Exploitation phase - lower learning rate
            learning_rate = base_lr * 0.5
        else:
            learning_rate = base_lr
        
        return learning_rate
    
    def _select_strategy(
        self,
        confidence: float,
        uncertainty: float,
        knowledge_gaps: List[str]
    ) -> str:
        """Select optimal learning strategy"""
        if uncertainty > 0.7:
            return 'exploration'  # Explore more
        elif confidence > 0.8 and not knowledge_gaps:
            return 'exploitation'  # Exploit current knowledge
        elif 'distribution_shift' in knowledge_gaps:
            return 'adaptation'  # Adapt to new distribution
        elif 'generalization' in knowledge_gaps:
            return 'regularization'  # Improve generalization
        else:
            return 'balanced'  # Balanced exploration-exploitation
    
    def should_adapt(self) -> bool:
        """Determine if system should adapt based on meta-cognitive state"""
        if not self.current_state:
            return False
        
        # Adapt if:
        # - Low confidence
        # - High uncertainty
        # - Knowledge gaps detected
        
        should_adapt = (
            self.current_state.confidence < self.confidence_threshold or
            self.current_state.uncertainty > 0.7 or
            len(self.current_state.knowledge_gaps) > 0
        )
        
        return should_adapt
    
    def get_adaptation_recommendations(self) -> List[str]:
        """Get recommendations for adaptation"""
        if not self.current_state:
            return []
        
        recommendations = []
        
        if self.current_state.confidence < self.confidence_threshold:
            recommendations.append("Increase training data diversity")
        
        if self.current_state.uncertainty > 0.7:
            recommendations.append("Collect more data or reduce model complexity")
        
        for gap in self.current_state.knowledge_gaps:
            if gap == 'accuracy':
                recommendations.append("Focus on improving model accuracy")
            elif gap == 'generalization':
                recommendations.append("Apply regularization techniques")
            elif gap == 'robustness':
                recommendations.append("Improve model robustness to perturbations")
            elif gap == 'distribution_shift':
                recommendations.append("Adapt to new data distribution")
        
        return recommendations

