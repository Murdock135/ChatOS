"""Compatibility import; implementation lives in chatos.mapping.map_topics."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("chatos.mapping.map_topics")
