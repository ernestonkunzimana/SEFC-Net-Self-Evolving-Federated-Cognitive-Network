"""
Enterprise-grade dashboard configuration
"""
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field

class DashboardConfig(BaseSettings):
    """Dashboard configuration settings"""
    
    # Server Configuration
    HOST: str = Field("0.0.0.0", env="DASHBOARD_HOST")
    PORT: int = Field(8050, env="DASHBOARD_PORT")
    DEBUG: bool = Field(False, env="DASHBOARD_DEBUG")
    
    # Authentication
    AUTH_REQUIRED: bool = Field(True, env="DASHBOARD_AUTH_REQUIRED")
    JWT_SECRET: str = Field(..., env="DASHBOARD_JWT_SECRET")
    TOKEN_EXPIRE_MINUTES: int = Field(60, env="DASHBOARD_TOKEN_EXPIRE")
    
    # Data Sources
    PROMETHEUS_URL: str = Field("http://localhost:9090", env="PROMETHEUS_URL")
    GRAFANA_URL: str = Field("http://localhost:3000", env="GRAFANA_URL")
    MLFLOW_TRACKING_URI: str = Field("http://localhost:5000", env="MLFLOW_URI")
    
    # Real-time Settings
    UPDATE_INTERVAL: int = Field(5000, env="DASHBOARD_UPDATE_INTERVAL")  # ms
    WEBSOCKET_PATH: str = Field("/ws", env="DASHBOARD_WS_PATH")
    MAX_CONNECTIONS: int = Field(100, env="DASHBOARD_MAX_CONNECTIONS")
    
    # Caching
    CACHE_TYPE: str = Field("redis", env="DASHBOARD_CACHE_TYPE")
    CACHE_URL: str = Field("redis://localhost:6379", env="DASHBOARD_CACHE_URL")
    CACHE_TTL: int = Field(300, env="DASHBOARD_CACHE_TTL")  # seconds
    
    # Feature Flags
    ENABLE_XAI: bool = Field(True, env="DASHBOARD_ENABLE_XAI")
    ENABLE_PREDICTIONS: bool = Field(True, env="DASHBOARD_ENABLE_PREDICTIONS")
    ENABLE_ALERTS: bool = Field(True, env="DASHBOARD_ENABLE_ALERTS")
    
    # Layout Configuration
    DEFAULT_THEME: str = Field("dark", env="DASHBOARD_THEME")
    CUSTOM_CSS: Optional[str] = Field(None, env="DASHBOARD_CUSTOM_CSS")
    
    # Performance
    MAX_POINTS_PER_CHART: int = Field(1000, env="DASHBOARD_MAX_POINTS")
    BATCH_SIZE: int = Field(100, env="DASHBOARD_BATCH_SIZE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True