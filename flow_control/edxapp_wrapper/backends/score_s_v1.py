"""
Score module definitions for Open edX Sumac release.
"""
# pylint: disable=import-error
from lms.djangoapps.courseware.model_data import ScoresClient


def get_score_module(*args, **kwargs):
    """
    Get ScoresClient model.

    Returns:
        ScoresClient: ScoresClient object.
    """
    return ScoresClient(*args, **kwargs)
