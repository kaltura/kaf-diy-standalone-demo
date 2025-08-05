#!/usr/bin/env python3
"""
KAF Standalone Demo - Entry Point
Run this script to start the Flask application
"""

import sys
import os

# Add the lib directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from lib.server import main

if __name__ == '__main__':
    main() 