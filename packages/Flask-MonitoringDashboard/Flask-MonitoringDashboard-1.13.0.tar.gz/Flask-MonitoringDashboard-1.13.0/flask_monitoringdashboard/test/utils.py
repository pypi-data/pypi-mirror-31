"""
    Some useful functions for setting up the testing environment, adding data, etc..
"""
import datetime

import pytz
from flask import Flask

NAME = 'main'
IP = '127.0.0.1'
GROUP_BY = '1'
EXECUTION_TIMES = [1000, 2000, 3000, 4000, 50000]
TIMES = [datetime.datetime.utcnow()] * 5
OUTLIER_COUNT = 3
for i in range(len(TIMES)):
    TIMES[i] -= datetime.timedelta(seconds=len(EXECUTION_TIMES)-i)
TEST_NAMES = ['test_name1', 'test_name2']


def set_test_environment():
    """ Override the config-object for a new testing environment. Module flask_monitoringdashboard
    must be imported locally. """
    import flask_monitoringdashboard
    flask_monitoringdashboard.config.database_name = 'sqlite:///test-database.db'


def clear_db():
    """ Drops and creates the tables in the database. Module flask_monitoringdashboard must be imported locally. """
    from flask_monitoringdashboard.database import get_tables, engine
    for table in get_tables():
        table.__table__.drop(engine)
        table.__table__.create(engine)


def add_fake_data():
    """ Adds data to the database for testing purposes. Module flask_monitoringdashboard must be imported locally. """
    from flask_monitoringdashboard.database import session_scope, FunctionCall, MonitorRule, Outlier, Tests,\
        TestsGrouped
    from flask_monitoringdashboard import config

    # Add functionCalls
    with session_scope() as db_session:
        for i in range(len(EXECUTION_TIMES)):
            call = FunctionCall(endpoint=NAME, execution_time=EXECUTION_TIMES[i], version=config.version,
                                time=TIMES[i], group_by=GROUP_BY, ip=IP)
            db_session.add(call)

    # Add MonitorRule
    with session_scope() as db_session:
        db_session.add(MonitorRule(endpoint=NAME, monitor=True, time_added=datetime.datetime.utcnow(),
                                   version_added=config.version, last_accessed=TIMES[0]))

    # Add Outliers
    with session_scope() as db_session:
        for i in range(OUTLIER_COUNT):
            db_session.add(Outlier(endpoint=NAME, cpu_percent='[%d, %d, %d, %d]' % (i, i + 1, i + 2, i + 3),
                                   execution_time = 100 * (i + 1), time = TIMES[i]))
    # Add Tests
    with session_scope() as db_session:
        db_session.add(Tests(name=NAME, succeeded=True))

    # Add TestsGrouped
    with session_scope() as db_session:
        for test_name in TEST_NAMES:
            db_session.add(TestsGrouped(endpoint=NAME, test_name=test_name))


def get_test_app():
    """
    :return: Flask Test Application with the right settings
    """
    import flask_monitoringdashboard
    user_app = Flask(__name__)
    user_app.config['SECRET_KEY'] = flask_monitoringdashboard.config.security_token
    user_app.testing = True
    flask_monitoringdashboard.user_app = user_app
    user_app.config['WTF_CSRF_ENABLED'] = False
    user_app.config['WTF_CSRF_METHODS'] = []
    flask_monitoringdashboard.config.get_group_by = lambda: '12345'
    flask_monitoringdashboard.bind(app=user_app)
    return user_app


def login(test_app):
    """
    Used for setting the sessions, such that you have a fake login to the flask_monitoringdashboard.
    :param test_app:
    """
    from flask_monitoringdashboard import config
    with test_app.session_transaction() as sess:
        sess[config.link + '_logged_in'] = True
        sess[config.link + '_admin'] = True


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def test_admin_secure(test_case, page):
    """
    Test whether the page is only accessible with admin credentials.
    :param test_case: test class, must be an instance of unittest.TestCase
    :param page: str with the page of the flask_monitoringdashboard
    """
    with test_case.app.test_client() as c:
        test_case.assertEqual(302, c.get('dashboard/{}'.format(page)).status_code)
        login(c)
        test_case.assertEqual(200, c.get('dashboard/{}'.format(page)).status_code)