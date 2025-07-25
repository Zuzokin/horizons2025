from dash_app.app  import create_dash_app
from .database.core import engine, Base
from .entities.generated_models import EndConsumer

from .api import register_routes
from .logging import configure_logging, LogLevels

from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware


configure_logging(LogLevels.info)

app = FastAPI()


# Монтируем Dash приложение
dash_app = create_dash_app()

# Монтируем Dash как WSGI приложениеgit
app.mount("/dash", WSGIMiddleware(dash_app.server))

Base.metadata.create_all(bind=engine)
register_routes(app)