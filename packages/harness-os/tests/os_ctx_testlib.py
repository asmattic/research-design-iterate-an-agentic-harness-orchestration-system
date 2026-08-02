"""Shared test helpers for the context/bs/drift lane (Phase 2C).

The package ``__init__.py`` re-exports sibling-lane modules that may not have
landed yet, so ``import harness_os`` can fail during this lane's window.
``load_harness_os_module`` tries the normal package import first and falls
back to loading the submodule directly from its source file; the final
integrated state exercises the normal-import path.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PACKAGE_ROOT / "src" / "harness_os"
PROMPTS_DIR = PACKAGE_ROOT / "prompts"

_ALIAS_PREFIX = "_os_ctx_lane"


def load_harness_os_module(name: str) -> ModuleType:
    """Import ``harness_os.<name>``, spec-loading directly if the package
    ``__init__`` cannot import (missing sibling-lane modules)."""
    try:
        return importlib.import_module(f"harness_os.{name}")
    except ImportError:
        alias = f"{_ALIAS_PREFIX}.{name}"
        cached = sys.modules.get(alias)
        if cached is not None:
            return cached
        path = SRC_DIR / f"{name}.py"
        spec = importlib.util.spec_from_file_location(alias, path)
        if spec is None or spec.loader is None:  # pragma: no cover
            raise
        module = importlib.util.module_from_spec(spec)
        sys.modules[alias] = module
        spec.loader.exec_module(module)
        return module
