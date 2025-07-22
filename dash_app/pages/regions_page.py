from dash import dcc, html, Input, Output, State
import pandas as pd
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def regions_page_layout():
    CSV_PATH = os.path.join(
        os.path.dirname(__file__),
        '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv'
    )
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Год отгрузки"] = pd.to_numeric(df_bd["Год отгрузки"], errors="coerce")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(
        df_bd["Дата фактической отгрузки"], errors="coerce"
    )
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(
        df_bd["Цена ТД без НДС, руб./тн."], errors="coerce"
    )

    unique_plants = df_bd["Завод"].dropna().unique()
    years = sorted(df_bd["Год отгрузки"].dropna().unique())

    return html.Div([
        html.H2("Диаграмма регионов"),
        html.Div([
            html.Label("Завод"),
            dcc.Dropdown(
                id="CB_PLANTS",
                options=[{"label": p, "value": p} for p in unique_plants],
                multi=True,
                style={"width": "300px"}
            ),
            html.Label("Год", style={"marginLeft": "20px"}),
            dcc.Dropdown(
                id="YEAR",
                options=[{"label": str(y), "value": y} for y in years],
                placeholder="Год",
                style={"width": "120px", "marginLeft": "5px"}
            ),
            html.Label("Период", style={"marginLeft": "20px"}),
            dcc.DatePickerRange(
                id='regions-date-picker-range',
                start_date_placeholder_text="Начало",
                end_date_placeholder_text="Конец",
                display_format='YYYY-MM-DD',
                style={"marginLeft": "5px"}
            ),
            html.Button("Обновить", id="BT_REFRESH", n_clicks=0, style={"marginLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),
        html.Div(id="regions-graph-container", style={"marginTop": "20px"})
    ], style={"padding": "20px"})


def register_regions_callbacks(app):
    CSV_PATH = os.path.join(
        os.path.dirname(__file__),
        '../../data/5cdfef22-9165-44bd-8e4e-e93346180843_Отгрузка ТМК.csv'
    )
    df_bd = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8")
    df_bd["Год отгрузки"] = pd.to_numeric(df_bd["Год отгрузки"], errors="coerce")
    df_bd["Дата фактической отгрузки"] = pd.to_datetime(
        df_bd["Дата фактической отгрузки"], errors="coerce"
    )
    df_bd["Вес, тн."] = pd.to_numeric(df_bd["Вес, тн."], errors="coerce")
    df_bd["Цена ТД без НДС, руб./тн."] = pd.to_numeric(
        df_bd["Цена ТД без НДС, руб./тн."], errors="coerce"
    )

    @app.callback(
        Output("regions-graph-container", "children"),
        Input("BT_REFRESH", "n_clicks"),
        State("CB_PLANTS", "value"),
        State("YEAR", "value"),
        State("regions-date-picker-range", "start_date"),
        State("regions-date-picker-range", "end_date"),
    )
    def update_regions_graph(n_clicks, plants, year, start_date, end_date):
        # 1) фильтрация
        dff = df_bd.copy()
        if plants:
            dff = dff[dff["Завод"].isin(plants)]
        if year:
            dff = dff[dff["Год отгрузки"] == year]
        if start_date:
            dff = dff[dff["Дата фактической отгрузки"]] >= pd.to_datetime(start_date)
        if end_date:
            dff = dff[dff["Дата фактической отгрузки"]] <= pd.to_datetime(end_date)

        if dff.empty:
            return html.Div("Нет данных по выбранным фильтрам", style={"color": "orange"})

        # 2) суммируем оба показателя
        grouped = dff.groupby("Регион Получателя").agg({
            "Вес, тн.": "sum",
            "Цена ТД без НДС, руб./тн.": "sum"
        }).reset_index()

        # 3) строим grouped bar с двумя осями
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(
                x=grouped["Регион Получателя"],
                y=grouped["Вес, тн."],
                name="Вес, тн.",
                offsetgroup=0
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(
                x=grouped["Регион Получателя"],
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

        return dcc.Graph(figure=fig)
