#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick setup script for installing dependencies
Run: python setup_dependencies.py
"""

import subprocess
import sys
import os

def install_deps():
    """Install required packages"""
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found")
        return False
    
    print("Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL)
        
        # Install from requirements
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Successfully installed all packages")
            print("Main packages: pandas, matplotlib, seaborn, selenium, numpy, beautifulsoup4, requests, python-dateutil, pytz")
            return True
        else:
            print("Installation failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"Error: Need Python 3.7+, got {version.major}.{version.minor}")
        return False
    
    print(f"Python {version.major}.{version.minor} OK")
    return True

def main():
    print("Trump Policy Analysis - Setup")
    print("-" * 30)
    
    if not check_python():
        return
    
    success = install_deps()
    
    if success:
        print("\nSetup complete! You can now run the scripts.")
    else:
        print("\nSetup failed. Try manual install:")
        print("pip install pandas matplotlib seaborn selenium numpy beautifulsoup4 requests python-dateutil pytz webdriver-manager")

if __name__ == "__main__":
    main()
