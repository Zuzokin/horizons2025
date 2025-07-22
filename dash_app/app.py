from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd


def create_dash_app():
    app = Dash(__name__, requests_pathname_prefix="/dash/")

    # Пример данных
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas"],
        "Amount": [4, 2, 3]
    })

    fig = px.bar(df, x="Fruit", y="Amount", title="Простой график")

    app.layout = html.Div([
        html.H1("Минимальный Dash в FastAPI"),
        dcc.Graph(figure=fig),
        html.P("Теперь работает без ошибок!")
    ])

    return app