""" Flow Control Xblock allows to provide distinct
course path according to certain conditions """

import logging
import pkg_resources

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, Integer, String
from xblockutils.studio_editable import StudioEditableXBlockMixin
from courseware.model_data import ScoresClient
from opaque_keys.edx.keys import UsageKey


LOGGER = logging.getLogger(__name__)


def load(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def _actions_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible actions to apply """

    return ['No action',
            'Redirect to tab by id, same section',
            'Redirect to URL',
            'Redirect using jump_to_id',
            'Show a message']


def _conditions_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible conditions to evaluate """
    return ['Grade on certain problem',
            'Grade on certain list of problems']


def _operators_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible operators to use """
    return ['equal',
            'distinct',
            'less than or equal to',
            'greater than or equal to',
            'less than',
            'greater than']


@XBlock.needs("i18n")
@XBlock.needs("user")
# pylint: disable=too-many-ancestors
class FlowCheckPointXblock(StudioEditableXBlockMixin, XBlock):
    """ FlowCheckPointXblock allows to take different
    learning paths based on a certain condition status """

    display_name = String(
        display_name="Display Name",
        scope=Scope.settings,
        default="Flow Control"
    )

    action = String(display_name="Action",
                    help="Select an action to apply given the condition",
                    scope=Scope.content,
                    default="No action",
                    values_provider=_actions_generator)

    condition = String(display_name="Condition",
                       help="Select a conditon to check",
                       scope=Scope.content,
                       default='Grade on certain problem',
                       values_provider=_conditions_generator)

    operator = String(display_name="Comparison type",
                      help="Select a operator to evaluate the condition",
                      scope=Scope.content,
                      default='equal',
                      values_provider=_operators_generator)

    ref_value = Integer(help="Value to use for comparison",
                        default=0,
                        scope=Scope.content,
                        display_name="Score percentage")

    tab_to = Integer(help="Number of unit tab to redirect",
                     default=1,
                     scope=Scope.content,
                     display_name="Tab to redirect")

    target_url = String(help="Url to redirect, supports relative"
                        " or absolute urls",
                        scope=Scope.content,
                        display_name="URL to redirect")

    target_id = String(help="Unit Id to redirect",
                       scope=Scope.content,
                       display_name="Id to redirect")

    message = String(help="Write a message for LMS users",
                     scope=Scope.content,
                     default='',
                     display_name="Message",
                     multiline_editor='html')

    problem_id = String(help="Problem Id to check the condition",
                        scope=Scope.content,
                        display_name="Problem Id")

    list_of_problems = String(help="List of problems Ids separated by spaces "
                              "to check the condition. Each score is "
                              "calculated independently, then an overall "
                              "score is obtained",
                              scope=Scope.content,
                              display_name="List of problems",
                              default='',
                              multiline_editor=True,
                              resettable_editor=False)

    editable_fields = ('condition',
                       'problem_id',
                       'list_of_problems',
                       'operator',
                       'ref_value',
                       'action',
                       'tab_to',
                       'target_url',
                       'target_id',
                       'message')

    def get_location_string(self, locator):
        """  Returns the location string for one problem, given its id  """
        # pylint: disable=no-member
        course_prefix = 'course'
        resource = 'problem'
        course_url = self.course_id.to_deprecated_string()
        course_url = course_url.split(course_prefix)[-1]

        location_string = '{prefix}{couse_str}+{type}@{type_id}+{prefix}@{locator}'.format(
            prefix=self.course_id.BLOCK_PREFIX,
            couse_str=course_url,
            type=self.course_id.BLOCK_TYPE_PREFIX,
            type_id=resource,
            locator=locator)

        return location_string

    def get_condition_status(self):
        """  Returns the current condition status  """
        condition_reached = False
        problems = []

        if self.condition == 'Grade on certain problem':
            problems = self.problem_id.split()
            usage_str = self.get_location_string(problems[0])
            condition_reached = self.condition_problem(usage_str)

        if self.condition == 'Grade on certain list of problems':
            problems = self.list_of_problems.split()
            condition_reached = self.condition_on_problem_list(problems)

        return condition_reached

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """  Returns a fragment for student view  """
        fragment = Fragment(u"<!-- This is the FlowCheckPointXblock -->")
        fragment.add_javascript(load("static/js/injection.js"))

        # helper variables
        # pylint: disable=no-member
        in_studio_runtime = hasattr(self.xmodule_runtime, 'is_author_mode')
        index_base = 1
        default_tab = 'tab_{}'.format(self.tab_to - index_base)

        fragment.initialize_js(
            'FlowControlGoto',
            json_args={"display_name": self.display_name,
                       "default": default_tab,
                       "default_tab_id": self.tab_to,
                       "action": self.action,
                       "target_url": self.target_url,
                       "target_id": self.target_id,
                       "message": self.message,
                       "in_studio_runtime": in_studio_runtime})

        return fragment

    @XBlock.json_handler
    def condition_status_handler(self, data, suffix=''):  # pylint: disable=unused-argument
        """  Returns the actual condition state  """

        return {
            'success': True,
            'status': self.get_condition_status()
        }

    def author_view(self, context=None):  # pylint: disable=unused-argument, no-self-use
        """  Returns author view fragment on Studio """
        # creating xblock fragment
        # TO-DO display for studio with setting resume
        fragment = Fragment(u"<!-- This is the studio -->")
        fragment.add_javascript(load("static/js/injection.js"))
        fragment.initialize_js('StudioFlowControl')

        return fragment

    def studio_view(self, context=None):
        """  Returns studio view fragment """
        fragment = super(FlowCheckPointXblock,
                         self).studio_view(context=context)

        # We could also move this function to a different file
        fragment.add_javascript(load("static/js/injection.js"))
        fragment.initialize_js('EditFlowControl')

        return fragment

    def compare_scores(self, correct, total):
        """  Returns the result of comparison using custom operator """
        result = False
        if total:
            # getting percentage score for that section
            percentage = (correct / total) * 100

            if self.operator == 'equal':
                result = percentage == self.ref_value
            if self.operator == 'distinct':
                result = percentage != self.ref_value
            if self.operator == 'less than or equal to':
                result = percentage <= self.ref_value
            if self.operator == 'greater than or equal to':
                result = percentage >= self.ref_value
            if self.operator == 'less than':
                result = percentage < self.ref_value
            if self.operator == 'greater than':
                result = percentage > self.ref_value

        return result

    def condition_problem(self, location_str):
        """  Returns the score for one problem """
        # pylint: disable=no-member
        usage_key = UsageKey.from_string(location_str)
        user_id = self.xmodule_runtime.user_id

        scores_client = ScoresClient(self.course_id, user_id)
        scores_client.fetch_scores([usage_key])
        score = scores_client.get(usage_key)

        return self.compare_scores(score.correct, score.total)

    def condition_on_problem_list(self, problems):
        """ Returns the score for a list of problems """
        # pylint: disable=no-member
        user_id = self.xmodule_runtime.user_id
        scores_client = ScoresClient(self.course_id, user_id)
        total = 0
        correct = 0

        for problem in problems:
            location_str = self.get_location_string(problem)
            usage_key = UsageKey.from_string(location_str)
            scores_client.fetch_scores([usage_key])
            score = scores_client.get(usage_key)
            if score.total:
                total += score.total
                correct += score.correct

        return self.compare_scores(correct, total)
