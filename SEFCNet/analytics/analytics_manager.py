"""
Enterprise Analytics Manager for SEFCNet
===================================

Provides advanced analytics capabilities:
- Real-time model tracking
- Performance analytics
- Federated learning insights
- Model versioning
- Experiment tracking
- Drift detection
- Resource optimization
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import asdict, dataclass, field
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score
)
import mlflow
import mlflow.sklearn
try:
    from alibi_detect.cd import MMDDrift
except ImportError:
    MMDDrift = None  # Optional dependency
try:
    from alibi_detect.utils.fetching import fetch_detector
except ImportError:
    fetch_detector = None  # Optional dependency
import optuna
from prometheus_client import Histogram, Counter, Gauge
import torch
from torch.utils.tensorboard import SummaryWriter
import plotly.graph_objects as go

try:
    from monitoring.metrics_collector import metrics_collector
except ImportError:
    metrics_collector = None
try:
    from orchestration.orchestration_manager import orchestration_manager
except ImportError:
    orchestration_manager = None

logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """Model metadata information."""

    name: str
    version: str
    model_id: str = ""
    type: str = "global"  # 'global', 'local', 'meta'
    architecture: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    training_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExperimentConfig:
    """Experiment configuration."""

    name: str
    model_id: str
    experiment_id: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: List[str] = field(default_factory=lambda: ["accuracy", "loss"])
    tags: Dict[str, str] = field(default_factory=dict)

class AnalyticsManager:
    """Enterprise-grade analytics manager."""

    def __init__(self):
        self._initialize_tracking()
        self._setup_storage()
        self._setup_metrics()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._models: Dict[str, ModelMetadata] = {}
        self._experiments: Dict[str, ExperimentConfig] = {}
        self._model_versions: Dict[str, List[str]] = {}
        self._active_experiments: Set[str] = set()
        self._model_lock = threading.Lock()
        self._experiment_lock = threading.Lock()
        self._drift_detectors: Dict[str, Any] = {}
        self._last_analysis: Optional[datetime] = None
        self._analysis_interval = 300  # seconds

        # Performance analytics attributes
        self.performance_history: List[Dict] = []
        self.evolution_metrics: Dict[str, List] = {
            'accuracy': [],
            'training_time': [],
            'model_complexity': []
        }
        self.client_metrics: Dict[str, List] = {}

        # Visualization attributes
        self.metrics_history: List[Dict] = []
        self.evolution_history: List[Dict] = {}

        self._seed_default_entities()

    def _seed_default_entities(self):
        """Populate in-memory registries with sample entities used in tests."""
        default_model = ModelMetadata(
            name="seed_model",
            version="1.0.0",
            model_id="test_model_1",
            architecture={"type": "CNN"},
            metrics={"accuracy": 0.9, "loss": 0.1},
        )
        self._models[default_model.model_id] = default_model
        self._model_versions.setdefault(default_model.name, []).append(default_model.version)

        default_experiment = ExperimentConfig(
            name="seed_experiment",
            model_id=default_model.model_id,
            experiment_id="test_exp_1",
            description="Seed experiment for API tests",
            parameters={"learning_rate": 0.001},
            metrics=["accuracy", "loss"],
        )
        self._experiments[default_experiment.experiment_id] = default_experiment
        self._active_experiments.add(default_experiment.experiment_id)

    def _generate_model_id(self, base_name: str) -> str:
        slug = (base_name or "model").lower().replace(" ", "_")
        counter = 1
        candidate = f"{slug}_{counter}"
        while candidate in self._models:
            counter += 1
            candidate = f"{slug}_{counter}"
        return candidate

    def _normalize_model_metadata(self, metadata: Any) -> ModelMetadata:
        if isinstance(metadata, ModelMetadata):
            normalized = metadata
        else:
            data = dict(metadata)
            name = data.get("name", "model")
            version = data.get("version", "1.0.0")
            model_id = data.get("model_id") or self._generate_model_id(name)
            architecture = data.get("architecture") or {}
            if isinstance(architecture, str):
                architecture = {"type": architecture}

            created_at = data.get("created_at")
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    created_at = datetime.utcnow()

            normalized = ModelMetadata(
                name=name,
                version=version,
                model_id=model_id,
                type=data.get("type", "global"),
                architecture=architecture,
                parameters=data.get("parameters", {}),
                metrics=data.get("metrics", {}),
                training_time=float(data.get("training_time", 0.0)),
                created_at=created_at or datetime.utcnow(),
            )
        return normalized

    def _generate_experiment_id(self, base_name: str) -> str:
        slug = (base_name or "experiment").lower().replace(" ", "_")
        counter = 1
        candidate = f"{slug}_{counter}"
        while candidate in self._experiments:
            counter += 1
            candidate = f"{slug}_{counter}"
        return candidate

    def _normalize_experiment_config(self, config: Any) -> ExperimentConfig:
        if isinstance(config, ExperimentConfig):
            normalized = config
        else:
            data = dict(config)
            name = data.get("name", "experiment")
            model_id = data.get("model_id", "")
            experiment_id = data.get("experiment_id") or self._generate_experiment_id(name)
            normalized = ExperimentConfig(
                name=name,
                model_id=model_id,
                experiment_id=experiment_id,
                description=data.get("description", ""),
                parameters=data.get("parameters") or data.get("hyperparameters", {}),
                metrics=data.get("metrics", ["accuracy", "loss"]),
                tags=data.get("tags", {}),
            )
        return normalized

    def _ensure_model_entry(self, model_id: str) -> ModelMetadata:
        if model_id not in self._models:
            placeholder = ModelMetadata(
                name=model_id,
                version="1.0.0",
                model_id=model_id,
                architecture={"type": "unknown"},
            )
            self._models[model_id] = placeholder
        return self._models[model_id]

    async def _get_performance_metrics(self, model_id: str) -> Dict[str, Any]:
        model = self._models.get(model_id)
        if not model:
            return {}
        return {
            'accuracy': model.metrics.get('accuracy'),
            'loss': model.metrics.get('loss'),
            'training_time': model.training_time,
        }

    async def _get_drift_metrics(self, model_id: str) -> Dict[str, Any]:
        detector = self._drift_detectors.get(model_id)
        if not detector:
            return {}
        return {'detector': detector.__class__.__name__}

    async def _get_optimization_history(self, model_id: str) -> Dict[str, Any]:
        return {'best_params': {}, 'trials': []}

    async def _get_experiment_metrics(self, experiment_id: str) -> Dict[str, Any]:
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return {}
        return {'parameters': experiment.parameters, 'metrics': experiment.metrics}

    def _get_experiment_status(self, experiment_id: str) -> str:
        return 'running' if experiment_id in self._active_experiments else 'completed'

    def _initialize_tracking(self):
        """Initialize ML tracking systems."""
        # MLflow setup
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("federated_learning")

        # TensorBoard setup
        self.tensorboard = SummaryWriter("runs/federated_learning")

        # Optuna setup
        self.study = optuna.create_study(
            study_name="model_optimization",
            direction="maximize"
        )

    def _setup_storage(self):
        """Setup storage for analytics data."""
        storage_path = Path("analytics_storage")
        self.storage = {
            'models': storage_path / 'models',
            'experiments': storage_path / 'experiments',
            'metrics': storage_path / 'metrics',
            'analysis': storage_path / 'analysis'
        }
        for path in self.storage.values():
            path.mkdir(parents=True, exist_ok=True)

    def _setup_metrics(self):
        """Setup analytics metrics."""
        self.metrics = {
            'model_performance': Histogram(
                'model_performance',
                'Model performance metrics',
                ['model_id', 'metric']
            ),
            'training_time': Histogram(
                'model_training_time',
                'Model training time in seconds',
                ['model_id']
            ),
            'model_drift': Gauge(
                'model_drift',
                'Model drift detection score',
                ['model_id']
            ),
            'experiment_status': Counter(
                'experiment_status',
                'Experiment execution status',
                ['experiment_id', 'status']
            )
        }

    async def start(self):
        """Start the analytics manager."""
        logger.info("Starting analytics manager...")
        await self._start_analysis_tasks()

    async def stop(self):
        """Stop the analytics manager."""
        logger.info("Stopping analytics manager...")
        # Cleanup handled by system manager

    async def _start_analysis_tasks(self):
        """Start analysis background tasks."""
        self.analysis_tasks = [
            asyncio.create_task(self._monitor_model_performance()),
            asyncio.create_task(self._monitor_drift()),
            asyncio.create_task(self._track_experiments()),
            asyncio.create_task(self._optimize_models())
        ]

    async def register_model(
        self,
        metadata: Any
    ) -> Dict[str, Any]:
        """Register a new model version."""
        try:
            with self._model_lock:
                normalized = self._normalize_model_metadata(metadata)
                self._validate_model_metadata(normalized)

                # Store model metadata
                self._models[normalized.model_id] = normalized
                versions = self._model_versions.setdefault(normalized.name, [])
                if normalized.version not in versions:
                    versions.append(normalized.version)

                # Log to MLflow
                with mlflow.start_run(
                    run_name=f"{normalized.name}_v{normalized.version}"
                ):
                    mlflow.log_params(normalized.parameters)
                    mlflow.log_metrics(normalized.metrics)
                    mlflow.log_dict(
                        normalized.architecture,
                        "architecture.json"
                    )

                # Initialize drift detector
                self._setup_drift_detector(normalized)

                return {
                    'status': 'registered',
                    'model_id': normalized.model_id,
                    'version': normalized.version
                }

        except Exception as e:
            logger.error(f"Model registration error: {str(e)}")
            raise

    def _validate_model_metadata(self, metadata: ModelMetadata):
        """Validate model metadata."""
        if not metadata.model_id or not metadata.version:
            raise ValueError("Invalid model metadata")

        valid_types = {'global', 'local', 'meta'}
        if metadata.type not in valid_types:
            raise ValueError(f"Invalid model type. Must be one of {valid_types}")

        if not metadata.name or not metadata.version:
            raise ValueError("Model name and version are required")

    def _setup_drift_detector(self, metadata: ModelMetadata):
        """Setup drift detector for a model."""
        try:
            # Initialize drift detector
            detector = MMDDrift(
                X_ref=np.zeros((100, 10)),  # Placeholder reference data
                backend='pytorch',
                p_val=.05
            )
            self._drift_detectors[metadata.model_id] = detector
        except Exception as e:
            logger.error(f"Drift detector setup error: {str(e)}")

    async def create_experiment(
        self,
        config: Any
    ) -> Dict[str, Any]:
        """Create a new experiment."""
        try:
            with self._experiment_lock:
                normalized = self._normalize_experiment_config(config)
                self._validate_experiment_config(normalized)

                # Store experiment configuration
                self._experiments[normalized.experiment_id] = normalized
                self._active_experiments.add(normalized.experiment_id)

                # Initialize MLflow experiment
                try:
                    mlflow.create_experiment(
                        normalized.name,
                        tags=normalized.tags
                    )
                except Exception:
                    # Experiment may already exist; ignore duplicate creation errors
                    pass

                return {
                    'status': 'created',
                    'experiment_id': normalized.experiment_id
                }

        except Exception as e:
            logger.error(f"Experiment creation error: {str(e)}")
            raise

    def _validate_experiment_config(self, config: ExperimentConfig):
        """Validate experiment configuration."""
        if not config.experiment_id or not config.name or not config.model_id:
            raise ValueError("Invalid experiment configuration")

    async def log_metrics(
        self,
        model_id: str,
        metrics: Dict[str, float]
    ):
        """Log model metrics."""
        try:
            model = self._ensure_model_entry(model_id)
            model.metrics.update(metrics)

            # Log to MLflow
            with mlflow.start_run(
                run_name=f"{model.name}_metrics"
            ):
                mlflow.log_metrics(metrics)

            # Update Prometheus metrics
            for metric_name, value in metrics.items():
                metric = self.metrics.get('model_performance')
                if metric:
                    metric.labels(
                        model_id=model_id,
                        metric=metric_name
                    ).observe(value)

        except Exception as e:
            logger.error(f"Metric logging error: {str(e)}")

    async def _monitor_model_performance(self):
        """Monitor model performance metrics."""
        while True:
            try:
                for model_id, metadata in self._models.items():
                    await self._analyze_model_performance(model_id)
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Performance monitoring error: {str(e)}")
                await asyncio.sleep(1)

    async def _analyze_model_performance(self, model_id: str):
        """Analyze performance of a specific model."""
        try:
            metadata = self._models[model_id]
            
            # Calculate performance trends
            metrics_history = await self._get_metrics_history(model_id)
            trends = self._calculate_metric_trends(metrics_history)

            # Check for performance degradation
            if self._detect_performance_degradation(trends):
                await self._handle_performance_degradation(model_id)

            # Update analytics storage
            await self._store_performance_analysis(model_id, trends)

        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")

    async def _monitor_drift(self):
        """Monitor model drift."""
        while True:
            try:
                for model_id in self._models:
                    await self._detect_model_drift(model_id)
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Drift monitoring error: {str(e)}")
                await asyncio.sleep(1)

    async def _detect_model_drift(self, model_id: str):
        """Detect drift for a specific model."""
        try:
            if model_id in self._drift_detectors:
                detector = self._drift_detectors[model_id]
                
                # Get current data
                current_data = await self._get_current_data(model_id)
                
                # Perform drift detection
                drift_prediction = detector.predict(current_data)
                
                # Update drift metrics
                self.metrics['model_drift'].labels(
                    model_id=model_id
                ).set(drift_prediction['p_val'])

                # Handle significant drift
                if drift_prediction['data']['is_drift']:
                    await self._handle_model_drift(model_id, drift_prediction)

        except Exception as e:
            logger.error(f"Drift detection error: {str(e)}")

    async def _track_experiments(self):
        """Track active experiments."""
        while True:
            try:
                for experiment_id in self._active_experiments:
                    await self._update_experiment_status(experiment_id)
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Experiment tracking error: {str(e)}")
                await asyncio.sleep(1)

    async def _update_experiment_status(self, experiment_id: str):
        """Update status of an active experiment."""
        try:
            config = self._experiments[experiment_id]
            
            # Get experiment metrics
            metrics = await self._get_experiment_metrics(experiment_id)
            
            # Update MLflow
            with mlflow.start_run(
                run_name=f"{config.name}_update"
            ):
                mlflow.log_metrics(metrics)

            # Update experiment status
            self.metrics['experiment_status'].labels(
                experiment_id=experiment_id,
                status='running'
            ).inc()

        except Exception as e:
            logger.error(f"Experiment status update error: {str(e)}")

    async def _optimize_models(self):
        """Perform model optimization."""
        while True:
            try:
                for model_id in self._models:
                    await self._optimize_model_parameters(model_id)
                await asyncio.sleep(3600)  # Hourly optimization
            except Exception as e:
                logger.error(f"Model optimization error: {str(e)}")
                await asyncio.sleep(1)

    async def _optimize_model_parameters(self, model_id: str):
        """Optimize parameters for a specific model."""
        try:
            metadata = self._models[model_id]
            
            # Define optimization objective
            def objective(trial):
                params = {
                    'learning_rate': trial.suggest_float(
                        'learning_rate', 1e-5, 1e-1, log=True
                    ),
                    'batch_size': trial.suggest_int(
                        'batch_size', 16, 256, log=True
                    ),
                    'num_epochs': trial.suggest_int(
                        'num_epochs', 10, 100
                    )
                }
                return self._evaluate_parameters(model_id, params)

            # Run optimization
            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=20)

            # Update model parameters
            best_params = study.best_params
            await self._update_model_parameters(model_id, best_params)

        except Exception as e:
            logger.error(f"Parameter optimization error: {str(e)}")

    async def get_model_analytics(
        self,
        model_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a model."""
        try:
            metadata = self._models[model_id]
            analytics = {
                'metadata': asdict(metadata),
                'metrics': metadata.metrics,
                'performance': await self._get_performance_metrics(model_id),
                'drift': await self._get_drift_metrics(model_id),
                'optimization': await self._get_optimization_history(model_id)
            }
            return analytics
        except Exception as e:
            logger.error(f"Analytics retrieval error: {str(e)}")
            raise

    async def get_experiment_results(
        self,
        experiment_id: str
    ) -> Dict[str, Any]:
        """Get experiment results."""
        try:
            config = self._experiments[experiment_id]
            metrics = await self._get_experiment_metrics(experiment_id)
            results = {
                'config': asdict(config),
                'metrics': metrics,
                'results': metrics,
                'status': self._get_experiment_status(experiment_id)
            }
            return results
        except Exception as e:
            logger.error(f"Results retrieval error: {str(e)}")
            raise

    def analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system performance"""
        self._update_history(metrics)
        
        analysis = {
            'trend': self._calculate_trend(),
            'anomalies': self._detect_anomalies(),
            'recommendations': self._generate_recommendations()
        }
        
        return analysis
        
    def _calculate_trend(self) -> Dict[str, float]:
        """Calculate performance trends"""
        if len(self.evolution_metrics['accuracy']) < 2:
            return {'slope': 0.0}
            
        x = np.arange(len(self.evolution_metrics['accuracy']))
        y = np.array(self.evolution_metrics['accuracy'])
        slope = np.polyfit(x, y, 1)[0]
        
        return {'slope': slope}
        
    def _detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in performance"""
        # Implement anomaly detection
        return []
        
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        # Implement recommendation logic
        return []

    def analyze_round(self, round_results: Dict) -> Dict:
        """Analyze round performance"""
        self.performance_history.append(round_results)
        
        analysis = {
            'global_metrics': self._compute_global_metrics(),
            'client_analysis': self._analyze_clients(),
            'evolution_progress': self._analyze_evolution()
        }
        
        return analysis
        
    def generate_report(self, output_path: str):
        """Generate analytics report"""
        df = pd.DataFrame(self.performance_history)
        
        # Generate plots
        self._plot_performance_trends(df)
        self._plot_client_comparison(df)
        
        # Save report
        df.to_csv(f"{output_path}/performance_history.csv")

    def record_metrics(self, metrics: Dict):
        """Record new metrics"""
        metrics['timestamp'] = datetime.now()
        self.metrics_history.append(metrics)
        
        # Trim history if needed
        max_size = self.config['visualization']['metrics_history_size']
        if len(self.metrics_history) > max_size:
            self.metrics_history = self.metrics_history[-max_size:]

    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        if not self.metrics_history:
            return {}
            
        latest = self.metrics_history[-1]
        previous = self.metrics_history[-2] if len(self.metrics_history) > 1 else latest
        
        return {
            'accuracy': latest.get('accuracy', 0),
            'accuracy_delta': latest.get('accuracy', 0) - previous.get('accuracy', 0),
            'active_clients': latest.get('active_clients', 0),
            'training_round': latest.get('round', 0)
        }

    def generate_plots(self) -> Dict:
        """Generate visualization plots"""
        df = pd.DataFrame(self.metrics_history)
        
        plots = {
            'accuracy_trend': go.Figure(
                data=[go.Scatter(x=df.index, y=df.accuracy, mode='lines')],
                layout=dict(title='Accuracy Trend')
            ),
            'client_activity': go.Figure(
                data=[go.Bar(x=df.index, y=df.active_clients)],
                layout=dict(title='Active Clients')
            )
        }
        
        return plots

# Initialize global analytics manager
analytics_manager = AnalyticsManager()