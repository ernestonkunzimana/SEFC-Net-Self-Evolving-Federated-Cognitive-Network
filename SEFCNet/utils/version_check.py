import pkg_resources
import logging
from typing import Dict, Optional

def check_dependencies() -> Dict[str, Optional[str]]:
    """
    Check installed package versions and return status
    """
    required_packages = [
        'flwr',
        'tensorflow',
        'numpy',
        'pandas',
        'scikit-learn',
        'streamlit',
        'plotly'
    ]
    
    versions = {}
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            versions[package] = version
        except pkg_resources.DistributionNotFound:
            versions[package] = None
            logging.warning(f"Package {package} not found")
    
    return versions

def print_environment_info():
    """
    Print current environment information
    """
    versions = check_dependencies()
    print("\n📦 Installed Packages:")
    print("-" * 40)
    for package, version in versions.items():
        status = "✅" if version else "❌"
        print(f"{status} {package}: {version or 'Not installed'}")
    print("-" * 40)

if __name__ == "__main__":
    print_environment_info()