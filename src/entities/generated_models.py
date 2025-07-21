from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..database.core import Base
import uuid


class EndConsumer(Base):
    __tablename__ = 'end_consumer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    end_consumer_name = Column(String, nullable=True)
    end_consumer_okpo = Column(Integer, nullable=True)
    end_consumer_industry = Column(String, nullable=True)
    end_consumer_subindustry = Column(String, nullable=True)
    end_consumer_subindustry_2_or_product = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Factory(Base):
    __tablename__ = 'factory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workshop = Column(String, nullable=True)
    mill = Column(String, nullable=True)
    plant = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Financial(Base):
    __tablename__ = 'financial'

    id = Column(Integer, primary_key=True, autoincrement=True)
    weight_ton = Column(String, nullable=True)
    document_currency = Column(String, nullable=True)
    td_currency_rate = Column(String, nullable=True)
    td_cost_excl_vat_rub = Column(Integer, nullable=True)
    td_price_excl_vat_per_ton_rub = Column(Integer, nullable=True)
    pfm_code = Column(String, nullable=True)
    pfm_text = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Geo(Base):
    __tablename__ = 'geo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_region_ru = Column(String, nullable=True)
    federal_district_ru_or_world_region = Column(String, nullable=True)
    destination_country = Column(String, nullable=True)
    destination_station = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class MetalTrader(Base):
    __tablename__ = 'metal_trader'

    id = Column(Integer, primary_key=True, autoincrement=True)
    metal_trader = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Payer(Base):
    __tablename__ = 'payer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    payer_name = Column(String, nullable=True)
    payer_operational_name = Column(String, nullable=True)
    payer_city = Column(String, nullable=True)
    payer_country = Column(String, nullable=True)
    payer_inn = Column(Integer, nullable=True)
    payer_okpo = Column(Integer, nullable=True)
    payer_internal_code = Column(Integer, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class PipeClassification(Base):
    __tablename__ = 'pipe_classification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipe_type_m1 = Column(String, nullable=True)
    pipe_type_m2 = Column(String, nullable=True)
    pipe_type_m3 = Column(String, nullable=True)
    pipe_type_m4_special = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    pipe_business_type_m1 = Column(String, nullable=True)
    business_segment_m3 = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_short_name = Column(String, nullable=True)
    material_full_name = Column(String, nullable=True)
    external_material_group_code = Column(String, nullable=True)
    steel_grade = Column(String, nullable=True)
    strength_group = Column(String, nullable=True)
    outer_diameter_mm = Column(String, nullable=True)
    dimension_1_mm = Column(String, nullable=True)
    dimension_2_mm = Column(String, nullable=True)
    wall_thickness_mm = Column(String, nullable=True)
    pipe_length_mm = Column(Integer, nullable=True)
    thread_type = Column(String, nullable=True)
    upset = Column(String, nullable=True)
    heat_treatment_flag = Column(String, nullable=True)
    pipe_standard = Column(String, nullable=True)
    coating_specification = Column(String, nullable=True)
    internal_coating_specification = Column(String, nullable=True)
    quantity_m = Column(String, nullable=True)
    quantity_pcs = Column(Integer, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class ProductionUnit(Base):
    __tablename__ = 'production_unit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mzk = Column(String, nullable=True)
    mzk_receiver = Column(String, nullable=True)
    oh = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Receiver(Base):
    __tablename__ = 'receiver'

    id = Column(Integer, primary_key=True, autoincrement=True)
    receiver_name = Column(String, nullable=True)
    receiver_operational_name = Column(String, nullable=True)
    receiver_address = Column(String, nullable=True)
    receiver_inn = Column(Integer, nullable=True)
    receiver_okpo = Column(Integer, nullable=True)
    receiver_internal_code = Column(Integer, nullable=True)
    receiver_city = Column(String, nullable=True)
    receiver_country = Column(String, nullable=True)
    receiver_region = Column(String, nullable=True)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipment.shipment_id'), nullable=True)


class Shipment(Base):
    __tablename__ = 'shipment'

    shipment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    shipment_year = Column(Integer, nullable=True)
    month = Column(String, nullable=True)
    actual_shipment_date = Column(DateTime, nullable=True)
    sales_department = Column(String, nullable=True)
    curator = Column(String, nullable=True)
    incoterms = Column(String, nullable=True)
    incoterms_location = Column(String, nullable=True)
    hs_code = Column(String, nullable=True)
    gtd_number = Column(String, nullable=True)
    gtd_date = Column(String, nullable=True)
    shipment_direction = Column(String, nullable=True)
    shipment_type = Column(String, nullable=True)
    line_number = Column(String, nullable=True)
    zru_from_kd = Column(String, nullable=True)
    igk_from_ks = Column(String, nullable=True)
