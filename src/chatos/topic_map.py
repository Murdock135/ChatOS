"""Compatibility import; implementation lives in chatos.experiments.points."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("chatos.experiments.points")
