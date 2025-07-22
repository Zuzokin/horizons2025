from dash import dcc, html, Input, Output
import pandas as pd
import os
import plotly.graph_objs as go

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
            html.Label("Период с", style={"marginLeft": "20px"}),
            dcc.Input(id="PERIOD_IN", type="text", placeholder="YYYY-MM-DD", style={"width": "120px"}),
            html.Label("по", style={"marginLeft": "5px"}),
            dcc.Input(id="PERIOD_OUT", type="text", placeholder="YYYY-MM-DD", style={"width": "120px"}),
            html.Button("Обновить диаграмму", id="BT_REFRESH", n_clicks=0, style={"marginLeft": "20px"}),
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
        [Input("BT_REFRESH", "n_clicks")],
        [Input("CB_PIPE_TYPE_M1", "value"),
         Input("PERIOD_IN", "value"),
         Input("PERIOD_OUT", "value"),
         Input("CB_PLANTS", "value")]
    )
    def update_pipe_type_graph(n_clicks, pipe_type, period_in, period_out, plant):
        if not pipe_type:
            return html.Div("Пожалуйста, выберите вид труб (обязательное поле)", style={"color": "red"})
        dff = df_bd[df_bd["Вид труб-М1"] == pipe_type]
        if plant:
            dff = dff[dff["Завод"] == plant]
        if period_in:
            try:
                period_in_dt = pd.to_datetime(period_in)
                dff = dff[dff["Дата фактической отгрузки"] >= period_in_dt]
            except Exception:
                pass
        if period_out:
            try:
                period_out_dt = pd.to_datetime(period_out)
                dff = dff[dff["Дата фактической отгрузки"] <= period_out_dt]
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
        fig.update_layout(barmode="group", title="Диаграмма по видам труб по регионам", xaxis_title="Регион", yaxis_title="Значение")
        return dcc.Graph(figure=fig) 