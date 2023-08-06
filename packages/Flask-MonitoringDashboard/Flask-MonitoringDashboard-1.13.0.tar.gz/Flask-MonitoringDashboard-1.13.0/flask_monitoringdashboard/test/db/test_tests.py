"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/tests.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, mean, \
    EXECUTION_TIMES, NAME

NAME2 = 'main2'
SUITE = 3


class TestDBTests(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_get_tests(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_tests, Tests
        with session_scope() as db_session:
            result = get_tests(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, Tests(name=NAME).name)
            self.assertTrue(result[0].run)

    def test_add_test(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import add_test, get_tests
        with session_scope() as db_session:
            self.test_get_tests()  # checks if there is 1 test in the DB
            add_test(db_session, NAME2)
            self.assertEqual(len(get_tests(db_session)), 2)

    def test_add_or_update_test(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import add_or_update_test, get_tests
        import datetime
        with session_scope() as db_session:
            self.test_add_test()  # adds a new test
            self.assertEqual(NAME2, get_tests(db_session)[1].name)
            time = datetime.datetime.utcnow()
            succeeded = True
            add_or_update_test(db_session, NAME2, time, succeeded)
            result = get_tests(db_session)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[1].name, NAME2)
            self.assertEqual(result[1].lastRun, time)
            self.assertEqual(result[1].succeeded, succeeded)

    def test_add_test_result(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_results, add_test_result
        from flask_monitoringdashboard import config
        import datetime
        with session_scope() as db_session:
            self.assertEqual(get_results(db_session), [])
            for exec_time in EXECUTION_TIMES:
                add_test_result(db_session, NAME, exec_time, datetime.datetime.utcnow(), config.version, SUITE, 2)
            result = get_results(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, NAME)
            self.assertEqual(result[0].count, len(EXECUTION_TIMES))
            self.assertEqual(result[0].average, mean(EXECUTION_TIMES))

    def test_get_suite_nr(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_suite_nr, add_test_result
        from flask_monitoringdashboard import config
        import datetime
        with session_scope() as db_session:
            self.assertEqual(get_suite_nr(db_session), 1)
            add_test_result(db_session, NAME, 1234, datetime.datetime.utcnow(), config.version, SUITE, 2)
            self.assertEqual(get_suite_nr(db_session), SUITE+1)

    def test_get_results(self):
        """
            Test whether the function returns the right values.
        """
        self.test_add_test_result()  # can be replaced by test_add_test_result, since this function covers two tests

    def test_get_res_current(self):
        """
            Test whether the function returns the right values.
        """
        self.test_add_test_result()
        from flask_monitoringdashboard.database.tests import get_res_current
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            result = get_res_current(db_session, config.version)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, NAME)
            self.assertEqual(result[0].count, len(EXECUTION_TIMES))
            self.assertEqual(result[0].average, mean(EXECUTION_TIMES))

            new_version = 'new_version'
            self.assertNotEqual(new_version, config.version)
            self.assertEqual(get_res_current(db_session, new_version), [])

    def test_get_line_results(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_line_results
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            self.test_add_test_result()
            result = get_line_results(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].version, config.version)
            self.assertEqual(result[0].avg, mean(EXECUTION_TIMES))
            self.assertEqual(result[0].min, min(EXECUTION_TIMES))
            self.assertEqual(result[0].max, max(EXECUTION_TIMES))
            self.assertEqual(result[0].count, len(EXECUTION_TIMES))

    def test_get_suites(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_suites
        self.test_add_test_result()
        with session_scope() as db_session:
            self.assertEqual(get_suites(db_session), [(SUITE, )])

    def test_get_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_measurements
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            self.assertEqual(get_measurements(db_session, SUITE), [])
            self.test_add_test_result()
            result = get_measurements(db_session, SUITE)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for test_run in result:
                self.assertEqual(test_run.name, NAME)
                self.assertIn(test_run.execution_time, EXECUTION_TIMES)
                self.assertEqual(test_run.version, config.version)
                self.assertEqual(test_run.suite, SUITE)

    def test_get_test_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_test_measurements
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            self.assertEqual(get_test_measurements(db_session, NAME, SUITE), [])
            self.test_add_test_result()
            result = get_test_measurements(db_session, NAME, SUITE)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for test_run in result:
                self.assertEqual(test_run.name, NAME)
                self.assertIn(test_run.execution_time, EXECUTION_TIMES)
                self.assertEqual(test_run.version, config.version)
                self.assertEqual(test_run.suite, SUITE)
