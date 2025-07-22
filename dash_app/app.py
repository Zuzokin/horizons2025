from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

def create_dash_app():
    app = Dash(
        __name__,
        requests_pathname_prefix="/dash/",
        suppress_callback_exceptions=True
    )

    # Навигация между страницами
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Nav([
            dcc.Link("Главная (Bar Chart)", href="/dash/"),
            " | ",
            dcc.Link("Круговая диаграмма", href="/dash/page1"),
            " | ",
            dcc.Link("Линейный график", href="/dash/page2"),
        ], style={"margin": "20px"}),
        html.Div(id="page-content")
    ])

    # Данные для трёх графиков
    df_bar = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas"],
        "Amount": [4, 2, 3]
    })
    df_pie = pd.DataFrame({
        "Category": ["A", "B", "C"],
        "Value": [10, 20, 30]
    })
    df_line = px.data.gapminder().query("country=='Canada'")

    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def render_page(pathname):
        if pathname == "/dash/page1":
            fig = px.pie(df_pie, names="Category", values="Value", title="Круговая диаграмма")
            return html.Div([
                html.H2("Страница 1: Pie Chart"),
                dcc.Graph(figure=fig),
            ], style={"padding": "20px"})

        elif pathname == "/dash/page2":
            fig = px.line(df_line, x="year", y="lifeExp", title="Life Expectancy in Canada")
            return html.Div([
                html.H2("Страница 2: Line Chart"),
                dcc.Graph(figure=fig),
            ], style={"padding": "20px"})

        # default: главная страница
        fig = px.bar(df_bar, x="Fruit", y="Amount", title="Простой бар-чарт")
        return html.Div([
            html.H2("Главная страница: Bar Chart"),
            dcc.Graph(figure=fig),
        ], style={"padding": "20px"})

    return app
