"""Compatibility import; implementation lives in chatos.search.semantic."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("chatos.search.semantic")
