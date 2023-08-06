import unittest
import sys
import yaml
import os
from functools import partial

from mock import Mock
from behave.model import Scenario

from behave_testrail_reporter.api import APIClient
from behave_testrail_reporter import TestrailReporter


class TestrailReporterTestCase(unittest.TestCase):
    def setUp(self):
        data = {
            'base_url': 'https://test.testrail.net',
            'projects': [
                {
                    'name': 'Testrail project name',
                    'id': 1,
                    'suite_id': 11,
                    'allowed_branch_pattern': '*',
                },
                {
                    'name': 'Testrail project name',
                    'id': 2,
                    'suite_id': 22,
                    'allowed_branch_pattern': '*',
                }
            ]
        }

        with open('testrail.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def tearDown(self):
        os.remove('testrail.yml')

    def test_load_config(self):
        testrail_reporter = TestrailReporter('master')
        empty_config = {}

        self.assertNotEqual(empty_config, testrail_reporter.config)

    def test_build_comment_for_scenario(self):
        testrail_reporter = TestrailReporter('master')

        step_01 = Mock(status='passed', keyword='given')
        step_01.name = 'step_01'
        step_02 = Mock(status='passed', keyword='given')
        step_02.name = 'step_02'

        steps = [step_01, step_02, ]

        mock_scenario = Mock(Scenario)
        mock_scenario.name = 'Dummy scenario'
        mock_scenario.steps = steps
        comment = testrail_reporter._buid_comment_for_scenario(mock_scenario)
        expected_comment = (
            'Dummy scenario\n'
            '->  given step_01 [passed]\n'
            '->  given step_02 [passed]')
        self.assertEqual(expected_comment, comment)

    def test_format_duration(self):
        testrail_reporter = TestrailReporter('master')
        duration = 69
        formatted_duration = testrail_reporter._format_duration(duration)

        self.assertEquals('69s', formatted_duration)

    def test_format_duration_return_one_for_zero_durations(self):
        testrail_reporter = TestrailReporter('master')
        duration = 0
        formatted_duration = testrail_reporter._format_duration(duration)

        self.assertEquals('1s', formatted_duration)


class TestrailReporterTestLoadConfig(unittest.TestCase):
    def test_config_file_is_not_present(self):
        with self.assertRaises(Exception) as context:
            TestrailReporter('master')

        exception_message = 'Could not read `testrail.yml` file, check the file exists in root of your project.'
        self.assertTrue(exception_message in context.exception.args[0])

    def test_config_file_is_not_valid_yaml_file(self):
        self.addCleanup(partial(os.remove, 'testrail.yml'))
        with open('testrail.yml', 'w') as outfile:
            outfile.write('-\n--\n---')

        with self.assertRaises(Exception) as context:
            TestrailReporter('master')

        exception_message = 'Error loading testrail.yml file:'
        self.assertTrue(exception_message in context.exception.args[0])

    def test_config_file_is_missing_base_url(self):
        self.addCleanup(partial(os.remove, 'testrail.yml'))
        data = {
            'projects': [
                {
                    'name': 'Testrail project name',
                    'id': 1,
                    'suite_id': 11,
                    'allowed_branch_pattern': '*',
                },
            ]
        }

        with open('testrail.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

        with self.assertRaises(Exception) as context:
            TestrailReporter('master')

        exception_message = 'Invalid testrail.yml file! error: \'base_url\' is a required property'
        self.assertEquals(exception_message, context.exception.args[0])

    def test_config_file_without_projects(self):
        self.addCleanup(partial(os.remove, 'testrail.yml'))
        data = {
            'base_url': 'https://test.testrail.net',
            'projects': []
        }

        with open('testrail.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

        with self.assertRaises(Exception) as context:
            TestrailReporter('master')

        exception_message = 'Your testrail.yml config file does not have any project configured!'
        self.assertEquals(exception_message, context.exception.args[0])
