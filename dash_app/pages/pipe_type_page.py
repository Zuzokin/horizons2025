from dash import dcc, html, Input, Output, State
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def pipe_type_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    unique_pipe_types = df_bd["Вид труб-М1"].dropna().unique()
    unique_plants = df_bd["Завод"].dropna().unique()
    return html.Div([
        html.H2("Диаграмма по видам труб"),
        html.Div([
            html.Label("Вид труб-М1*"),
            dcc.Dropdown(
                id="CB_PIPE_TYPE_M1",
                options=[{"label": p, "value": p} for p in unique_pipe_types],
                value=list(unique_pipe_types),  # по умолчанию все
                multi=True,
                placeholder="Выберите вид труб",
                style={"width": "300px"}
            ),
            html.Label("Завод", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="CB_PLANTS",
                options=[{"label": p, "value": p} for p in unique_plants],
                placeholder="Завод (необязательно)",
                style={"width": "200px", "display": "inline-block", "marginLeft": "5px"}
            ),
            html.Label("Период", style={"marginLeft": "20px"}),
            dcc.DatePickerRange(
                id='pipe-type-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить диаграмму", id="BT_REFRESH_PIPE", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px"}),
        html.Div(id="pipe-type-graph-container")
    ], style={"padding": "20px"})

def register_pipe_type_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    @app.callback(
        Output("pipe-type-graph-container", "children"),
        Input("BT_REFRESH_PIPE", "n_clicks"),
        [State("CB_PIPE_TYPE_M1", "value"),
         State("pipe-type-date-picker-range", "start_date"),
         State("pipe-type-date-picker-range", "end_date"),
         State("CB_PLANTS", "value")]
    )
    def update_pipe_type_graph(n_clicks, pipe_types, start_date, end_date, plant):
        # pipe_types теперь список или None
        dff = df_bd.copy()
        if pipe_types:
            dff = dff[dff["Вид труб-М1"].isin(pipe_types)]
        if plant:
            dff = dff[dff["Завод"] == plant]
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
        grouped = dff.groupby("Регион Получателя").agg({
            "Вес, тн.": "sum",
            "Цена ТД без НДС, руб./тн.": "sum"
        }).reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=grouped["Регион Получателя"], y=grouped["Вес, тн."], name="Вес, тн.", offsetgroup=0, secondary_y=False)
        fig.add_bar(x=grouped["Регион Получателя"], y=grouped["Цена ТД без НДС, руб./тн."], name="Сумма цены, руб./тн.", offsetgroup=1, secondary_y=True)
        fig.update_layout(
            barmode="group",
            title="Диаграмма по видам труб по регионам",
            xaxis_title="Регион"
        )
        fig.update_yaxes(title_text="Вес, тн.", secondary_y=False)
        fig.update_yaxes(title_text="Цена (сумма), руб./тн.", secondary_y=True)
        return dcc.Graph(figure=fig)
