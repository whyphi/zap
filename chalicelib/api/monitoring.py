from chalice import Blueprint
from chalicelib.services.MonitoringService import monitoring_service
from chalicelib.decorators import auth
from chalicelib.models.roles import Roles

monitoring_api = Blueprint(__name__)


@monitoring_api.route("/monitoring/visited-pages", methods=["GET"], cors=True)
@auth(monitoring_api, roles=[Roles.ADMIN])
def get_top_10_visited_pages():
    return monitoring_service.get_top_10_visited_pages()