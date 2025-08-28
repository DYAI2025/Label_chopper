#!/usr/bin/env python3
"""
DHL Label Cropper - Main Entry Point
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from START_CROPPER import install_and_run

if __name__ == "__main__":
    install_and_run()
