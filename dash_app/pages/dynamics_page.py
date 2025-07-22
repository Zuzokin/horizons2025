from dash import dcc, html, Input, Output, State
import pandas as pd
import os
import plotly.express as px

def dynamics_page_layout():
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    unique_industries = df_bd["Отрасль Основного Потребителя"].dropna().unique()
    
    return html.Div([
        html.H2("Динамика отгрузок"),
        html.Div([
            html.Label("Отрасль Основного Потребителя"),
            dcc.Dropdown(
                id="dynamics_end_consumer_industry",
                options=[{"label": i, "value": i} for i in unique_industries],
                placeholder="Выберите отрасль",
                style={"width": "400px"}
            ),
            html.Label("Дата отгрузки", style={"marginLeft": "20px"}),
            dcc.DatePickerRange(
                id='dynamics-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить диаграмму", id="BT_REFRESH_DYNAMICS", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "20px"}),
        html.Div(id="dynamics-graph-container")
    ], style={"padding": "20px"})

def register_dynamics_callbacks(app):
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv')
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(df_bd["Дата фактической отгрузки"], errors="coerce")
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")

    @app.callback(
        Output("dynamics-graph-container", "children"),
        Input("BT_REFRESH_DYNAMICS", "n_clicks"),
        [State("dynamics_end_consumer_industry", "value"),
         State("dynamics-date-picker-range", "start_date"),
         State("dynamics-date-picker-range", "end_date")]
    )
    def update_dynamics_graph(n_clicks, industry, start_date, end_date):
        if n_clicks == 0:
            return html.Div("Настройте фильтры и нажмите 'Обновить диаграмму'", style={"color": "grey"})

        dff = df_bd.copy()
        
        title = 'Динамика отгрузок'
        if industry:
            dff = dff[dff["Отрасль Основного Потребителя"] == industry]
            title += f' для отрасли "{industry}"'

        if start_date:
            try:
                period_in_dt = pd.to_datetime(start_date)
                dff = dff[dff["Дата фактической отгрузки"] >= period_in_dt]
            except Exception:
                pass # Ignore invalid date format
        
        if end_date:
            try:
                period_out_dt = pd.to_datetime(end_date)
                dff = dff[dff["Дата фактической отгрузки"] <= period_out_dt]
            except Exception:
                pass # Ignore invalid date format

        if dff.empty:
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"})

        # Group by date and sum weight
        dff = dff.sort_values(by="Дата фактической отгрузки")
        dynamics_data = dff.groupby(dff["Дата фактической отгрузки"].dt.to_period("D"))["Вес, тн."].sum().reset_index()
        dynamics_data["Дата фактической отгрузки"] = dynamics_data["Дата фактической отгрузки"].dt.to_timestamp()


        if dynamics_data.empty:
            return html.Div("Нет данных для построения диаграммы после агрегации.", style={"color": "orange"})

        fig = px.line(dynamics_data, 
                      x="Дата фактической отгрузки", 
                      y="Вес, тн.", 
                      title=title)
        
        return dcc.Graph(figure=fig) 