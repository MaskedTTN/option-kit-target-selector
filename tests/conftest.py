import os
import sys

# Ensure the package `src/` is on sys.path so tests can import modules like `main`.
HERE = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(HERE, '..', 'src'))

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
