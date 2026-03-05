#!/usr/bin/env python3
"""
ZED Comprehensive Dashboard Launcher
===================================
Simple launcher script with checks for dependencies
"""

import sys
import os
import subprocess
import importlib

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'tkinter',
        'matplotlib', 
        'numpy',
        'cv2',
        'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'cv2':
                import cv2
            elif package == 'PIL':
                import PIL
            else:
                importlib.import_module(package)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    return missing_packages

def check_zed_sdk():
    """Check if ZED SDK is installed"""
    try:
        import pyzed.sl as sl
        return True
    except ImportError:
        print("✗ ZED SDK - MISSING")
        print("Please install the ZED SDK from: https://www.stereolabs.com/developers/release/")
        return False

def install_missing_packages(packages):
    """Install missing packages using pip"""
    if not packages:
        return True
        
    print(f"\nAttempting to install missing packages: {', '.join(packages)}")
    try:
        # Map package names to pip install names
        pip_names = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow'
        }
        
        for package in packages:
            if package == 'tkinter':
                print(f"⚠️  tkinter comes with Python. If missing, reinstall Python with tkinter support.")
                continue
                
            pip_name = pip_names.get(package, package)
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Installed {pip_name}")
            else:
                print(f"✗ Failed to install {pip_name}: {result.stderr}")
                return False
        return True
    except Exception as e:
        print(f"Error installing packages: {e}")
        return False

def main():
    """Main launcher function"""
    print("ZED Comprehensive Dashboard Launcher")
    print("=" * 40)
    
    print("\nChecking dependencies...")
    missing = check_dependencies()
    
    # Check ZED SDK separately
    zed_ok = check_zed_sdk()
    
    if missing:
        print(f"\nMissing packages detected: {', '.join(missing)}")
        user_input = input("Would you like to install them automatically? (y/n): ")
        
        if user_input.lower() in ['y', 'yes']:
            if install_missing_packages(missing):
                print("✓ All packages installed successfully!")
            else:
                print("✗ Some packages failed to install. Please install manually.")
                return
        else:
            print("Please install missing packages manually and try again.")
            return
    
    if not zed_ok:
        print("\n⚠️  ZED SDK is required but not found.")
        print("Please install from: https://www.stereolabs.com/developers/release/")
        input("Press Enter to continue anyway (some features may not work)...")
    
    print("\n🚀 Launching ZED Dashboard...")
    try:
        # Import and run the dashboard
        from zed_comprehensive_dashboard import main as run_dashboard
        run_dashboard()
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()