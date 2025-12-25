import subprocess
import sys
import os
import webbrowser
import time

def check_environment():
    """Check if virtual environment is activated"""
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        print("⚠️ Virtual environment not activated!")
        print("Please run:")
        print("   .\\venv\\Scripts\\Activate")
        sys.exit(1)

def launch_demo():
    """Launch the SEFCNet demonstration"""
    check_environment()
    
    print("🚀 Launching SEFCNet Demo...")
    
    # Ensure dependencies are installed
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start dashboard
    dashboard_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", 
         os.path.join("dashboard", "run_dashboard.py")],
        shell=True
    )
    
    # Wait for dashboard to start
    time.sleep(3)
    
    # Open browser
    webbrowser.open('http://localhost:8501')
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo...")
        dashboard_process.terminate()

if __name__ == "__main__":
    launch_demo()