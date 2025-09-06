# TO BE COMPLETED: create api routes for analytics
from chalice.app import Blueprint
from chalicelib.services.InsightsService import InsightsService
from chalicelib.decorators import auth
from chalicelib.models.roles import Roles


insights_api = Blueprint(__name__)


def register_routes(insights_service: InsightsService):

    @insights_api.route("/insights/listing/{listing_id}", methods=["GET"], cors=True)
    @auth(insights_api, roles=[Roles.ADMIN, Roles.MEMBER])
    def get_listing_insights(listing_id):
        """Get insights from <listing_id>"""
        return insights_service.get_insights_from_listing(listing_id)
