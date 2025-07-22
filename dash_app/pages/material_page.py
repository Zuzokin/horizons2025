from dash import dcc, html, Input, Output, State
import pandas as pd
import os
import plotly.graph_objs as go

def material_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    unique_items = df_bd["Краткое наименование материала"].dropna().unique()
    unique_plants = df_bd["Завод"].dropna().unique()
    return html.Div([
        html.H2("Отчет по материалу"),
        html.Div([
            html.Label("Наименование материала*"),
            dcc.Dropdown(
                id="CB_ITEM_NAME",
                options=[{"label": i, "value": i} for i in unique_items],
                placeholder="Выберите материал",
                style={"width": "350px"}
            ),
            html.Label("Завод", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="CB_PLANTS",
                options=[{"label": p, "value": p} for p in unique_plants],
                placeholder="Завод (необязательно)",
                style={"width": "200px", "display": "inline-block", "marginLeft": "5px"}
            ),
            html.Label("Дата отгрузки", style={"marginLeft": "20px"}),
            dcc.DatePickerRange(
                id='material-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить диаграмму", id="BT_REFRESH_MATERIAL", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px", "flexWrap": "wrap"}),
        html.Div(id="material-graph-container")
    ], style={"padding": "20px"})

def register_material_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    @app.callback(
        Output("material-graph-container", "children"),
        Input("BT_REFRESH_MATERIAL", "n_clicks"),
        [State("CB_ITEM_NAME", "value"),
         State("material-date-picker-range", "start_date"),
         State("material-date-picker-range", "end_date"),
         State("CB_PLANTS", "value")]
    )
    def update_material_graph(n_clicks, item_name, start_date, end_date, plant):
        if not item_name:
            return html.Div("Пожалуйста, выберите материал (обязательное поле)", style={"color": "red"})
        dff = df_bd[df_bd["Краткое наименование материала"] == item_name]
        if plant:
            dff = dff[dff["Завод"] == plant]
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
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"})
        grouped = dff.groupby("Регион Получателя").agg({
            "Вес, тн.": "sum",
            "Цена ТД без НДС, руб./тн.": "sum"
        }).reset_index()
        fig = go.Figure()
        fig.add_bar(x=grouped["Регион Получателя"], y=grouped["Вес, тн."], name="Вес, тн.")
        fig.add_bar(x=grouped["Регион Получателя"], y=grouped["Цена ТД без НДС, руб./тн."], name="Цена ТД без НДС, руб./тн.")
        fig.update_layout(barmode="group", title="Поставки по регионам для выбранного материала", xaxis_title="Регион", yaxis_title="Значение")
        return dcc.Graph(figure=fig) 