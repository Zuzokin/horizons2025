from dash import dcc, html, Input, Output
import pandas as pd
import os
import plotly.express as px

def geographical_cut_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    
    unique_regions = df_bd["Регион ПОСТАВКИ РФ"].dropna().unique()
    
    return html.Div([
        html.H2("Географический срез"),
        html.Div([
            html.Label("Регион ПОСТАВКИ РФ"),
            dcc.Dropdown(
                id="geo_delivery_region_ru",
                options=[{"label": r, "value": r} for r in unique_regions],
                placeholder="Выберите один или несколько регионов (необязательно)",
                multi=True,
                style={"width": "400px"}
            ),
            html.Button("Обновить диаграмму", id="BT_REFRESH_GEO", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px"}),
        html.Div(id="geographical-cut-graph-container")
    ], style={"padding": "20px"})

def register_geographical_cut_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")

    @app.callback(
        Output("geographical-cut-graph-container", "children"),
        Input("BT_REFRESH_GEO", "n_clicks"),
        Input("geo_delivery_region_ru", "value")
    )
    def update_geographical_cut_graph(n_clicks, regions):
        if n_clicks == 0:
            return html.Div("Выберите регионы (или оставьте пустым для топ-5 по всем) и нажмите 'Обновить диаграмму'", style={"color": "grey"})
            
        dff = df_bd.copy()

        if regions:
            dff = dff[dff["Регион ПОСТАВКИ РФ"].isin(regions)]

        if dff.empty:
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"})

        # Group by region and sum weight, then get top 5
        top_5_regions = dff.groupby("Регион ПОСТАВКИ РФ")["Вес, тн."].sum().nlargest(5).reset_index()

        if top_5_regions.empty:
            return html.Div("Нет данных для построения диаграммы после агрегации.", style={"color": "orange"})

        fig = px.bar(top_5_regions, 
                     x="Регион ПОСТАВКИ РФ", 
                     y="Вес, тн.", 
                     title="Топ-5 регионов по объему отгрузки")
        
        return dcc.Graph(figure=fig) 