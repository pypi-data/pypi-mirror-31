from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.core.utils import get_endpoint_details, simplify
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.data_grouped import get_version_data_grouped
from flask_monitoringdashboard.database.endpoint import to_local_datetime
from flask_monitoringdashboard.database.versions import get_versions, get_first_requests

TITLE = 'Per-Version Performance'

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents the versions 
that are used.'''

CONTENT_INFO = '''This graph shows a horizontal boxplot for the versions that are used. With this
graph you can found out whether the performance changes across different versions.'''


@blueprint.route('/endpoint/<end>/versions', methods=['GET', 'POST'])
@secure
def versions(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        graph = versions_graph(db_session, end)
        return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph,
                               title='{} for {}'.format(TITLE, end),
                               information=get_information(AXES_INFO, CONTENT_INFO))


def format_version(version, first_used):
    """
    :param version: name of the version
    :param first_used: datetime object when the version was first used.
    :return: string that represents the version
    """
    if not first_used:
        return version
    return '{}<br>{}'.format(version, to_local_datetime(first_used).strftime('%Y-%m-%d %H:%M'))


def versions_graph(db_session, end):
    versions = get_versions(db_session, end=end)
    times = get_version_data_grouped(db_session, lambda x: simplify(x, 10), FunctionCall.endpoint == end)
    used = get_first_requests(db_session)
    data = [boxplot(name=format_version(v, get_value(used, v)), values=get_value(times, v),
                    marker={'color': get_color(v)})
            for v in versions]

    layout = get_layout(
        height=350 + 40 * len(versions),
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'Version', 'autorange': 'reversed'},
        margin=get_margin()
    )
    return get_figure(layout=layout, data=data)
