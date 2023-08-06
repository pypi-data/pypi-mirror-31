import datetime

from flask import request

import flask_monitoringdashboard.views.export.csv
import flask_monitoringdashboard.views.export.json
from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.tests import add_or_update_test, add_test_result, get_suite_nr
from flask_monitoringdashboard.database.tests_grouped import reset_tests_grouped, add_tests_grouped


@blueprint.route('/submit-test-results', methods=['POST'])
def submit_test_results():
    content = request.get_json()['test_runs']
    with session_scope() as db_session:
        suite = get_suite_nr(db_session)
        for result in content:
            time = datetime.datetime.strptime(result['time'], '%Y-%m-%d %H:%M:%S.%f')
            add_or_update_test(db_session, result['name'], time, result['successful'])
            add_test_result(db_session, result['name'], result['exec_time'], time, config.version, suite,
                            result['iter'])

        groups = request.get_json()['grouped_tests']
        if groups:
            reset_tests_grouped(db_session)
            add_tests_grouped(db_session, groups)

    return '', 204
