#!/usr/bin/env python3
"""
Entry point quando barflow viene eseguito come modulo
"""

import sys
import os

# Aggiungi la directory parent al path per trovare main.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from main import main

if __name__ == "__main__":
    main()