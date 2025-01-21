"""
Score module generalized definitions.
"""

from importlib import import_module
from django.conf import settings


def get_score_module_function(*args, **kwargs):
    """Get ScoreModule model."""

    backend_function = settings.FLOW_CONTROL_SCORE_MODULE_BACKEND
    backend = import_module(backend_function)

    return backend.get_score_module(*args, **kwargs)


score_module = get_score_module_function
