from dash import dcc, html, Input, Output, State, callback_context
import dash
import plotly.express as px
import pandas as pd
import requests
import base64
import io

def main_page_layout():
    return html.Div([
        html.Hr(),
        html.Label("Загрузить Excel-файл (.xlsx или .xls)"),
        dcc.Upload(
            id='upload-data',
            children=html.Button('Выбрать файл'),
            multiple=False,
            style={"marginRight": "16px"}
        ),
        html.Button('Загрузить', id='upload-btn', n_clicks=0, style={"marginLeft": "8px"}),
        html.Div(id='upload-status', style={"marginTop": "15px", "fontWeight": "bold", "color": "#0a376d"}),
    ], style={"padding": "20px"})


def register_main_callbacks(app, fastapi_url="http://127.0.0.1:8000"):  # fastapi_url можно указать свой

    @app.callback(
        Output('upload-status', 'children'),
        Input('upload-btn', 'n_clicks'),
        State('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def upload_file(n_clicks, contents, filename):
        if not contents:
            return "Сначала выберите файл!"

        # Получаем файл из base64
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        files = {
            'file': (filename, io.BytesIO(decoded), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }

        # Шлем запрос на FastAPI
        try:
            r = requests.post(f"{fastapi_url}/uploads/excel", files=files)
            if r.status_code == 201:
                data = r.json()
                return f"✅ {data['message']} (Загружено: {data['rows_loaded']}, Ошибок: {data['rows_error']})"
            else:
                return f"❌ Ошибка: {r.text}"
        except Exception as e:
            return f"❌ Не удалось отправить файл: {str(e)}"
