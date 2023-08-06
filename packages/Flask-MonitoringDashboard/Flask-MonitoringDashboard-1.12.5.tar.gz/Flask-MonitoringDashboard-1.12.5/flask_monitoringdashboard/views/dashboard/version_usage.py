from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import get_layout, get_figure, get_margin, heatmap
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.function_calls import get_endpoints
from flask_monitoringdashboard.database.versions import get_versions

TITLE = 'Distribution of the load per endpoint per version'


@blueprint.route('/measurements/version_usage')
@secure
def version_usage():
    return render_template('fmd_dashboard/graph.html', graph=get_version_usage(), title=TITLE)


def get_version_usage():
    """
    Used for getting a Heatmap with an overview of which endpoints are used in which versions
    :return:
    """
    with session_scope() as db_session:
        endpoints = get_endpoints(db_session)
        versions = get_versions(db_session)

        hits = [[count_requests(db_session, e, FunctionCall.version == v) for v in versions] for e in endpoints]

        for i in range(len(versions)):  # compute the total number of hits in a specific version
            total_hits = max(1, sum([column[i] for column in hits]))

            for j in range(len(endpoints)):  # compute distribution
                hits[j][i] = hits[j][i] * 100 / total_hits

    layout = get_layout(
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin()
    )

    trace = heatmap(
        z=hits,
        x=versions,
        y=['{} '.format(e) for e in endpoints],
        colorbar={
            'titleside': 'top',
            'tickmode': 'array',
        }
    )
    return get_figure(layout=layout, data=[trace])
