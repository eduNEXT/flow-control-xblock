"""
Unit tests for flow-control
"""

import unittest
from mock import MagicMock, patch
# from xblock.core import XBlock
from xblock.field_data import DictFieldData

from flow_control.flow import FlowCheckPointXblock
from flow_control.flow import (_actions_generator, _conditions_generator,
                               _operators_generator, load)


class TestBuilderBlocks(unittest.TestCase):
    """ Unit tests for flow-control """

    def setUp(self):
        """
        Set up a instance of FlowCheckPointXblock for testing
        """
        self.runtime_mock = MagicMock()
        scope_ids_mock = MagicMock()
        scope_ids_mock.usage_id = u'0'
        self.block = FlowCheckPointXblock(
            self.runtime_mock,
            field_data=DictFieldData({}),
            scope_ids=scope_ids_mock)

    def test_actions_generator(self):
        """
        It should return a list with allowed actions
        """
        actions_allowed = _actions_generator(self.block)
        actions = ['No action',
                   'Redirect to tab by id, same section',
                   'Redirect to URL',
                   'Redirect using jump_to_id',
                   'Show a message']
        self.assertEqual(actions, actions_allowed)

    def test_conditions_generator(self):
        """
        It should return a list with allowed actions
        """
        conditions_allowed = _conditions_generator(self.block)
        conditions = ['Grade on certain problem',
                      'Grade on certain list of problems']
        self.assertEqual(conditions, conditions_allowed)

    def test_operators_generator(self):
        """
        It should return list with allowed actions
        """
        operators_allowed = _operators_generator(self.block)
        operators = ['equal',
                     'distinct',
                     'less than or equal to',
                     'greater than or equal to',
                     'less than',
                     'greater than']
        self.assertEqual(operators, operators_allowed)

    def test_load(self):
        """
        It should return the corresponding resource
        """
        path_mock = MagicMock()
        with patch('pkg_resources.resource_string') as my_patch:
            load(path_mock)
            my_patch.assert_called_once_with('flow_control.flow', path_mock)

    def test_get_location_string(self):
        """
        It should return the problem location string given its Id
        """

        # prepare
        resource = 'problem'
        locator = 'hbdf3883be0935'
        course_prefix = 'course'
        resource = 'problem'
        self.block.course_id = MagicMock()
        self.block.course_id.BLOCK_PREFIX = 'dsgdseg'
        self.block.course_id.BLOCK_TYPE_PREFIX = 'dfsgesh'
        course_url = self.block.course_id.to_deprecated_string()
        course_url = course_url.split(course_prefix)[-1]
        # execute code
        result_string = self.block.get_location_string(locator)

        # asserts
        testing_string = '{prefix}{couse_str}+{type}@{type_id}+{prefix}@{locator}'.format(
            prefix=self.block.course_id.BLOCK_PREFIX,
            couse_str=course_url,
            type=self.block.course_id.BLOCK_TYPE_PREFIX,
            type_id=resource,
            locator=locator)

        self.assertEqual(testing_string, result_string)
        self.block.course_id.to_deprecated_string.assert_called_with()

    def test_get_condition_status(self):
        """
        It should return the actual condition status
        """

        # prepare
        self.block.condition = 'Grade on certain problem'
        self.block.get_location_string = MagicMock()
        self.block.condition_on_problem_list = MagicMock()
        self.block.problem_id = '    ndsjkjhgs78768346  '
        self.block.list_of_problems = 'ndsjkjhg8768346fd  njhgs78ikdgshuhg46  '
        problems = self.block.problem_id.split()
        # execute code
        self.block.get_condition_status()

        # asserts
        self.block.condition_on_problem_list.assert_called_with((problems))

        # prepare for a different condifiton
        self.block.condition = 'Grade on certain list of problems'

        # execute code
        self.block.get_condition_status()

        # asserts
        problems = self.block.list_of_problems.split()
        self.block.condition_on_problem_list.assert_called_with((problems))

    @patch('flow_control.flow.Fragment')
    def test_student_view(self, fragment_mock):
        """
        It should return the student view
        """

        # prepare
        fragment_instance = MagicMock()
        fragment_mock.return_value = fragment_instance
        self.block.xmodule_runtime = MagicMock()
        # execute code
        self.block.student_view(context=None)

        # asserts
        fragment_mock.assert_called()
        fragment_instance.add_javascript.assert_called()
        fragment_instance.initialize_js.assert_called()

    @patch('flow_control.flow.Fragment')
    def test_author_view(self, fragment_mock):
        """
        It should return the author view
        """

        # prepare
        fragment_instance = MagicMock()
        fragment_mock.return_value = fragment_instance

        # execute code
        self.block.author_view(context=None)

        # asserts
        fragment_mock.assert_called()
        fragment_instance.add_javascript.assert_called()
        fragment_instance.initialize_js.assert_called()
