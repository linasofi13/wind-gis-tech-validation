"""
Setup script for Vento Wind GIS Technology Validation.

This script helps install the project in development mode and
handles dependency management for different Python versions.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"Python {version.major}.{version.minor} is not compatible. Requires Python 3.8+")
        return False

def install_requirements():
    """Install requirements based on Python version."""
    version = sys.version_info
    
    if version.major == 3 and version.minor == 8:
        requirements_file = "requirements-py38.txt"
        print("Using Python 3.8 compatible requirements")
    else:
        requirements_file = "requirements.txt"
        print("Using standard requirements")
    
    if not Path(requirements_file).exists():
        print(f"Requirements file {requirements_file} not found")
        return False
    
    try:
        print(f"Installing requirements from {requirements_file}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return False

def install_development():
    """Install the project in development mode."""
    try:
        print("Installing project in development mode...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", "."
        ])
        print("Project installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install project: {e}")
        return False

def run_tests():
    """Run basic tests to verify installation."""
    try:
        print("Running basic tests...")
        subprocess.check_call([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ])
        print("Tests passed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Tests failed: {e}")
        return False

def main():
    """Main setup function."""
    print("Vento Wind GIS Technology Validation Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("Some requirements failed to install. Continuing...")
    
    # Install project
    if not install_development():
        print("Project installation failed. You may need to install manually.")
    
    # Run tests
    print("\nRunning verification tests...")
    if run_tests():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Prepare your data in the data/ directory")
        print("2. Configure analysis in configs/wsi.yaml")
        print("3. Run: python -m src.interface.cli info")
        print("4. Run: python -m src.interface.cli compute-wsi configs/wsi.yaml")
    else:
        print("\nSetup completed with warnings. Check the output above.")
    
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()


