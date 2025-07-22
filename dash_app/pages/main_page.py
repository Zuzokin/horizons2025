from dash import dcc, html
import plotly.express as px
import pandas as pd

def main_page_layout():
    df_bar = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas"],
        "Amount": [4, 2, 3]
    })
    fig = px.bar(df_bar, x="Fruit", y="Amount", title="Простой бар-чарт")
    return html.Div([
        html.H2("Главная страница: Bar Chart"),
        dcc.Graph(figure=fig),
    ], style={"padding": "20px"}) 