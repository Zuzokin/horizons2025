from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
# Добавляю импорты страниц
from dash_app.pages.main_page import main_page_layout
from dash_app.pages.regions_page import regions_page_layout, register_regions_callbacks
from dash_app.pages.pipe_type_page import pipe_type_page_layout, register_pipe_type_callbacks
from dash_app.pages.industry_cut_page import industry_cut_page_layout, register_industry_cut_callbacks

def create_dash_app():
    app = Dash(
        __name__,
        requests_pathname_prefix="/dash/",
        suppress_callback_exceptions=True
    )

    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Nav([
            dcc.Link("Главная (Bar Chart)", href="/dash/"),
            " | ",
            dcc.Link("Диаграмма регионов", href="/dash/regions"),
            " | ",
            dcc.Link("Диаграмма по видам труб", href="/dash/pipe-type"),
            " | ",
            dcc.Link("Отраслевой срез", href="/dash/industry-cut"),
        ], style={"margin": "20px"}),
        html.Div(id="page-content")
    ])

    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def render_page(pathname):
        if pathname == "/dash/regions":
            return regions_page_layout()
        elif pathname == "/dash/pipe-type":
            return pipe_type_page_layout()
        elif pathname == "/dash/industry-cut":
            return industry_cut_page_layout()
        # default: главная страница
        return main_page_layout()

    # Регистрирую callbacks
    register_regions_callbacks(app)
    register_pipe_type_callbacks(app)
    register_industry_cut_callbacks(app)

    return app
