""" Flow Control Xblock allows to provide distinct
course path according to certain conditions """

import logging
import pkg_resources

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, Integer, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

# # Not strictly xblock
from courseware.model_data import ScoresClient
from opaque_keys.edx.keys import UsageKey
# # End of Not strictly xblock


logger = logging.getLogger(__name__)


@XBlock.needs("i18n")
@XBlock.needs("user")
class FlowControlXblock(XBlock):
    """
    """

    def student_view(self, context=None):
        """
        Args:
            context: Not used for this view.

        Returns:
            (Fragment): The HTML Fragment for this XBlock
        """
        fragment = Fragment(u"<!-- This is the FlowControlXblock -->")

        return fragment


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
                'Grade on certain list of problems']

    def operators_genarator(self):
        return ['equal',
                'distinct',
                'less than or equal to',
                'greater than or equal to',
                'less than',
                'greater than']

    action = String(display_name="Action",
                    help="Select an action to apply given the condition",
                    scope=Scope.content,
                    values_provider=actions_genarator)

    condition = String(display_name="Condition",
                       help="Select a conditon to check",
                       scope=Scope.content,
                       values_provider=conditions_genarator)

    operator = String(display_name="Comparison type",
                      help="Select a operator to evaluate the condition",
                      scope=Scope.content,
                      values_provider=operators_genarator)

    ref_value = Integer(help="Value to use for comparison",
                        default=0,
                        scope=Scope.content,
                        display_name="Score percentage")

    to = Integer(help="Number of unit tab to redirect",
                 default=0,
                 scope=Scope.content,
                 display_name="Tab to redirect")

    target_url = String(help="Url to redirect, supports relative or absolute urls",
                        scope=Scope.content,
                        display_name="URL to redirect")

    target_id = String(help="Unit Id to redirect",
                       scope=Scope.content,
                       display_name="Id to redirect")

    message = String(help="Write a message for LMS users",
                     scope=Scope.content,
                     display_name="Message",
                     multiline_editor='html')

    problem_id = String(help="Problem Id to check the condition",
                        scope=Scope.content,
                        display_name="Problem Id")

    list_of_problems = String(help="List of problems Ids separated by spaces to check"
                                    " the condition. Each score is calculated independently"
                                    " then an overall score is obtained",
                              scope=Scope.content,
                              display_name="List of problems",
                              multiline_editor=True,
                              resettable_editor=False)

    editable_fields = ('condition',
                       'problem_id',
                       'list_of_problems',
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

    def get_location_string(self, locator):
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

        condition_reached = False
        problems = []

        if self.condition == 'Grade on certain problem':
            usage_str = self.get_location_string(self.problem_id)
            condition_reached = self.condition_problem(usage_str)

        if self.condition == 'Grade on certain list of problems':
            problems = self.list_of_problems.split()
            condition_reached = self.condition_subsection(problems)

        return condition_reached

    def student_view(self, context=None):

        fragment = Fragment(u"<!-- This is the FlowCheckPointXblock -->")
        fragment.add_javascript(
            self.resource_string("static/js/injection.js"))

        # helper variables
        in_studio_runtime = hasattr(self.xmodule_runtime, 'is_author_mode')
        index_base = 1
        default_tab = 'tab_{}'.format(self.to - index_base)

        fragment.initialize_js(
            'FlowControlGoto',
            json_args={"display_name": self.display_name,
                       "default": default_tab,
                       "default_tab_id": self.to,
                       "action": self.action,
                       "target_url": self.target_url,
                       "target_id": self.target_id,
                       "message": self.message,
                       "in_studio_runtime": in_studio_runtime})

        return fragment

    @XBlock.json_handler
    def condition_status_handler(self, data, suffix=''):
        """  Returns the actual condition state  """

        return {
            'success': True,
            'status': self.get_condition_status()
        }

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
        fragment.add_javascript(self.resource_string("static/js/injection.js"))
        fragment.initialize_js('EditFlowControl')

        return fragment

    def compare_scores(self, correct, total):
        if total:
            # getting percentage score for that section
            percentage = (correct / total) * 100

            if self.operator == 'equal':
                return percentage == self.ref_value
            if self.operator == 'distinct':
                return percentage != self.ref_value
            if self.operator == 'less than or equal to':
                return percentage <= self.ref_value
            if self.operator == 'greater than or equal to':
                return percentage >= self.ref_value
            if self.operator == 'less than':
                return percentage < self.ref_value
            if self.operator == 'greater than':
                return percentage > self.ref_value

        return False

    def condition_problem(self, location_str):

        usage_key = UsageKey.from_string(location_str)
        user_id = self.xmodule_runtime.user_id

        scores_client = ScoresClient(self.course_id, user_id)
        scores_client.fetch_scores([usage_key])
        score = scores_client.get(usage_key)

        return self.compare_scores(score.correct, score.total)

    def condition_subsection(self, problems):
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
