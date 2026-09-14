"""Repo-root pytest conftest: ensures `knowledge` (and future top-level
packages such as `agents`, `llm`, `automation`) are importable during test
collection regardless of the invocation working directory. No test
behavior is defined here — this file only fixes sys.path.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
