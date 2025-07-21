from fastapi import FastAPI
from .database.core import engine, Base
from .entities.todo import Todo
from .entities.generated_models import EndConsumer, Factory, Financial, Geo, MetalTrader, Payer,PipeClassification, Product,ProductionUnit,Receiver, Shipment
from .entities.user import User
from .api import register_routes
from .logging import configure_logging, LogLevels


configure_logging(LogLevels.info)

app = FastAPI()

Base.metadata.create_all(bind=engine)

register_routes(app)
