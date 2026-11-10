"""Compatibility import; implementation lives in chatos.mapping.dense_map."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("chatos.mapping.dense_map")
