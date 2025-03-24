import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State, ALL
import re
import base64
from io import BytesIO

# Cargar datos desde el archivo corregido
excel_path = "FH_areas_interes_final_corregido.xlsx"
df_original = pd.read_excel(excel_path)
df_original["Link"] = df_original["Link"].apply(lambda x: f"[🔗 Ver artículo]({x})" if pd.notna(x) else "")

# Inicializar la app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Traducciones
txt = {
    "es": {
        "titulo": "Artículos de la ",
        "filtrar": "📂 Filtrar por Categoría:",
        "articulos_desde": "📅 Artículos desde",
        "total": "📄 Total: {} artículos",
        "grafico_categorias": "📊 Artículos por Categoría",
        "grafico_evolucion": "📈 Evolución de {}",
    },
    "en": {
        "titulo": "Articles from ",
        "filtrar": "📂 Filter by Category:",
        "articulos_desde": "📅 Articles from",
        "total": "📄 Total: {} articles",
        "grafico_categorias": "📊 Articles by Category",
        "grafico_evolucion": "📈 Evolution of {}",
    }
}

# Layout
app.layout = dbc.Container(fluid=True, className="p-0", children=[

    dbc.Row([
        dbc.Col(html.Img(src="/assets/cover_ingles.png", style={"width": "100%", "display": "block"}), width=12)
    ], className="mb-3 g-0"),

    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id="idioma-selector",
                options=[
                    {"label": html.Span(["🇪🇸 Español"], style={"margin-right": "10px"}), "value": "es"},
                    {"label": html.Span(["🇬🇧 English"]), "value": "en"}
                ],
                value="es",
                inline=True,
                labelStyle={"margin-right": "0 15px"},
                inputStyle={"marginRight": "5px"},
                className="text-center"
            ),
            dcc.Store(id="categorias-seleccionadas", data=[])
        ], width=12, className="text-end pe-4")
    ]),

    dbc.Row([
        dbc.Col(html.H4(id="titulo-cabecera", style={"paddingLeft": "20px"}), width=8),
        dbc.Col(html.Div([
            html.Small(id="rango-fechas", className="text-muted d-block"),
            html.Small(id="total-articulos", className="text-muted"),
        ], className="text-end", style={"paddingRight": "20px"}), width=4)
    ], className="mb-3", align="center"),

    html.H6(id="label-filtrar", className="text-center mt-2 text-secondary"),

    dbc.Row([
        dbc.Col(html.Div(id="botones-categorias", className="d-flex flex-wrap justify-content-center gap-1"), width=12)
    ], className="mb-2"),

    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id="articulos-table",
            columns=[
                {"name": "Año - Volumen - Número", "id": "Año - Volumen - Número"},
                {"name": "Título", "id": "Título"},
                {"name": "Categoría", "id": "categoria_traducida"},
                {"name": "Link", "id": "Link", "presentation": "markdown"},
            ],
            style_table={"overflowX": "auto", "width": "100%"},
            style_cell={"textAlign": "left", "padding": "4px", "whiteSpace": "normal", "fontSize": "12px"},
            style_header={"backgroundColor": "#86dade", "color": "black", "fontWeight": "bold"},
            page_size=10,
            markdown_options={"link_target": "_blank"}
        ), width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="categoria-chart", clickData=None), width=12)
    ])
])

@app.callback(
    Output("categorias-seleccionadas", "data"),
    Output("titulo-cabecera", "children"),
    Output("rango-fechas", "children"),
    Output("total-articulos", "children"),
    Output("label-filtrar", "children"),
    Output("botones-categorias", "children"),
    Output("articulos-table", "data"),
    Output("categoria-chart", "figure"),
    Input("idioma-selector", "value"),
    Input("categoria-chart", "clickData"),
    Input({"type": "category-button", "index": ALL}, "n_clicks"),
    State({"type": "category-button", "index": ALL}, "id"),
    State("categorias-seleccionadas", "data")
)
def actualizar_dashboard(idioma, clickData, btn_clicks, button_ids, categorias_seleccionadas):
    df = df_original[df_original["Idioma"] == idioma].copy()
    col_categoria = "categoria" if idioma == "es" else "category"
    df.rename(columns={col_categoria: "categoria_traducida"}, inplace=True)

    categorias = sorted(df["categoria_traducida"].dropna().unique())

    selected = categorias_seleccionadas.copy()

    if btn_clicks and button_ids:
        for i, btn in enumerate(button_ids):
            if btn_clicks[i] and btn_clicks[i] % 2 != 0:
                cat = btn["index"]
                if cat in selected:
                    selected.remove(cat)
                else:
                    selected.append(cat)

    if clickData and "points" in clickData:
        clicked = clickData["points"][0]["y"]
        if clicked in selected:
            selected.remove(clicked)
        else:
            selected.append(clicked)

    botones = []
    for cat in categorias:
        seleccionado = cat in selected
        botones.append(
            dbc.Button(
                cat,
                id={"type": "category-button", "index": cat},
                title=cat,
                color="primary" if seleccionado else "secondary",
                outline=not seleccionado,
                className="m-1 px-2 py-1 btn-sm text-truncate",
                style={"fontSize": "11px", "minWidth": "90px", "maxWidth": "140px"}
            )
        )

    df_filtrado = df if not selected else df[df["categoria_traducida"].isin(selected)]

    min_year = df["Año - Volumen - Número"].str[:4].astype(int).min()
    max_year = df["Año - Volumen - Número"].str[:4].astype(int).max()
    rango = f"{txt[idioma]['articulos_desde']} {min_year} - {max_year}"
    total = txt[idioma]["total"].format(len(df))

    if len(selected) == 1:
        counts = df_filtrado["Año - Volumen - Número"].value_counts().reset_index()
        counts.columns = ["Número", "Artículos"]
        fig = px.line(counts.sort_values(by="Número"), x="Número", y="Artículos",
                      title=txt[idioma]["grafico_evolucion"].format(selected[0]), markers=True,
                      template="plotly_white",
                      color_discrete_sequence=["#cc007c"])
    else:
        counts = df["categoria_traducida"].value_counts().reset_index()
        counts.columns = ["Categoría", "Artículos"]
        fig = px.bar(counts, x="Artículos", y="Categoría",
                     orientation="h",
                     color="Artículos",
                     title=txt[idioma]["grafico_categorias"],
                     template="plotly_white",
                     color_continuous_scale=["#ffffff", "#cc007c"])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=700)

    return selected, html.Span([
        "📚 " + txt[idioma]["titulo"],
        html.A("Revista Farmacia Hospitalaria", href="https://www.revistafarmaciahospitalaria.es/",
               target="_blank", className="text-primary fw-bold text-decoration-none")
    ]), rango, total, txt[idioma]["filtrar"], botones, df_filtrado.to_dict("records"), fig

if __name__ == '__main__':
    app.run_server(debug=True)
