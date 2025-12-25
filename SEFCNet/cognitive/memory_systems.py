"""
Cognitive Memory Systems for SEFCNet
====================================
Episodic, Semantic, and Procedural memory for cognitive federated learning
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class MemoryEpisode:
    """Represents an episodic memory"""
    event: str
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    timestamp: datetime
    importance: float = 1.0
    access_count: int = 0


@dataclass
class SemanticPattern:
    """Represents a semantic memory pattern"""
    pattern_type: str
    features: np.ndarray
    associations: List[str]
    strength: float
    last_accessed: datetime


@dataclass
class ProceduralRule:
    """Represents a procedural memory rule"""
    condition: Dict[str, Any]
    action: str
    parameters: Dict[str, Any]
    success_rate: float
    usage_count: int


class EpisodicMemory:
    """
    Episodic Memory System
    Remembers specific events and experiences in federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize episodic memory"""
        self.config = config or {}
        self.max_episodes = self.config.get('max_episodes', 1000)
        self.episodes: List[MemoryEpisode] = []
        self.importance_threshold = self.config.get('importance_threshold', 0.5)
        
        logger.info("Episodic Memory initialized (MANDATORY)")
    
    def store_episode(
        self,
        event: str,
        context: Dict[str, Any],
        outcome: Dict[str, Any],
        importance: Optional[float] = None
    ) -> MemoryEpisode:
        """Store a new episodic memory"""
        if importance is None:
            importance = self._calculate_importance(context, outcome)
        
        episode = MemoryEpisode(
            event=event,
            context=context,
            outcome=outcome,
            timestamp=datetime.now(),
            importance=importance
        )
        
        self.episodes.append(episode)
        
        # Maintain memory size
        if len(self.episodes) > self.max_episodes:
            self._forget_least_important()
        
        logger.debug(f"Stored episodic memory: {event}")
        return episode
    
    def retrieve_similar_episodes(
        self,
        query_context: Dict[str, Any],
        top_k: int = 5
    ) -> List[MemoryEpisode]:
        """Retrieve similar past episodes"""
        if not self.episodes:
            return []
        
        # Calculate similarity scores
        similarities = []
        for episode in self.episodes:
            similarity = self._calculate_similarity(query_context, episode.context)
            weighted_score = similarity * episode.importance * (1.0 + episode.access_count * 0.1)
            similarities.append((weighted_score, episode))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[0], reverse=True)
        retrieved = [ep for _, ep in similarities[:top_k]]
        
        # Update access counts
        for ep in retrieved:
            ep.access_count += 1
        
        return retrieved
    
    def _calculate_importance(
        self,
        context: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> float:
        """Calculate importance of an episode"""
        # Importance based on:
        # - Performance improvement
        # - Novelty
        # - Success/failure
        
        performance_change = outcome.get('performance_change', 0.0)
        novelty = context.get('novelty_score', 0.5)
        success = 1.0 if outcome.get('success', False) else 0.5
        
        importance = (
            0.4 * abs(performance_change) +
            0.3 * novelty +
            0.3 * success
        )
        
        return min(1.0, max(0.0, importance))
    
    def _calculate_similarity(
        self,
        context1: Dict[str, Any],
        context2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between contexts"""
        # Simple similarity based on common keys
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())
        
        if not keys1 or not keys2:
            return 0.0
        
        common_keys = keys1.intersection(keys2)
        if not common_keys:
            return 0.0
        
        # Calculate value similarity for common keys
        similarities = []
        for key in common_keys:
            val1 = context1[key]
            val2 = context2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                diff = abs(val1 - val2)
                max_val = max(abs(val1), abs(val2), 1.0)
                sim = 1.0 - min(1.0, diff / max_val)
                similarities.append(sim)
            elif val1 == val2:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _forget_least_important(self):
        """Forget least important episodes (memory management)"""
        # Sort by importance and access count
        self.episodes.sort(
            key=lambda e: e.importance * (1.0 + e.access_count * 0.1)
        )
        
        # Remove bottom 10%
        remove_count = max(1, len(self.episodes) // 10)
        self.episodes = self.episodes[remove_count:]


class SemanticMemory:
    """
    Semantic Memory System
    Stores general knowledge and patterns about federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize semantic memory"""
        self.config = config or {}
        self.patterns: Dict[str, SemanticPattern] = {}
        self.association_strength = self.config.get('association_strength', 0.5)
        
        logger.info("Semantic Memory initialized (MANDATORY)")
    
    def store_pattern(
        self,
        pattern_type: str,
        features: np.ndarray,
        associations: Optional[List[str]] = None
    ) -> SemanticPattern:
        """Store a semantic pattern"""
        pattern = SemanticPattern(
            pattern_type=pattern_type,
            features=features,
            associations=associations or [],
            strength=1.0,
            last_accessed=datetime.now()
        )
        
        pattern_key = f"{pattern_type}_{len(self.patterns)}"
        self.patterns[pattern_key] = pattern
        
        logger.debug(f"Stored semantic pattern: {pattern_type}")
        return pattern
    
    def retrieve_patterns(
        self,
        query_features: np.ndarray,
        pattern_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[SemanticPattern]:
        """Retrieve similar semantic patterns"""
        candidates = [
            p for p in self.patterns.values()
            if pattern_type is None or p.pattern_type == pattern_type
        ]
        
        if not candidates:
            return []
        
        # Calculate feature similarities
        similarities = []
        for pattern in candidates:
            similarity = self._feature_similarity(query_features, pattern.features)
            weighted_score = similarity * pattern.strength
            similarities.append((weighted_score, pattern))
        
        # Sort and return top-k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in similarities[:top_k]]
    
    def strengthen_association(
        self,
        pattern_key: str,
        associated_pattern: str
    ):
        """Strengthen association between patterns"""
        if pattern_key in self.patterns:
            pattern = self.patterns[pattern_key]
            if associated_pattern not in pattern.associations:
                pattern.associations.append(associated_pattern)
            pattern.strength += self.association_strength
            pattern.last_accessed = datetime.now()
    
    def _feature_similarity(
        self,
        features1: np.ndarray,
        features2: np.ndarray
    ) -> float:
        """Calculate similarity between feature vectors"""
        if features1.shape != features2.shape:
            # Pad or truncate to match
            min_len = min(len(features1), len(features2))
            features1 = features1[:min_len]
            features2 = features2[:min_len]
        
        # Cosine similarity
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class ProceduralMemory:
    """
    Procedural Memory System
    Stores learned procedures and optimization strategies.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize procedural memory"""
        self.config = config or {}
        self.rules: List[ProceduralRule] = []
        self.min_success_rate = self.config.get('min_success_rate', 0.6)
        
        logger.info("Procedural Memory initialized (MANDATORY)")
    
    def store_rule(
        self,
        condition: Dict[str, Any],
        action: str,
        parameters: Dict[str, Any],
        success: bool
    ) -> ProceduralRule:
        """Store or update a procedural rule"""
        # Check if similar rule exists
        existing_rule = self._find_similar_rule(condition, action)
        
        if existing_rule:
            # Update existing rule
            existing_rule.usage_count += 1
            # Update success rate (exponential moving average)
            alpha = 0.1
            existing_rule.success_rate = (
                alpha * (1.0 if success else 0.0) +
                (1 - alpha) * existing_rule.success_rate
            )
            return existing_rule
        else:
            # Create new rule
            rule = ProceduralRule(
                condition=condition,
                action=action,
                parameters=parameters,
                success_rate=1.0 if success else 0.0,
                usage_count=1
            )
            self.rules.append(rule)
            return rule
    
    def retrieve_rule(
        self,
        current_context: Dict[str, Any]
    ) -> Optional[ProceduralRule]:
        """Retrieve best matching procedural rule"""
        if not self.rules:
            return None
        
        # Find rules that match current context
        matching_rules = []
        for rule in self.rules:
            match_score = self._match_condition(rule.condition, current_context)
            if match_score > 0.5:  # Threshold
                weighted_score = match_score * rule.success_rate * (1.0 + rule.usage_count * 0.01)
                matching_rules.append((weighted_score, rule))
        
        if not matching_rules:
            return None
        
        # Return best matching rule
        matching_rules.sort(key=lambda x: x[0], reverse=True)
        return matching_rules[0][1]
    
    def _find_similar_rule(
        self,
        condition: Dict[str, Any],
        action: str
    ) -> Optional[ProceduralRule]:
        """Find similar existing rule"""
        for rule in self.rules:
            if rule.action == action:
                match_score = self._match_condition(rule.condition, condition)
                if match_score > 0.8:  # High similarity threshold
                    return rule
        return None
    
    def _match_condition(
        self,
        condition: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate how well condition matches context"""
        if not condition:
            return 1.0
        
        matches = 0
        total = 0
        
        for key, value in condition.items():
            total += 1
            if key in context:
                if isinstance(value, (int, float)) and isinstance(context[key], (int, float)):
                    # Numerical match with tolerance
                    tolerance = abs(value) * 0.1  # 10% tolerance
                    if abs(context[key] - value) <= tolerance:
                        matches += 1
                elif context[key] == value:
                    matches += 1
        
        return matches / total if total > 0 else 0.0

