""" Flow Control Xblock allows to provide distinct
path courses according to certain conditions """

import logging
import pkg_resources

from django.template.context import Context
from django.template.loader import get_template
from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, Integer, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

# # Not strictly xblock
import courseware
from django.db import transaction
from courseware.module_render import toc_for_course, get_module_for_descriptor
from django.contrib.auth.models import User
from util.module_utils import yield_dynamic_descriptor_descendants
from opaque_keys.edx.keys import UsageKey
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
        field_data_cache = courseware.model_data.FieldDataCache.cache_for_descriptor_descendents(
            self.course_id, self.user, course, depth=2)
        toc = toc_for_course(self.user, request, course,
                             None, None, field_data_cache)

        # the other way
        with ForceNonAtomic():
            my_grades = courseware.grades.grade(self.user, request, course)
            progress_summary = courseware.grades.progress_summary(
                self.user, request, course)

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
                    "XBlock service could not find user for anonymous_user_id '{}'".format(
                        anonymous_user_id)
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
                    "XBlock service could not find user for anonymous_user_id '{}'".format(
                        anonymous_user_id)
                )
                return None


@XBlock.needs("i18n")
@XBlock.needs("user")
class FlowCheckPointXblock(StudioEditableXBlockMixin, XBlock):

    display_name = String(
        display_name="Display Name",
        scope=Scope.settings,
        default="Flow Control"
    )

    def actions_genarator(self):
        return ['No action',
                'Redirect to tab by id, same section',
                'Redirect to URL',
                'Redirect using jump_to_id',
                'Show a message']

    def conditions_genarator(self):
        return ['Grade on certain problem',
                'Grade on certain section']

    def operators_genarator(self):
        return ['equal',
                'distinct',
                'less than or equal to',
                'greater than or equal to',
                'less than',
                'greater than']

    action = String(display_name="Action",
                    help="Select an action to apply flow control",
                    scope=Scope.content,
                    values_provider=actions_genarator)

    condition = String(display_name="Conditon",
                       help="Select a conditon to apply flow control",
                       scope=Scope.content,
                       values_provider=conditions_genarator)

    operator = String(display_name="Comparison type",
                      help="Select a operator to check the condition",
                      scope=Scope.content,
                      values_provider=operators_genarator)

    ref_value = Integer(help="Value to use for comparison",
                        default=0,
                        scope=Scope.content,
                        display_name="Score percentage")

    to = Integer(help="Number of unit to redirect",
                 default=0,
                 scope=Scope.content,
                 display_name="Tab to redirect")

    target_url = String(help="Url to redirect",
                        scope=Scope.content,
                        display_name="URL to redirect")

    target_id = String(help="Unit id to redirect",
                       scope=Scope.content,
                       display_name="Id to redirect")

    message = String(help="Write a message for LMS users",
                     scope=Scope.content,
                     display_name="Message",
                     multiline_editor='html')

    problem_id = String(help="Problem Id to apply condition",
                        scope=Scope.content,
                        display_name="Problem Id")

    section_id = String(help="Section Id that to apply condition",
                        scope=Scope.content,
                        display_name="Section Id")

    editable_fields = ('condition',
                       'problem_id',
                       'section_id',
                       'operator',
                       'ref_value',
                       'action',
                       'to',
                       'target_url',
                       'target_id',
                       'message'
                       )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_location_string(self, resource):
        course_prefix = 'course'
        course_url = self.course_id.to_deprecated_string()
        course_url = course_url.split(course_prefix)[-1]

        location_string = '{}{}+{}@{}+{}@{}'.format(
            self.course_id.BLOCK_PREFIX,
            course_url,
            self.course_id.BLOCK_TYPE_PREFIX,
            resource,
            self.course_id.BLOCK_PREFIX,
            self.problem_id)

        return location_string

    def get_condition_status(self):
        resource = None
        condition_reached = None

        if self.condition == 'Grade on certain problem':
            resource = 'problem'
            condition_reached = self.condition_problem(
                self.get_location_string(resource))

        if self.condition == 'Grade on certain section':
            resource = 'vertical'
            condition_reached = False

        return condition_reached

    def student_view(self, context=None):

        fragment = Fragment(u"<!-- This is the FlowCheckPointXblock -->")
        fragment.add_javascript(
            self.resource_string("static/js/injection.js"))

        # helper variables
        in_studio_runtime = hasattr(self.xmodule_runtime, 'is_author_mode')
        index_base = 1
        default_tab = 'tab_{}'.format(self.to - index_base)
        condition_reached = self.get_condition_status()
        if condition_reached:
            fragment.initialize_js(
                'FlowControlGoto',
                json_args={"display_name": self.display_name,
                           "default": default_tab,
                           "default_tab_id": self.to,
                           "action": self.action,
                           "target_url": self.target_url,
                           "target_id": self.target_id,
                           "message": self.message,
                           "condition_reached": condition_reached,
                           "in_studio_runtime": in_studio_runtime})
        else:
            fragment.initialize_js('StudioFlowControl')

        return fragment

    def author_view(self, context=None):

        # creating xblock fragment
        # TO-DO display for studio with setting resume
        fragment = Fragment(u"<!-- This is the studio -->")
        fragment.add_javascript(
            self.resource_string("static/js/injection.js"))
        fragment.initialize_js('StudioFlowControl')

        return fragment

    def studio_view(self, context=None):

        fragment = super(FlowCheckPointXblock,
                         self).studio_view(context=context)

        # We could also move this function to a different file
        fragment.add_javascript(load("static/js/injection.js"))
        fragment.initialize_js('EditFlowControl')

        return fragment

    def condition_problem(self, location_str):

        usage_key = UsageKey.from_string(location_str)
        user_id = self.xmodule_runtime.user_id

        scores_client = courseware.model_data.ScoresClient(
            self.course_id, user_id)
        scores_client.fetch_scores([usage_key])
        score = scores_client.get(usage_key)
        if score:
            # seleccionar el operador correcto y comparar contra el correcto
            percentage = score.correct / score.total
            # import ipdb; ipdb.set_trace()
            print percentage
            return score.total == score.correct

        return False

    @XBlock.json_handler
    def condition_status_handler(self, data, suffix=''):
        """  Returns the actual condition state  """

        return {
            'success': True,
            'status': self.get_condition_status()
        }

    def condition_subsection(self):

        # url_name = "c23b546c327a48fab9a6d352a64550af"  # xblock testing (section) -> chapter
        # url_name = "workflow"                          # edx_exams (subseccion)   -> sequential
        # url_name = "42cd641b48ea4326b91765a9d60d3272"  # all the evil (subsection)
        # block    = "vertical_ac391cde8a91"             # limited checks
        # (vertical)

        # location_str = "block-v1:edX+DemoX+Demo_Course+type@chapter+block@c23b546c327a48fab9a6d352a64550af"
        # location_str = "block-v1:edX+DemoX+Demo_Course+type@sequential+block@workflow"
        location_str = "block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_ac391cde8a91"
        usage_key = UsageKey.from_string(location_str)
        summary = self.get_progress_summary()

        (earned, possible) = summary.score_for_module(usage_key)
        return earned == possible

    #################################
    #          EXPERIMENTAL         #
    #################################

    def get_progress_summary(self):
        user = self.get_user()
        course = courseware.courses.get_course(self.course_id)

        with ForceNonAtomic():
            progress_summary = courseware.grades._progress_summary(
                user,
                self.make_request_for_grades(user),
                course,
                None,
                None,
            )
        return progress_summary

    def get_user(self):
        """
        Return the user of the user associated with anonymous_user_id

        Returns: the user if it can be identified. If the xblock service to converts to a real user
            fails, returns None and logs the error.
        """
        anonymous_user_id = self.xmodule_runtime.anonymous_student_id
        user = self.xmodule_runtime.get_real_user(anonymous_user_id)
        if user:
            return user
        else:
            logger.exception(
                "XBlock service could not find user for anonymous_user_id '{}'".format(
                    anonymous_user_id)
            )
            return None

    def make_request_for_grades(self, user):
        """
        This is a helper method to create a request object which can be used to
        call courseware.grade functions
        """
        hostname = self.xmodule_runtime.hostname
        user_obj = user

        class _req:
            META = {}
            user = user_obj

            def is_secure(self):
                return False

            def get_host(self):
                return hostname

        return _req()
