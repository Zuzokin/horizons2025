# Файл создал Мазанов Кирилл

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash import html, dcc, dash_table, Input, Output, State
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
import os

# ======= Загрузка данных (будет использоваться при каждом callback) =======
CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/ed459fb8-e8f5-46c8-aaa6-6362bb859dee_Отгрузка ТМК.csv')
df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")

pipe_types = [{"label": v, "value": v} for v in sorted(df_bd["Вид труб-М1"].dropna().unique())]
regions = [{"label": v, "value": v} for v in sorted(df_bd["Регион ПОСТАВКИ РФ"].dropna().unique())]

# ======= Описания моделей =======
MODEL_OPTIONS = [
    {
        "label": "Holt–Winters (сезонное экспоненциальное сглаживание)",
        "value": "holtwinters",
        "description": "Работает хорошо на регулярных рядах с трендом и/или сезонностью. Использует сглаживание уровня, тренда и сезонного компонента. Хорош для недельной/месячной агрегации."
    },
    {
        "label": "ARIMA (классическая модель временных рядов)",
        "value": "arima",
        "description": "Подходит для стационарных или преобразованных к стационарности рядов. Ловит автокорреляцию, иногда хуже справляется с выраженной сезонностью. Лучше на длинных, равномерных рядах."
    }
]

# ======= Вёрстка страницы =======
def predict_page_layout():
    return html.Div([
        html.H2("Прогнозирование"),
        html.Div([
            html.Label("Вид труб-М1"),
            dcc.Dropdown(id="PREDICT_PIPE_TYPE_M1", options=pipe_types, placeholder="Выберите вид труб", style={"width": "230px"}),
            html.Label("Регион", style={"marginLeft": "16px"}),
            dcc.Dropdown(id="PREDICT_REGION", options=regions, placeholder="Регион (опционально)", style={"width": "230px"}),
            html.Label("Период прогноза", style={"marginLeft": "16px"}),
            dcc.DatePickerRange(
                id="PREDICT_DATE_RANGE",
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format="YYYY-MM-DD",
            ),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "16px", "flexWrap": "wrap"}),
        html.Div([
            html.Label("Модель для прогноза", style={"marginRight": "8px"}),
            dcc.Dropdown(
                id="PREDICT_MODEL",
                options=[{"label": m["label"], "value": m["value"]} for m in MODEL_OPTIONS],
                value="holtwinters",
                style={"width": "380px", "marginRight": "18px"},
            ),
            html.Div(id="PREDICT_MODEL_HINT", style={"fontSize": "13px", "fontStyle": "italic", "color": "#888"}),
            html.Button("Построить прогноз", id="PREDICT_BUTTON", n_clicks=0, style={"marginLeft": "30px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}),
        html.Div(id="predict-graph-container"),
        html.Hr(),
        html.H3("Детализация прогноза"),
        html.Div(id="predict-table-container")
    ], style={"padding": "24px"})


# ======= Callback (логика) =======
def register_predict_callbacks(app):
    @app.callback(
        Output("PREDICT_MODEL_HINT", "children"),
        Input("PREDICT_MODEL", "value"),
    )
    def update_model_hint(model_val):
        hint = next((m["description"] for m in MODEL_OPTIONS if m["value"] == model_val), "")
        return hint

    @app.callback(
        [Output("predict-graph-container", "children"),
         Output("predict-table-container", "children")],
        Input("PREDICT_BUTTON", "n_clicks"),
        [
            State("PREDICT_PIPE_TYPE_M1", "value"),
            State("PREDICT_REGION", "value"),
            State("PREDICT_DATE_RANGE", "start_date"),
            State("PREDICT_DATE_RANGE", "end_date"),
            State("PREDICT_MODEL", "value"),
        ]
    )
    def update_predict_report(n_clicks, pipe_type, region, pred_start, pred_end, model_val):
        dff = df_bd.copy()
        # Фильтрация по виду трубы и региону
        if pipe_type:
            dff = dff[dff["Вид труб-М1"] == pipe_type]
        if region:
            dff = dff[dff["Регион ПОСТАВКИ РФ"] == region]
        # Проверка периода прогноза
        if not pred_start or not pred_end:
            return html.Div("Выберите период прогноза", style={"color": "orange"}), None
        pred_start_dt = pd.to_datetime(pred_start)
        pred_end_dt = pd.to_datetime(pred_end)
        if pred_start_dt > pred_end_dt:
            return html.Div("Некорректный диапазон дат", style={"color": "orange"}), None

        # ---- Автоматический подбор обучающего окна ----
        pred_days = (pred_end_dt - pred_start_dt).days + 1
        min_lookback = max(28, pred_days * 3)
        max_lookback = 365  # ограничим 1 годом
        lookback_days = min(max_lookback, max(min_lookback, pred_days * 3))
        train_end = pred_start_dt - pd.Timedelta(days=1)
        train_start = train_end - pd.Timedelta(days=lookback_days-1)
        train_df = dff[(dff["Дата фактической отгрузки"] >= train_start) & (dff["Дата фактической отгрузки"] <= train_end)]
        if train_df.empty or (train_df["Вес, тн."].sum() == 0):
            return html.Div("Нет данных для обучения за выбранный период. Попробуйте другой фильтр или период.", style={"color": "orange"}), None

        # ---- Агрегация по дням ----
        series = train_df.groupby("Дата фактической отгрузки")["Вес, тн."].sum().asfreq("D").fillna(0.0)
        use_seasonal = len(series) >= 14
        horizon = pred_days
        pred_dates = pd.date_range(pred_start_dt, pred_end_dt)

        # ---- Holt–Winters ----
        if model_val == "holtwinters":
            if use_seasonal:
                model = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=7, initialization_method="estimated")
            else:
                model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
            fit = model.fit(optimized=True)
            forecast = fit.forecast(horizon).clip(lower=0)
            forecast.index = pred_dates

        # ---- ARIMA ----
        elif model_val == "arima":
            try:
                order = (1, 1, 0) if len(series) < 60 else (2, 1, 2)
                fit = ARIMA(series, order=order).fit()
                forecast = fit.forecast(horizon)
                forecast[forecast < 0] = 0
                forecast.index = pred_dates
            except Exception as e:
                return html.Div(f"Ошибка ARIMA: {e}", style={"color": "red"}), None

        else:
            return html.Div("Выбранная модель недоступна.", style={"color": "red"}), None

        # ---- Собираем график ----
        trace_fact = go.Scatter(x=series.index, y=series.values, name="Факт (train)", mode="lines+markers")
        trace_pred = go.Scatter(x=forecast.index, y=forecast.values, name="Прогноз", mode="lines+markers")
        fig = go.Figure([trace_fact, trace_pred])
        fig.update_layout(title="Прогноз объёма отгрузок",
                          xaxis_title="Дата", yaxis_title="Вес, тн.",
                          legend_title="Линия", template="plotly_white")

        # ---- Таблица прогноза ----
        forecast_df = pd.DataFrame({"Дата": forecast.index.strftime('%Y-%m-%d'), "Прогноз, тн.": forecast.values})
        table = dash_table.DataTable(
            columns=[{"name": "Дата", "id": "Дата"}, {"name": "Прогноз, тн.", "id": "Прогноз, тн."}],
            data=forecast_df.to_dict('records'),
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"fontWeight": "bold"}
        )

        return dcc.Graph(figure=fig), table
