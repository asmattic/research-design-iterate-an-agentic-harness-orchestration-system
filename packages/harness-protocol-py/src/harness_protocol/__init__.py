"""Harness-agnostic orchestration protocol: schemas, validators, conformance runner."""

from harness_protocol.assets import assets_root
from harness_protocol.validate import SCHEMA_NAMES, is_valid, iter_errors, load_schema

__version__ = "0.2.0"
PROTOCOL_VERSION = "0.2.0"

__all__ = [
    "__version__",
    "PROTOCOL_VERSION",
    "SCHEMA_NAMES",
    "load_schema",
    "iter_errors",
    "is_valid",
    "assets_root",
]
