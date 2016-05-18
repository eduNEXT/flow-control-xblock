"""
"""
import json
import logging
import pkg_resources

from django.template.context import Context
from django.template.loader import get_template
from xblock.core import XBlock
from xblock.fragment import Fragment

# # Not strictly xblock
import courseware
from django.db import transaction
from courseware.module_render import toc_for_course, get_module_for_descriptor
from django.contrib.auth.models import User
# # End of Not strictly xblock


logger = logging.getLogger(__name__)


class ForceNonAtomic:
    def __enter__(self):
        self.before = transaction.get_connection().in_atomic_block
        transaction.get_connection().in_atomic_block = False
        return

    def __exit__(self, type, value, traceback):
        transaction.get_connection().in_atomic_block = self.before


def load(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


@XBlock.needs("i18n")
@XBlock.needs("user")
class FlowControlXblock(XBlock):
    """
    """

    def make_request_for_grades(self):
        """
        This is a helper method to create a fake request
        """
        hostname = self.xmodule_runtime.hostname

        class req:
            META = {}
            user = self.user

            def is_secure(self):
                return False

            def get_host(self):
                return hostname

        request = req()
        return request

    def student_view(self, context=None):
        """The main view of FlowControlXblock, displayed when viewing courses.

        Args:
            context: Not used for this view.

        Returns:
            (Fragment): The HTML Fragment for this XBlock
        """
        self.user = self.get_user()

        # # TODO: remove this note
        # # Not strictly xblock
        request = self.make_request_for_grades()
        course = courseware.courses.get_course(self.course_id)

        # One way
        field_data_cache = courseware.model_data.FieldDataCache.cache_for_descriptor_descendents(self.course_id, self.user, course, depth=2)
        toc = toc_for_course(self.user, request, course, None, None, field_data_cache)

        # the other way
        with ForceNonAtomic():
            my_grades = courseware.grades.grade(self.user, request, course)
            progress_summary = courseware.grades.progress_summary(self.user, request, course)

        # # End of Not strictly xblock

        # All data we intend to pass to the front end.
        from pprint import pformat as pf

        section_breakdown = my_grades.get('section_breakdown')
        grade_breakdown = my_grades.get('grade_breakdown')
        totaled_scores = my_grades.get('totaled_scores')

        context_dict = {
            # "toc": pf(toc),
            "my_grades": pf(my_grades),
            "section_breakdown": pf(section_breakdown),
            "grade_breakdown": pf(grade_breakdown),
            "totaled_scores": pf(totaled_scores),
            "progress_summary": pf(progress_summary),
            "show_staff_area": self.is_course_staff and not self.in_studio_preview,
        }
        template = get_template("base.html")

        context = Context(context_dict)
        fragment = Fragment(template.render(context))
        fragment.add_javascript(load("static/js/check-point.js"))
        fragment.initialize_js('SomeFunctionFromXblock')

        return fragment

    def author_view(self, context=None):
        """
        """
        template = get_template("author.html")
        fragment = Fragment(template.render(context))
        return fragment

    @XBlock.json_handler
    def control_point(self, data, suffix=''):
        """        """

        return {
            'success': True,
            'data': data,
            'suffix': suffix,
        }

    @property
    def is_course_staff(self):
        """
        Check whether the user has course staff permissions for this XBlock.

        Returns:
            bool
        """
        if hasattr(self, 'xmodule_runtime'):
            return getattr(self.xmodule_runtime, 'user_is_staff', False)
        else:
            return False

    @property
    def is_beta_tester(self):
        """
        Check whether the user is a beta tester.

        Returns:
            bool
        """
        if hasattr(self, 'xmodule_runtime'):
            return getattr(self.xmodule_runtime, 'user_is_beta_tester', False)
        else:
            return False

    @property
    def in_studio_preview(self):
        """
        Check whether we are in Studio preview mode.

        Returns:
            bool

        """
        # When we're running in Studio Preview mode, the XBlock won't provide us with a user ID.
        # (Note that `self.xmodule_runtime` will still provide an anonymous
        # student ID, so we can't rely on that)
        return self.scope_ids.user_id is None

    def workbench_scenarios():
        """A canned scenario for display in the workbench.

        These scenarios are only intended to be used for Workbench XBlock
        Development.

        """
        return [
        ]

    @property
    def _(self):
        i18nService = self.runtime.service(self, 'i18n')
        return i18nService.ugettext

    def get_username(self, anonymous_user_id):
        """
        Return the username of the user associated with anonymous_user_id
        Args:
            anonymous_user_id (str): the anonymous user id of the user

        Returns: the username if it can be identified. If the xblock service to converts to a real user
            fails, returns None and logs the error.

        """
        if hasattr(self, "xmodule_runtime"):
            user = self.xmodule_runtime.get_real_user(anonymous_user_id)
            if user:
                return user.username
            else:
                logger.exception(
                    "XBlock service could not find user for anonymous_user_id '{}'".format(anonymous_user_id)
                )
                return None

    def get_user(self):
        """
        Return the username of the user associated with anonymous_user_id
        Args:
            anonymous_user_id (str): the anonymous user id of the user

        Returns: the user if it can be identified. If the xblock service to converts to a real user
            fails, returns None and logs the error.

        """

        anonymous_user_id = self.xmodule_runtime.anonymous_student_id

        if hasattr(self, "xmodule_runtime"):
            user = self.xmodule_runtime.get_real_user(anonymous_user_id)
            if user:
                return user
            else:
                logger.exception(
                    "XBlock service could not find user for anonymous_user_id '{}'".format(anonymous_user_id)
                )
                return None


class FlowCheckPointXblock(XBlock):

    def student_view(self, context=None):

        fragment = Fragment(u"<!-- This is the FlowCheckPointXblock -->")
        fragment.add_javascript(load("static/js/injection.js"))
        fragment.initialize_js('FlowControlGoto', json_args={"target": "tab_0"})

        return fragment

    @XBlock.json_handler
    def control_point(self, data, suffix=''):
        """        """

        return {
            'success': True,
            'data': data,
            'suffix': suffix,
        }
