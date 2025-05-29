"""
Script to install all required dependencies in the current Python environment.
"""
import subprocess
import sys

def install_dependencies():
    """Install all dependencies from requirements.txt."""
    print("Installing dependencies from requirements.txt...")
    
    # Read requirements from file
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    
    # Install each requirement
    for req in requirements:
        if req.strip():
            print(f"Installing {req}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                print(f"Successfully installed {req}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {req}")
    
    print("Dependency installation complete.")

if __name__ == "__main__":
    install_dependencies()
