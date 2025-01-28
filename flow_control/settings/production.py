"""
Settings for the Flow Control plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary project settings for production envs.
    """
    settings.FLOW_CONTROL_SCORE_MODULE_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "FLOW_CONTROL_SCORE_MODULE_BACKEND",
        settings.FLOW_CONTROL_SCORE_MODULE_BACKEND
    )
