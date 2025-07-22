from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
# Добавляю импорты страниц
from pages.main_page import main_page_layout
from pages.regions_page import regions_page_layout, register_regions_callbacks

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
        # default: главная страница
        return main_page_layout()

    # Регистрирую callbacks для regions_page
    register_regions_callbacks(app)

    return app
