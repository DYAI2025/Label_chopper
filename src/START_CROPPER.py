#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Launcher für DHL Label Cropper
Installiert automatisch Dependencies und startet die App
"""

import subprocess
import sys
import os

def install_and_run():
    print("=" * 50)
    print("DHL Label Cropper - Auto-Installer & Launcher")
    print("=" * 50)
    print()
    
    # Check/Install PyMuPDF
    print("📦 Checking PyMuPDF...")
    try:
        import fitz
        print("✅ PyMuPDF already installed")
    except ImportError:
        print("📥 Installing PyMuPDF...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF==1.23.8"])
    
    # Run the app
    print()
    print("🚀 Starting DHL Label Cropper...")
    print("-" * 50)
    
    # Import and run
    try:
        from dhl_label_cropper_robust import DHLLabelCropper
        app = DHLLabelCropper()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    install_and_run()
