from dash import dcc, html, Input, Output
import pandas as pd
import os
import plotly.graph_objs as go

def regions_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Год отгрузки"] = pd.to_numeric(df_bd["Год отгрузки"], errors="coerce")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    df_bd["Стоимость ТД без НДС, руб."] = pd.to_numeric(df_bd["Стоимость ТД без НДС, руб."], errors="coerce")
    unique_plants = df_bd["Завод"].dropna().unique()
    years = sorted(df_bd["Год отгрузки"].dropna().unique())
    return html.Div([
        html.H2("Диаграмма регионов"),
        html.Div([
            html.Label("Завод*"),
            dcc.Dropdown(
                id="CB_PLANTS",
                options=[{"label": p, "value": p} for p in unique_plants],
                placeholder="Выберите завод",
                style={"width": "300px"}
            ),
            html.Label("Год", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="YEAR",
                options=[{"label": str(y), "value": y} for y in years],
                placeholder="Год",
                style={"width": "120px", "display": "inline-block", "marginLeft": "5px"}
            ),
            html.Label("Период с", style={"marginLeft": "20px"}),
            dcc.Input(id="PERIOD_IN", type="text", placeholder="YYYY-MM-DD", style={"width": "120px"}),
            html.Label("по", style={"marginLeft": "5px"}),
            dcc.Input(id="PERIOD_OUT", type="text", placeholder="YYYY-MM-DD", style={"width": "120px"}),
            html.Button("Обновить диаграмму", id="BT_REFRESH", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px"}),
        html.Div(id="regions-graph-container")
    ], style={"padding": "20px"})

def register_regions_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Год отгрузки"] = pd.to_numeric(df_bd["Год отгрузки"], errors="coerce")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    df_bd["Стоимость ТД без НДС, руб."] = pd.to_numeric(df_bd["Стоимость ТД без НДС, руб."], errors="coerce")
    @app.callback(
        Output("regions-graph-container", "children"),
        [Input("BT_REFRESH", "n_clicks")],
        [Input("CB_PLANTS", "value"),
         Input("YEAR", "value"),
         Input("PERIOD_IN", "value"),
         Input("PERIOD_OUT", "value")]
    )
    def update_regions_graph(n_clicks, plant, year, period_in, period_out):
        if not plant:
            return html.Div("Пожалуйста, выберите завод (обязательное поле)", style={"color": "red"})
        dff = df_bd[df_bd["Завод"] == plant]
        if year:
            dff = dff[dff["Год отгрузки"] == year]
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
        fig.update_layout(barmode="group", title="Диаграмма по регионам", xaxis_title="Регион", yaxis_title="Значение")
        return dcc.Graph(figure=fig) 