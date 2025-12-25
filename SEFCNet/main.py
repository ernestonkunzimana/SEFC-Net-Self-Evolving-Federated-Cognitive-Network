"""
SEFCNet - Main entrypoint (minimal, robust)
"""

import sys
import os
import logging
import argparse
import threading
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure project root on sys.path for tests / imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def run_dashboard_stub():
    try:
        # import here to avoid importing heavy deps at module import time
        from dashboard.app import run_dashboard
        run_dashboard()
    except Exception as e:
        logger.warning("Dashboard failed to start: %s", e)

def main():
    parser = argparse.ArgumentParser(description="SEFCNet")
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--test", action="store_true", help="Run tests instead of starting")
    args = parser.parse_args()

    if args.test:
        # delegate to pytest
        import pytest
        sys.exit(pytest.main([]))

    # Lazy import core system manager so tests/flat utils don't require heavy deps
    try:
        from core.system_manager import SystemManager
    except Exception as e:
        logger.warning("SystemManager import failed: %s", e)
        SystemManager = None

    if args.dashboard:
        t = threading.Thread(target=run_dashboard_stub, daemon=True)
        t.start()

    if SystemManager:
        try:
            sm = SystemManager(str(PROJECT_ROOT / "config" / "evolution_config.yaml"))
            sm.initialize()
            sm.start_federation()
        except Exception as e:
            logger.error("Runtime error: %s", e)

if __name__ == "__main__":
    main()