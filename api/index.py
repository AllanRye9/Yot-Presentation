"""
Vercel serverless entrypoint for Yot-Presentation.

This module re-exports the Flask ``app`` object from ``web/app.py`` so that
Vercel's Python runtime can use it as a WSGI handler.
"""

import sys
from pathlib import Path

# Ensure the repository root is on sys.path so ``web.app`` can be imported.
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from web.app import app  # noqa: E402 -- WSGI handler for Vercel
