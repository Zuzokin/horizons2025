from dash import dcc, html, Input, Output, State
import pandas as pd
import os
import plotly.express as px

def industry_cut_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    # Pre-process data to avoid errors
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    
    unique_industries = df_bd["Отрасль Основного Потребителя"].dropna().unique()
    unique_regions = df_bd["Регион ПОСТАВКИ РФ"].dropna().unique()
    
    return html.Div([
        html.H2("Отраслевой срез: Топ-5 заказчиков"),
        html.Div([
            html.Label("Отрасль Основного Потребителя"),
            dcc.Dropdown(
                id="end_consumer_industry",
                options=[{"label": i, "value": i} for i in unique_industries],
                placeholder="Выберите одну или несколько отраслей",
                multi=True,
                style={"width": "400px"}
            ),
            html.Label("Регион ПОСТАВКИ РФ", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="delivery_region_ru",
                options=[{"label": r, "value": r} for r in unique_regions],
                placeholder="Выберите один или несколько регионов",
                multi=True,
                style={"width": "400px", "display": "inline-block", "marginLeft": "5px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px"}),
        html.Div([
            html.Label("Дата отгрузки"),
            dcc.DatePickerRange(
                id='industry-cut-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить диаграмму", id="BT_REFRESH_INDUSTRY", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px"}),
        html.Div(id="industry-cut-graph-container")
    ], style={"padding": "20px"})

def register_industry_cut_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    # Pre-process data to avoid errors
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")

    @app.callback(
        Output("industry-cut-graph-container", "children"),
        Input("BT_REFRESH_INDUSTRY", "n_clicks"),
        [State("end_consumer_industry", "value"),
         State("delivery_region_ru", "value"),
         State("industry-cut-date-picker-range", "start_date"),
         State("industry-cut-date-picker-range", "end_date")]
    )
    def update_industry_cut_graph(n_clicks, industries, regions, start_date, end_date):
        if n_clicks == 0:
            return html.Div("Настройте фильтры и нажмите 'Обновить диаграмму'", style={"color": "grey"})
            
        dff = df_bd.copy()

        if industries:
            dff = dff[dff["Отрасль Основного Потребителя"].isin(industries)]
        if regions:
            dff = dff[dff["Регион ПОСТАВКИ РФ"].isin(regions)]

        if start_date:
            try:
                period_in_dt = pd.to_datetime(start_date)
                dff = dff[dff["Дата фактической отгрузки"] >= period_in_dt]
            except Exception:
                pass
        if end_date:
            try:
                period_out_dt = pd.to_datetime(end_date)
                dff = dff[dff["Дата фактической отгрузки"] <= period_out_dt]
            except Exception:
                pass

        if dff.empty:
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"})

        # Group by customer and sum weight, then get top 5
        top_5 = dff.groupby("Основной Потребитель")["Вес, тн."].sum().nlargest(5).reset_index()

        if top_5.empty:
            return html.Div("Нет данных для построения диаграммы после агрегации.", style={"color": "orange"})

        fig = px.pie(top_5, 
                     names="Основной Потребитель", 
                     values="Вес, тн.", 
                     title="Топ-5 заказчиков по объему")
        
        return dcc.Graph(figure=fig) 