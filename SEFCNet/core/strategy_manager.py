from typing import Any, Dict, List, Optional


class StrategyManager:
    """Minimal strategy manager used for orchestration/testing."""

    def __init__(self) -> None:
        self.executed_strategies: List[Dict[str, Any]] = []

    def execute_strategy(self, name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not name:
            raise ValueError("Strategy name is required")

        record = {
            "name": name,
            "context": context or {},
            "status": "executed",
        }
        self.executed_strategies.append(record)
        return record

