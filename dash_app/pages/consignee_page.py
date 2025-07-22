from dash import dcc, html, Input, Output, State
import pandas as pd
import os
import plotly.graph_objs as go

def consignee_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    unique_consignees = df_bd["Получатель рабочее наименование"].dropna().unique()
    return html.Div([
        html.H2("Отчет по грузополучателю"),
        html.Div([
            html.Label("Грузополучатель*"),
            dcc.Dropdown(
                id="CB_CONSIGNEE_CODE",
                options=[{"label": c, "value": c} for c in unique_consignees],
                placeholder="Выберите грузополучателя",
                style={"width": "350px"}
            ),
            html.Label("Наименование грузополучателя", style={"marginLeft": "20px"}),
            dcc.Input(id="RECEIVER_NAME", type="text", readOnly=True, style={"width": "350px"}),
            html.Label("Дата отгрузки", style={"marginLeft": "20px"}),
            dcc.DatePickerRange(
                id='consignee-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить диаграмму", id="BT_REFRESH_CONSIGNEE", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px", "flexWrap": "wrap"}),
        html.Div(id="consignee-graph-container")
    ], style={"padding": "20px"})

def register_consignee_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    @app.callback(
        Output("RECEIVER_NAME", "value"),
        Input("CB_CONSIGNEE_CODE", "value")
    )
    def update_receiver_name(consignee):
        if not consignee:
            return ""
        return consignee

    @app.callback(
        Output("consignee-graph-container", "children"),
        Input("BT_REFRESH_CONSIGNEE", "n_clicks"),
        [State("CB_CONSIGNEE_CODE", "value"),
         State("consignee-date-picker-range", "start_date"),
         State("consignee-date-picker-range", "end_date")]
    )
    def update_consignee_graph(n_clicks, consignee, start_date, end_date):
        if not consignee:
            return html.Div("Пожалуйста, выберите грузополучателя (обязательное поле)", style={"color": "red"})
        dff = df_bd[df_bd["Получатель рабочее наименование"] == consignee]
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
        grouped = dff.groupby("Завод").agg({
            "Вес, тн.": "sum",
            "Цена ТД без НДС, руб./тн.": "sum"
        }).reset_index()
        fig = go.Figure()
        fig.add_bar(x=grouped["Завод"], y=grouped["Вес, тн."], name="Вес, тн.")
        fig.add_bar(x=grouped["Завод"], y=grouped["Цена ТД без НДС, руб./тн."], name="Цена ТД без НДС, руб./тн.")
        fig.update_layout(barmode="group", title="Поставки по заводам для выбранного грузополучателя", xaxis_title="Завод", yaxis_title="Значение")
        return dcc.Graph(figure=fig) 