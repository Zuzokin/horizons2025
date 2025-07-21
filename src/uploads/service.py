import io
import pandas as pd
from fastapi import UploadFile
from pydantic import BaseModel
from src.entities.generated_models import EndConsumer, Factory, Financial, Geo, MetalTrader, Payer,PipeClassification, Product,ProductionUnit,Receiver, Shipment
from sqlalchemy.orm import Session

class UploadResult(BaseModel):
    rows_loaded: int

class ExcelUploadService:
    async def process(self, file: UploadFile, db: Session) -> UploadResult:
        # считываем всё в память
        content = await file.read()
        # читаем в pandas
        try:
            df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise ValueError("не удалось прочитать Excel: " + str(e))



        # простая валидация: есть ли колонки
        # expected = {"client_id", "industry", "region", "volume", "date"}
        # missing = expected - set(df.columns.str.lower())
        # if missing:
        #     raise ValueError(f"Отсутствуют обязательные колонки: {set(df.columns.str.lower())}")

        # TODO: нормализовать колонки, типы данных,
        # загрузить в БД через слой репозиториев

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


        saved = 0
        for _, row in df.iterrows():
            # 1) Shipment
            sh = Shipment(
                shipment_year   = row.get('year'),
                month           = row.get('month'),
                actual_shipment_date = pd.to_datetime(row.get('date'), errors='coerce'),
                sales_department= row.get('sales_department'),
                curator         = row.get('curator'),
                incoterms       = row.get('incoterms'),
                incoterms_location = row.get('incoterms_location'),
                hs_code         = row.get('hs_code'),
                gtd_number      = str(row.get('gtd_number')) if row.get('gtd_number') else None,
                gtd_date        = pd.to_datetime(row.get('gtd_date'), errors='coerce'),
                shipment_direction = row.get('shipment_direction'),
                shipment_type   = row.get('shipment_type'),
                line_number     = None,  # если надо, добавьте маппинг
                zru_from_kd     = None,
                igk_from_ks     = None,
            )
            self.db.add(sh)
            self.db.flush()  # получает sh.shipment_id

            # 2) Factory
            fac = Factory(
                workshop   = row.get('workshop'),
                mill       = row.get('mill'),
                plant      = None,
                shipment_id= sh.shipment_id
            )
            # 3) ProductionUnit
            pu = ProductionUnit(
                mzk        = row.get('mzk'),
                mzk_receiver = row.get('mzk_receiver'),
                oh         = row.get('oh'),
                shipment_id= sh.shipment_id
            )
            # 4) Product
            prod = Product(
                material_short_name = row.get('material_short_name'),
                material_full_name  = row.get('material_full_name'),
                outer_diameter_mm   = row.get('outer_diameter_mm'),
                dimension_1_mm      = row.get('dimension_1_mm'),
                dimension_2_mm      = row.get('dimension_2_mm'),
                wall_thickness_mm   = row.get('wall_thickness_mm'),
                pipe_length_mm      = row.get('pipe_length_mm'),
                steel_grade         = row.get('steel_grade'),
                strength_group      = row.get('strength_group'),
                thread_type         = row.get('thread_type'),
                upset               = row.get('upset'),
                heat_treatment_flag = row.get('heat_treatment_flag'),
                pipe_type_m1        = row.get('pipe_type_m1'),
                pipe_type_m2        = row.get('pipe_type_m2'),
                pipe_type_m3        = row.get('pipe_type_m3'),
                pipe_type_m4_special= row.get('pipe_type_m4_special'),
                quantity_m          = row.get('quantity_m'),
                quantity_pcs        = row.get('quantity_pcs'),
                shipment_id         = sh.shipment_id
            )
            # 5) PipeClassification
            pc = PipeClassification(
                business_type        = row.get('business_type'),
                business_segment_m3  = row.get('business_segment_m3'),
                shipment_id          = sh.shipment_id
            )
            # 6) Receiver
            rec = Receiver(
                receiver_name            = row.get('receiver_name'),
                receiver_operational_name= row.get('receiver_operational_name'),
                receiver_address         = row.get('receiver_address'),
                receiver_inn             = row.get('receiver_inn'),
                receiver_okpo            = row.get('receiver_okpo'),
                receiver_city            = row.get('receiver_city'),
                receiver_region          = row.get('receiver_region'),
                receiver_country         = row.get('receiver_country'),
                shipment_id              = sh.shipment_id
            )
            # 7) Payer
            payer = Payer(
                payer_name         = row.get('payer_name'),
                payer_city         = row.get('payer_city'),
                payer_country      = row.get('payer_country'),
                payer_inn          = row.get('payer_inn'),
                payer_okpo         = row.get('payer_okpo'),
                payer_internal_code= row.get('payer_internal_code'),
                shipment_id        = sh.shipment_id
            )
            # 8) MetalTrader
            mt = MetalTrader(
                metal_trader = row.get('metal_trader'),
                shipment_id  = sh.shipment_id
            )
            # 9) Geo
            geo = Geo(
                delivery_region_ru           = row.get('delivery_region_ru'),
                federal_district_ru_or_world_region = row.get('federal_district_ru_or_world_region'),
                destination_country          = row.get('destination_country'),
                destination_station          = row.get('destination_station'),
                shipment_id                  = sh.shipment_id
            )
            # 10) Financial
            fin = Financial(
                weight_ton            = row.get('weight_ton'),
                document_currency     = row.get('document_currency'),
                td_currency_rate      = row.get('td_currency_rate'),
                td_cost_excl_vat_rub  = row.get('td_cost_excl_vat_rub'),
                td_price_excl_vat_per_ton_rub = row.get('td_price_excl_vat_per_ton_rub'),
                pfm_code              = row.get('pfm_code'),
                pfm_text              = row.get('pfm_text'),
                shipment_id           = sh.shipment_id
            )
            # 11) EndConsumer
            ec = EndConsumer(
                end_consumer_name             = row.get('end_consumer_name'),
                end_consumer_okpo             = row.get('end_consumer_okpo'),
                end_consumer_industry         = row.get('end_consumer_industry'),
                end_consumer_subindustry      = row.get('end_consumer_subindustry'),
                end_consumer_subindustry_2_or_product = row.get('end_consumer_subindustry_2_or_product'),
                shipment_id                   = sh.shipment_id
            )

            # Добавляем все
            self.db.add_all([fac, pu, prod, pc, rec, payer, mt, geo, fin, ec])
            saved += 1

        # Коммит в конце
        self.db.commit()
        return saved
