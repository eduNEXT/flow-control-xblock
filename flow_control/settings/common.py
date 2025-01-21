"""
Settings for the Flow Control plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary common project settings.
    """
    settings.FLOW_CONTROL_SCORE_MODULE_BACKEND = 'flow_control.edxapp_wrapper.backends.score_s_v1'
