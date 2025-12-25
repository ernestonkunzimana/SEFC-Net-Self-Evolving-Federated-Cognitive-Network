import sys
import importlib
import pkg_resources

def check_setup():
    """Verify SEFCNet environment setup"""
    required_packages = [
        'flwr',
        'tensorflow',
        'numpy',
        'pandas',
        'scikit-learn',
        'streamlit',
        'plotly'
    ]
    
    print("\n🔍 Checking SEFCNet Environment Setup")
    print("-" * 50)
    
    # Check Python version
    py_version = sys.version.split()[0]
    print(f"Python Version: {py_version}")
    
    # Check packages
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"✅ {package:<20} version {version}")
        except pkg_resources.DistributionNotFound:
            print(f"❌ {package:<20} NOT FOUND")

if __name__ == "__main__":
    check_setup()