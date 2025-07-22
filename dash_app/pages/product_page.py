from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import os
import plotly.graph_objs as go

def product_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    unique_pipe_types = df_bd["Вид труб-М1"].dropna().unique()
    unique_industries = df_bd["Отрасль Основного Потребителя"].dropna().unique()
    unique_subindustries = df_bd["Подотрасль Основного Потребителя"].dropna().unique()
    return html.Div([
        html.H2("Продукт: востребованность по отраслям"),
        html.Div([
            html.Label("Вид труб-М1"),
            dcc.Dropdown(
                id="product_pipe_type_m1",
                options=[{"label": p, "value": p} for p in unique_pipe_types],
                placeholder="Выберите вид труб",
                style={"width": "250px"}
            ),
            html.Label("Отрасль", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="product_end_consumer_industry",
                options=[{"label": i, "value": i} for i in unique_industries],
                placeholder="Выберите отрасль",
                style={"width": "250px"}
            ),
            html.Label("Подотрасль", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="product_end_consumer_subindustry",
                options=[{"label": s, "value": s} for s in unique_subindustries],
                placeholder="Выберите подотрасль (опционально)",
                style={"width": "250px"}
            ),
            html.Label("Дата отгрузки", style={"marginLeft": "20px"}),
            dcc.DatePickerRange(
                id='product-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить отчет", id="BT_REFRESH_PRODUCT", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px", "flexWrap": "wrap"}),
        html.Div(id="product-graph-container"),
        html.Hr(),
        html.H3("Детализация по продукту"),
        html.Div(id="product-table-container")
    ], style={"padding": "20px"})

def register_product_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    @app.callback(
        [Output("product-graph-container", "children"),
         Output("product-table-container", "children")],
        Input("BT_REFRESH_PRODUCT", "n_clicks"),
        [State("product_pipe_type_m1", "value"),
         State("product-date-picker-range", "start_date"),
         State("product-date-picker-range", "end_date"),
         State("product_end_consumer_industry", "value"),
         State("product_end_consumer_subindustry", "value")]
    )
    def update_product_report(n_clicks, pipe_type, start_date, end_date, industry, subindustry):
        dff = df_bd.copy()
        if pipe_type:
            dff = dff[dff["Вид труб-М1"] == pipe_type]
        if industry:
            dff = dff[dff["Отрасль Основного Потребителя"] == industry]
            if industry == "Машиностроение" and subindustry:
                dff = dff[dff["Подотрасль Основного Потребителя"] == subindustry]
        if start_date:
            try:
                dff = dff[dff["Дата фактической отгрузки"] >= pd.to_datetime(start_date)]
            except Exception:
                pass
        if end_date:
            try:
                dff = dff[dff["Дата фактической отгрузки"] <= pd.to_datetime(end_date)]
            except Exception:
                pass
        if dff.empty:
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"}), None
        # График по регионам
        grouped = dff.groupby("Регион ПОСТАВКИ РФ").agg({
            "Вес, тн.": "sum",
            "Цена ТД без НДС, руб./тн.": "sum"
        }).reset_index()
        fig = go.Figure()
        fig.add_bar(x=grouped["Регион ПОСТАВКИ РФ"], y=grouped["Вес, тн."], name="Вес, тн.")
        fig.add_bar(x=grouped["Регион ПОСТАВКИ РФ"], y=grouped["Цена ТД без НДС, руб./тн."], name="Цена ТД без НДС, руб./тн.")
        fig.update_layout(barmode="group", title="Поставки по регионам", xaxis_title="Регион", yaxis_title="Значение")
        # Таблица детализации
        table_df = dff[["Полное наименование материала", "Вес, тн.", "Цена ТД без НДС, руб./тн."]].copy()
        table = dash_table.DataTable(
            columns=[
                {"name": "Полное наименование материала", "id": "Полное наименование материала"},
                {"name": "Вес, тн.", "id": "Вес, тн."},
                {"name": "Цена ТД без НДС, руб./тн.", "id": "Цена ТД без НДС, руб./тн."}
            ],
            data=table_df.to_dict('records'),
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"fontWeight": "bold"}
        )
        return dcc.Graph(figure=fig), table 