from logging import getLogger
from pyramid.config import Configurator


logger = getLogger(__name__)


def aview(request):
    logger.info("request: %r", {"REMOTE_ADDR": request.remote_addr})
    return "OK"


def app_factory(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_route("root", pattern="/")
    config.add_view(aview, route_name="root", renderer="json")
    logger.info("app created")
    return config.make_wsgi_app()
