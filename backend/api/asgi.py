from api.app import create_app
from api.settings import settings

api = create_app(settings)
