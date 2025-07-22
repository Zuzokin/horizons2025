from dash import dcc, html, Input, Output
import pandas as pd
import os
import plotly.express as px
from dash import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def geographical_cut_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")
    
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
        html.Div(id="geographical-cut-graph-container"),
        html.Hr(),
        html.H3("Детализация по регионам"),
        html.Div(id="geographical-cut-table-container")
    ], style={"padding": "20px"})

def register_geographical_cut_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(df_bd["Цена ТД без НДС, руб./тн."], errors="coerce")

    @app.callback(
        [Output("geographical-cut-graph-container", "children"),
         Output("geographical-cut-table-container", "children")],
        Input("BT_REFRESH_GEO", "n_clicks"),
        Input("geo_delivery_region_ru", "value")
    )
    def update_geographical_cut_graph(n_clicks, regions):
        if n_clicks == 0:
            return html.Div("Выберите регионы (или оставьте пустым для вывода по всем) и нажмите 'Обновить диаграмму'", style={"color": "grey"}), None
            
        dff = df_bd.copy()

        if regions:
            dff = dff[dff["Регион ПОСТАВКИ РФ"].isin(regions)]

        if dff.empty:
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"}), None

        # Group by region and sum weight and price
        grouped = dff.groupby("Регион ПОСТАВКИ РФ").agg({
            "Вес, тн.": "sum",
            "Цена ТД без НДС, руб./тн.": "sum"
        }).reset_index()

        if grouped.empty:
            return html.Div("Нет данных для построения диаграммы после агрегации.", style={"color": "orange"}), None

        # График как в regions_page: оба bar, secondary_y для цены
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=grouped["Регион ПОСТАВКИ РФ"],
                y=grouped["Вес, тн."],
                name="Вес, тн.",
                offsetgroup=0
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(
                x=grouped["Регион ПОСТАВКИ РФ"],
                y=grouped["Цена ТД без НДС, руб./тн."],
                name="Сумма цены, руб./тн.",
                offsetgroup=1
            ),
            secondary_y=True
        )
        fig.update_layout(
            barmode="group",
            title="Диаграмма по регионам",
            xaxis_title="Регион"
        )
        fig.update_yaxes(title_text="Вес, тн.", secondary_y=False)
        fig.update_yaxes(title_text="Цена (сумма), руб./тн.", secondary_y=True)

        table = dash_table.DataTable(
            columns=[
                {"name": "Регион ПОСТАВКИ РФ", "id": "Регион ПОСТАВКИ РФ"},
                {"name": "Вес, тн.", "id": "Вес, тн."},
                {"name": "Цена ТД без НДС, руб./тн.", "id": "Цена ТД без НДС, руб./тн."}
            ],
            data=grouped.to_dict('records'),
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"fontWeight": "bold"}
        )
        return dcc.Graph(figure=fig), table 