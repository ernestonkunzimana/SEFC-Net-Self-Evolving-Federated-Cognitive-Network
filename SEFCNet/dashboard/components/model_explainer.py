"""Model explainability component for the dashboard."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import shap
from typing import Any
import torch
from sklearn.inspection import permutation_importance
import lime
from lime import lime_tabular

class ModelExplainer:
    def __init__(self):
        self.explainer = None
        
    def plot_feature_importance(self, model: Any, X: np.ndarray) -> go.Figure:
        """Plot feature importance using multiple methods."""
        if isinstance(model, torch.nn.Module):
            return self._plot_deep_learning_importance(model, X)
        return self._plot_traditional_importance(model, X)
        
    def _plot_deep_learning_importance(self, model: torch.nn.Module, X: torch.Tensor) -> go.Figure:
        """Create feature importance visualization for deep learning models."""
        # Use SHAP for deep learning models
        explainer = shap.DeepExplainer(model, X[:100])
        shap_values = explainer.shap_values(X[:100])
        
        # Convert SHAP values to feature importance
        feature_importance = np.abs(shap_values).mean(0)
        
        return self._create_importance_plot(
            feature_importance,
            [f"Feature {i}" for i in range(len(feature_importance))]
        )
        
    def _plot_traditional_importance(self, model: Any, X: np.ndarray) -> go.Figure:
        """Create feature importance visualization for traditional ML models."""
        # Use permutation importance
        result = permutation_importance(
            model, X, model.predict(X),
            n_repeats=10,
            random_state=42
        )
        
        return self._create_importance_plot(
            result.importances_mean,
            [f"Feature {i}" for i in range(len(result.importances_mean))]
        )
        
    def _create_importance_plot(self, importance: np.ndarray, feature_names: list) -> go.Figure:
        """Create a plotly figure for feature importance."""
        fig = go.Figure()
        
        # Sort importance values
        sorted_idx = np.argsort(importance)
        sorted_importance = importance[sorted_idx]
        sorted_names = [feature_names[i] for i in sorted_idx]
        
        fig.add_trace(go.Bar(
            x=sorted_importance,
            y=sorted_names,
            orientation='h',
            marker_color='#00CC96'
        ))
        
        fig.update_layout(
            title='Feature Importance',
            xaxis_title='Importance Score',
            yaxis_title='Feature',
            template='plotly_dark'
        )
        
        return fig
        
    def plot_decision_boundary(self, model: Any) -> go.Figure:
        """Plot decision boundary visualization."""
        # This is a placeholder - actual implementation would depend on the model type
        # and number of features. For 2D visualization:
        
        fig = go.Figure()
        
        # Add decision boundary visualization here
        # This would typically involve creating a mesh grid and
        # plotting model predictions across the feature space
        
        fig.update_layout(
            title='Decision Boundary',
            template='plotly_dark'
        )
        
        return fig
        
    def explain_prediction(self, model: Any, X: np.ndarray, instance_idx: int) -> dict:
        """Generate explanation for a specific prediction."""
        if self.explainer is None:
            self.explainer = lime_tabular.LimeTabularExplainer(
                X,
                feature_names=[f"Feature {i}" for i in range(X.shape[1])],
                class_names=['Class 0', 'Class 1', 'Class 2'],  # Adjust based on your problem
                mode='classification'
            )
            
        explanation = self.explainer.explain_instance(
            X[instance_idx],
            model.predict_proba,
            num_features=10
        )
        
        return {
            'local_importance': explanation.local_exp[1],
            'prediction': explanation.predict_proba,
            'feature_values': explanation.local_pred
        }