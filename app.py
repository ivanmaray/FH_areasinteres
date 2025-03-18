import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Cargar los datos
df = pd.read_excel("FH_areas_interes.xlsx")

# Inicializar la aplicación Dash con Bootstrap para mejor diseño
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # Necesario para despliegue

# Obtener categorías únicas
categorias = df["Categoría"].unique()

# Estilos para mejorar visualización
BUTTON_STYLE = {
    "margin": "5px", "padding": "5px 10px", "border-radius": "10px",
    "cursor": "pointer", "border": "1px solid #007bff", "background-color": "white",
    "color": "#007bff", "font-size": "12px", "font-weight": "bold"
}
BUTTON_ACTIVE_STYLE = BUTTON_STYLE.copy()
BUTTON_ACTIVE_STYLE.update({"background-color": "#007bff", "color": "white"})

# Layout de la app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H4(["📚 ", html.A("Artículos de la Revista Farmacia Hospitalaria", href="https://www.revistafarmaciahospitalaria.es/", target="_blank", style={"color": "#007bff", "text-decoration": "none"})]), width=8),
        dbc.Col(html.P(id="total-articulos", style={"text-align": "right", "font-size": "14px", "color": "gray"}), width=4),
    ], className="mb-3"),

    # Botones de filtro
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Button(cat, id=f"btn-{cat}", n_clicks=0, style=BUTTON_STYLE) for cat in categorias
            ], style={"display": "flex", "flex-wrap": "wrap"})
        ])
    ], className="mb-3"),

    # Gráfico de artículos por categoría
    dcc.Graph(id="categoria-chart"),

    # Tabla de artículos
    dash_table.DataTable(
        id="articulos-table",
        columns=[
            {"name": "Año - Volumen - Número", "id": "Año - Volumen - Número"},
            {"name": "Título", "id": "Título"},
            {"name": "Categoría", "id": "Categoría"},
            {"name": "Ver", "id": "Enlace", "presentation": "markdown"},
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'fontSize': '12px'},
        style_header={'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold'},
        page_size=10,
    )
], fluid=True)


# Callback para actualizar tabla y gráfico
@app.callback(
    [Output("articulos-table", "data"),
     Output("categoria-chart", "figure"),
     Output("total-articulos", "children")],
    [Input(f"btn-{cat}", "n_clicks") for cat in categorias],
    prevent_initial_call=False
)
def update_dashboard(*btn_clicks):
    selected_categories = [categorias[i] for i, clicks in enumerate(btn_clicks) if clicks % 2 != 0]
    
    # Filtrar datos
    filtered_df = df[df["Categoría"].isin(selected_categories)] if selected_categories else df

    # Construcción de tabla
    filtered_df["Enlace"] = filtered_df["Enlace"].apply(lambda x: f"[🔗 Ver artículo]({x})")

    # Construcción del gráfico
    if len(selected_categories) == 1:
        fig = px.histogram(filtered_df, x="Año - Volumen - Número", title=f"Artículos en {selected_categories[0]}", color_discrete_sequence=["#007bff"])
    else:
        fig = px.bar(filtered_df["Categoría"].value_counts().reset_index(), x="index", y="Categoría",
                     labels={"index": "Categoría", "Categoría": "Número de Artículos"},
                     title="Número de Artículos por Categoría",
                     color_discrete_sequence=["#007bff"])
    
    return filtered_df.to_dict("records"), fig, f"Total de artículos: {len(filtered_df)}"


if __name__ == "__main__":
    app.run_server(debug=True)
