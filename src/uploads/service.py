import io
import pandas as pd
from fastapi import UploadFile
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from src.entities.generated_models import EndConsumer, Factory, Financial, Geo, MetalTrader, Payer,PipeClassification, Product,ProductionUnit,Receiver, Shipment
from sqlalchemy.orm import Session

class UploadResult(BaseModel):
    rows_loaded: int


def process(file: UploadFile, db: Session) -> UploadResult:
    # Считываем файл в память
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise ValueError("Не удалось прочитать Excel: " + str(e))

    df = df.rename(columns={
        'Год отгрузки': 'year',
        'Месяц': 'month',
        'Дата фактической отгрузки': 'date',
        'Цех': 'workshop',
        'Стан': 'mill',
        'МЗК': 'mzk',
        'Получатель МЗК': 'mzk_receiver',
        'ОХ': 'oh',
        'Краткое наименование материала': 'material_short_name',
        'Полное наименование материала': 'material_full_name',
        'Диаметр наружный, мм': 'outer_diameter_mm',
        'Размер 1, мм': 'dimension_1_mm',
        'Размер 2, мм': 'dimension_2_mm',
        'Стенка, мм': 'wall_thickness_mm',
        'Длина трубы, мм': 'pipe_length_mm',
        'Марка стали': 'steel_grade',
        'Группа прочности': 'strength_group',
        'Тип Резьбы': 'thread_type',
        'Высадка': 'upset',
        'Признак термообрабоки': 'heat_treatment_flag',
        'Вид труб-М1': 'pipe_type_m1',
        'Вид труб-М2': 'pipe_type_m2',
        'Вид труб-М3': 'pipe_type_m3',
        'Вид труб-М4-Спец': 'pipe_type_m4_special',
        'Вес, тн.': 'weight_ton',
        'Валюта Документа': 'document_currency',
        'Валютный курс с/ф ТД': 'td_currency_rate',
        'Стоимость ТД без НДС, руб.': 'td_cost_excl_vat_rub',
        'Цена ТД без НДС, руб./тн.': 'td_price_excl_vat_per_ton_rub',
        'Инкотермс': 'incoterms',
        'Инкотермс, Место': 'incoterms_location',
        'Код ТН ВЭД': 'hs_code',
        'Номер ГТД': 'gtd_number',
        'Дата ГТД': 'gtd_date',
        'Отдел Сбыта': 'sales_department',
        'ПФМ Код': 'pfm_code',
        'ПФМ Текст': 'pfm_text',
        'Куратор': 'curator',
        'Вид трубы Бизнес (M1)': 'business_type',
        'Сегмент Бизнес (M3)': 'business_segment_m3',
        'Получатель рабочее наименование': 'receiver_operational_name',
        'ИНН получателя': 'receiver_inn',
        'ОКПО получателя': 'receiver_okpo',
        'Получатель': 'receiver_name',
        'Адрес Получателя': 'receiver_address',
        'Город Получателя': 'receiver_city',
        'Регион Получателя': 'receiver_region',
        'Страна Получателя': 'receiver_country',
        'Станция назначения': 'destination_station',
        'Тип отгрузки': 'shipment_type',
        'Внутр.номер Плательщика': 'payer_internal_code',
        'ИНН плательщика': 'payer_inn',
        'ОКПО плательщика': 'payer_okpo',
        'Плательщик': 'payer_name',
        'Город Плательщика': 'payer_city',
        'Страна Плательщика': 'payer_country',
        'Металлотрейдер': 'metal_trader',
        'Регион ПОСТАВКИ РФ': 'delivery_region_ru',
        'Фед.округ РФ/ Регион мира': 'federal_district_ru_or_world_region',
        'Страна назначения': 'destination_country',
        'Направление отгрузки': 'shipment_direction',
        'Отрасль Основного Потребителя': 'end_consumer_industry',
        'Подотрасль Основного Потребителя': 'end_consumer_subindustry',
        'Подотрасль потребителя 2 /продукт': 'end_consumer_subindustry_2_or_product',
        'ОКПО основного потребителя': 'end_consumer_okpo',
        'Основной Потребитель': 'end_consumer_name',
        'Количество, м': 'quantity_m',
        'Количество, шт.': 'quantity_pcs',
        # ... добавьте остальные маппинги по необходимости
    })

    rows_loaded = 0
    for _, row in df.iterrows():

        sh = Shipment(
            shipment_year        = row.get('year'),
            month                = row.get('month'),
            actual_shipment_date = pd.to_datetime(row.get('date'), errors='coerce'),
            sales_department     = row.get('sales_department'),
            curator              = row.get('curator'),
        )
        db.add(sh)
        rows_loaded += 1
    db.commit()
    return UploadResult(rows_loaded=rows_loaded)