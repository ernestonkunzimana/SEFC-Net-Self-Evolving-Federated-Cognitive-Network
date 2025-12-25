import sys
import pkg_resources
import logging

def check_compatibility():
    """Check system compatibility"""
    python_version = sys.version_info
    
    if python_version.major != 3 or python_version.minor < 8:
        raise RuntimeError(
            f"Python 3.8+ is required, but you have {python_version.major}.{python_version.minor}"
        )
    
    required_packages = {
        'flwr': '1.6.0',
        'tensorflow-federated': '0.33.0',
        'tensorflow': '2.12.0'
    }
    
    for package, version in required_packages.items():
        try:
            pkg_resources.require(f"{package}=={version}")
        except pkg_resources.VersionConflict as e:
            logging.warning(f"Package version conflict: {e}")
            logging.info(f"Try: pip install {package}=={version}")
        except pkg_resources.DistributionNotFound:
            logging.error(f"Required package not found: {package}")
            logging.info(f"Try: pip install {package}=={version}")

# Run compatibility check on import
check_compatibility()