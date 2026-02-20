import os
import sys
import subprocess

def run_app():
    """
    Entry point to run the Streamlit app.
    """
    app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")
    print(f"Starting CRAFT Layout Optimizer...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    run_app()
