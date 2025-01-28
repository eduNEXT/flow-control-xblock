"""
Flow Control Django application initialization.
"""

from django.apps import AppConfig


class FlowControlConfig(AppConfig):
    """
    Configuration for the Flow Control Django application.
    """
    name = "flow_control"

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        }
    }
