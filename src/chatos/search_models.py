"""Compatibility import; implementation lives in chatos.search.search_models."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("chatos.search.search_models")
