from dash import Dash, dcc, html, Input, Output
# Импорт страниц — как у вас
from dash_app.pages.main_page import main_page_layout, register_main_callbacks
from dash_app.pages.predict_page import predict_page_layout, register_predict_callbacks
from dash_app.pages.regions_page import regions_page_layout, register_regions_callbacks
from dash_app.pages.pipe_type_page import pipe_type_page_layout, register_pipe_type_callbacks
from dash_app.pages.industry_cut_page import industry_cut_page_layout, register_industry_cut_callbacks
from dash_app.pages.geographical_cut_page import geographical_cut_page_layout, register_geographical_cut_callbacks
from dash_app.pages.dynamics_page import dynamics_page_layout, register_dynamics_callbacks
from dash_app.pages.product_page import product_page_layout, register_product_callbacks
from dash_app.pages.consignee_page import consignee_page_layout, register_consignee_callbacks
from dash_app.pages.material_page import material_page_layout, register_material_callbacks

def create_dash_app():
    app = Dash(
        __name__,
        requests_pathname_prefix="/dash/",
        suppress_callback_exceptions=True
    )

    NAV_LINKS = [
        {"label": "Диаграмма регионов", "href": "/dash/regions"},
        {"label": "Диаграмма по видам труб", "href": "/dash/pipe-type"},
        {"label": "Отраслевой срез", "href": "/dash/industry-cut"},
        {"label": "Географический срез", "href": "/dash/geographical-cut"},
        {"label": "Динамика", "href": "/dash/dynamics"},
        {"label": "Продукт", "href": "/dash/product"},
        {"label": "Грузополучатель", "href": "/dash/consignee"},
        {"label": "Материал", "href": "/dash/material"},
        {"label": "Предсказание", "href": "/dash/predict"},
    ]

    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),

        html.Nav([
            # Логотип — это ссылка
            dcc.Link(
                "ТМК Sales Analytics",
                href="/dash/",
                style={
                    "fontWeight": "bold",
                    "fontSize": "2.3rem",
                    "color": "#123877",
                    "letterSpacing": "0.04em",
                    "marginRight": "38px",
                    "fontFamily": "Segoe UI, Arial",
                    "textDecoration": "none",
                    "transition": "color 0.18s"
                }
            ),

            # Ссылки
            html.Div([
                dcc.Link(
                    link["label"],
                    href=link["href"],
                    className="nav-link",
                    id={"type": "nav-link", "index": link["href"]},
                    style={
                        "fontSize": "1.18rem",
                        "fontWeight": "600",
                        "padding": "10px 22px",
                        "borderRadius": "9px",
                        "transition": "background 0.2s, color 0.2s, box-shadow 0.18s",
                        "textDecoration": "none",
                        "color": "#274b89",
                        "marginRight": "2px",
                        "letterSpacing": "0.02em"
                    }
                )
                for link in NAV_LINKS
            ], style={
                "display": "flex",
                "gap": "7px",
                "alignItems": "center"
            }),
        ], style={
            "display": "flex",
            "justifyContent": "flex-start",
            "alignItems": "center",
            "padding": "24px 48px 22px 48px",
            "backgroundColor": "#f5f7fa",
            "boxShadow": "0 2px 8px 0 #e1e6f0",
            "marginBottom": "36px"
        }),

        html.Div(id="page-content", style={"margin": "0 38px"})
    ])

    # Стили для ссылок (через Dash clientsidedash)
    app.clientside_callback(
        """
        function(pathname) {
            setTimeout(() => {
                let links = document.querySelectorAll('.nav-link');
                links.forEach(link => {
                    if(link.getAttribute('href') === pathname) {
                        link.style.fontWeight = "bold";
                        link.style.textDecoration = "underline";
                        link.style.background = "#e4eafd";
                        link.style.borderRadius = "7px";
                        link.style.color = "#184b8f";
                        link.style.boxShadow = "0 2px 8px #e3e7fa inset";
                        link.style.padding = "8px 15px";
                    } else {
                        link.style.fontWeight = "normal";
                        link.style.textDecoration = "none";
                        link.style.background = "";
                        link.style.borderRadius = "";
                        link.style.color = "#375a8c";
                        link.style.boxShadow = "";
                        link.style.padding = "8px 15px";
                    }
                });
            }, 10);
            return '';
        }
        """,
        Output('page-content', 'data-dummy'),
        Input('url', 'pathname')
    )

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
        elif pathname == "/dash/geographical-cut":
            return geographical_cut_page_layout()
        elif pathname == "/dash/dynamics":
            return dynamics_page_layout()
        elif pathname == "/dash/product":
            return product_page_layout()
        elif pathname == "/dash/consignee":
            return consignee_page_layout()
        elif pathname == "/dash/material":
            return material_page_layout()
        elif pathname == "/dash/predict":
            return predict_page_layout()
        # default
        return main_page_layout()

    # Регистрация callbacks
    register_regions_callbacks(app)
    register_pipe_type_callbacks(app)
    register_industry_cut_callbacks(app)
    register_geographical_cut_callbacks(app)
    register_dynamics_callbacks(app)
    register_product_callbacks(app)
    register_consignee_callbacks(app)
    register_material_callbacks(app)
    register_predict_callbacks(app)
    register_main_callbacks(app)

    return app
