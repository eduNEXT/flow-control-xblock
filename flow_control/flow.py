""" Flow Control Xblock allows to evaluate a condition and based on the outcome
 either display the unit's content or take an alternative action """

import logging
import pkg_resources
import re

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, Integer, String
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblock.validation import ValidationMessage
from courseware.model_data import ScoresClient
from opaque_keys.edx.keys import UsageKey
from opaque_keys import InvalidKeyError

LOGGER = logging.getLogger(__name__)


def load(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def _actions_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible actions to
    take when the condition is met """

    return [
        {"display_name": "Display a message",
         "value": "display_message"},
        {"display_name": "Redirect using jump_to_id",
         "value": "to_jump"},
        {"display_name": "Redirect to a given unit in the same subsection",
         "value": "to_unit"},
        {"display_name": "Redirect to a given URL",
         "value": "to_url"}
    ]


def _conditions_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible conditions to evaluate """
    return [
        {"display_name": "Grade of a problem",
         "value": "single_problem"},
        {"display_name": "Average grade of a list of problems",
         "value": "average_problems"}
    ]


def _operators_generator(block):  # pylint: disable=unused-argument
    """ Generates a list of possible operators to use """

    return [
        {"display_name": "equal to",
         "value": "eq"},
        {"display_name": "not equal to",
         "value": "noeq"},
        {"display_name": "less than or equal to",
         "value": "lte"},
        {"display_name": "less than",
         "value": "lt"},
        {"display_name": "greater than or equal to",
         "value": "gte"},
        {"display_name": "greater than",
         "value": "gt"},
        {"display_name": "none of the problems have been answered",
         "value": "all_null"},
        {"display_name": "all problems have been answered",
         "value": "all_not_null"},
        {"display_name": "some problem has not been answered",
         "value": "has_null"}
    ]


def n_all(iterable):
    """
    This iterator has the same logic of the function all() for an array.
    But it only responds to the existence of None and not False
    """
    for element in iterable:
        if element is None:
            return False
    return True


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
                    help="Select the action to be performed "
                    "when the condition is met",
                    scope=Scope.content,
                    default="display_message",
                    values_provider=_actions_generator)

    condition = String(display_name="Flow control condition",
                       help="Select a conditon to evaluate",
                       scope=Scope.content,
                       default='single_problem',
                       values_provider=_conditions_generator)

    operator = String(display_name="Comparison type",
                      help="Select an operator for the condition",
                      scope=Scope.content,
                      default='eq',
                      values_provider=_operators_generator)

    ref_value = Integer(help="Enter the value to be used in "
                        "the comparison. (From 0 to 100)",
                        default=0,
                        scope=Scope.content,
                        display_name="Score percentage")

    tab_to = Integer(help="Number of unit tab to redirect to. (1, 2, 3...)",
                     default=1,
                     scope=Scope.content,
                     display_name="Tab to redirect to")

    target_url = String(help="URL to redirect to, supports relative "
                        "or absolute urls",
                        scope=Scope.content,
                        display_name="URL to redirect to")

    target_id = String(help="Unit identifier to redirect to (Location id)",
                       scope=Scope.content,
                       display_name="Unit identifier to redirect to")

    message = String(help="Message for the learners to view "
                     "when the condition is met",
                     scope=Scope.content,
                     default='',
                     display_name="Message",
                     multiline_editor='html')

    problem_id = String(help="Problem id to use for the condition.  (Not the "
                        "complete problem locator. Only the 32 characters "
                        "alfanumeric id. "
                        "Example: 618c5933b8b544e4a4cc103d3e508378)",
                        scope=Scope.content,
                        display_name="Problem id")

    list_of_problems = String(help="List of problems ids separated by commas "
                              "or line breaks. (Not the complete problem "
                              "locators. Only the 32 characters alfanumeric "
                              "ids. Example: 618c5933b8b544e4a4cc103d3e508378"
                              ", 905333bd98384911bcec2a94bc30155f). "
                              "The simple average score for all problems will "
                              "be used.",
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
                       'tab_to',
                       'target_url',
                       'target_id',
                       'message')

    def validate_field_data(self, validation, data):
        """
        Validate this block's field data
        """

        if data.tab_to <= 0:
            validation.add(ValidationMessage(
                ValidationMessage.ERROR,
                u"Tab to redirect to must be greater than zero"))

        if data.ref_value < 0 or data.ref_value > 100:
            validation.add(ValidationMessage(
                ValidationMessage.ERROR,
                u"Score percentage field must "
                u"be an integer number between 0 and 100"))

    def get_location_string(self, locator, is_draft=False):
        """  Returns the location string for one problem, given its id  """
        # pylint: disable=no-member
        course_prefix = 'course'
        resource = 'problem'
        course_url = self.course_id.to_deprecated_string()

        if is_draft:
            course_url = course_url.split(self.course_id.run)[0]
            prefix = 'i4x://'
            location_string = '{prefix}{couse_str}{type_id}/{locator}'.format(
                prefix=prefix,
                couse_str=course_url,
                type_id=resource,
                locator=locator)
        else:
            course_url = course_url.replace(course_prefix, '', 1)

            location_string = '{prefix}{course_str}+{type}@{type_id}+{prefix}@{locator}'.format(
                prefix=self.course_id.BLOCK_PREFIX,
                course_str=course_url,
                type=self.course_id.BLOCK_TYPE_PREFIX,
                type_id=resource,
                locator=locator)

        return location_string

    def get_condition_status(self):
        """  Returns the current condition status  """
        condition_reached = False
        problems = []

        if self.problem_id and self.condition == 'single_problem':
            # now split problem id by spaces or commas
            problems = re.split('\s*,*|\s*,\s*', self.problem_id)
            problems = filter(None, problems)
            problems = problems[:1]

        if self.list_of_problems and self.condition == 'average_problems':
            # now split list of problems id by spaces or commas
            problems = re.split('\s*,*|\s*,\s*', self.list_of_problems)
            problems = filter(None, problems)

        if problems:
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

            if self.operator == 'eq':
                result = percentage == self.ref_value
            if self.operator == 'noeq':
                result = percentage != self.ref_value
            if self.operator == 'lte':
                result = percentage <= self.ref_value
            if self.operator == 'gte':
                result = percentage >= self.ref_value
            if self.operator == 'lt':
                result = percentage < self.ref_value
            if self.operator == 'gt':
                result = percentage > self.ref_value

        return result

    def are_all_not_null(self, problems_to_answer):
        """  Returns true when all problems have been answered """
        result = False
        all_problems_were_answered = n_all(problems_to_answer)
        if problems_to_answer and all_problems_were_answered:
            result = True
        return result

    def has_null(self, problems_to_answer):
        """  Returns true when at least one problem have not been answered """
        result = False
        all_problems_were_answered = n_all(problems_to_answer)
        if not problems_to_answer or not all_problems_were_answered:
            result = True
        return result

    def are_all_null(self, problems_to_answer):
        """  Returns true when all problems have not been answered """
        for element in problems_to_answer:
            if element is not None:
                return False
        return True

    SPECIAL_COMPARISON_DISPATCHER = {
        'all_not_null': are_all_not_null,
        'all_null': are_all_null,
        'has_null': has_null
    }

    def condition_on_problem_list(self, problems):
        """ Returns the score for a list of problems """
        # pylint: disable=no-member
        user_id = self.xmodule_runtime.user_id
        scores_client = ScoresClient(self.course_id, user_id)
        correct_neutral = {'correct': 0.0}
        total_neutral = {'total': 0.0}
        total = 0
        correct = 0

        def _get_usage_key(problem):

            loc = self.get_location_string(problem)
            try:
                uk = UsageKey.from_string(loc)
            except InvalidKeyError:
                uk = _get_draft_usage_key(problem)
            return uk

        def _get_draft_usage_key(problem):

            loc = self.get_location_string(problem, True)
            try:
                uk = UsageKey.from_string(loc)
                uk = uk.map_into_course(self.course_id)
            except InvalidKeyError:
                uk = None

            return uk

        def _to_reducible(score):
            correct_default = 0.0
            total_default = 1.0
            if not score.total:
                return {'correct': correct_default, 'total': total_default}
            else:
                return {'correct': score.correct, 'total': score.total}

        def _calculate_correct(first_score, second_score):
            correct = first_score['correct'] + second_score['correct']
            return {'correct': correct}

        def _calculate_total(first_score, second_score):
            total = first_score['total'] + second_score['total']
            return {'total': total}

        usages_keys = map(_get_usage_key, problems)
        scores_client.fetch_scores(usages_keys)
        scores = map(scores_client.get, usages_keys)
        scores = filter(None, scores)

        problems_to_answer = [score.total for score in scores]
        if self.operator in self.SPECIAL_COMPARISON_DISPATCHER.keys():
            evaluation = self.SPECIAL_COMPARISON_DISPATCHER[self.operator](
                self,
                problems_to_answer)

            return evaluation

        reducible_scores = map(_to_reducible, scores)
        correct = reduce(_calculate_correct, reducible_scores,
                         correct_neutral)
        total = reduce(_calculate_total, reducible_scores,
                       total_neutral)

        return self.compare_scores(correct['correct'], total['total'])
