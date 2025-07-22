from sqlalchemy import Column, String, BigInteger, Float, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from ..database.core import Base
import uuid

class DataUnloading(Base):
    __tablename__ = 'unloading_data'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    td = Column(String, nullable=True)
    plant = Column(String, nullable=True)
    year = Column(String, nullable=True)
    month = Column(String, nullable=True)
    shipment_date = Column(DateTime, nullable=True)
    workshop = Column(String, nullable=True)
    mill = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    pipe_standard = Column(String, nullable=True)
    diameter_mm = Column(String, nullable=True)
    length_1_m = Column(String, nullable=True)
    length_2_m = Column(String, nullable=True)
    wall_thickness_mm = Column(String, nullable=True)
    strength_group = Column(Float, nullable=True)  # NUMERIC
    thread_type = Column(String, nullable=True)
    weight_ton = Column(Float, nullable=True)  # NUMERIC
    incoterms = Column(String, nullable=True)
    hs_code = Column(Float, nullable=True)  # NUMERIC
    consignee_code = Column(String, nullable=True)
    receiver_name = Column(String, nullable=True)
    receiver_address = Column(String, nullable=True)
    receiver_city = Column(String, nullable=True)
    receiver_region = Column(String, nullable=True)
    receiver_country = Column(String, nullable=True)
    destination_station = Column(String, nullable=True)
    payer_code = Column(String, nullable=True)
    payer_okpo = Column(String, nullable=True)
    payer_inn = Column(String, nullable=True)
    payer_name = Column(String, nullable=True)
    payer_city = Column(String, nullable=True)
    payer_country = Column(String, nullable=True)
    metal_trader = Column(String, nullable=True)
    quantity_pcs = Column(Float, nullable=True)  # NUMERIC