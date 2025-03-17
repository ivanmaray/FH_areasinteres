import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State, ALL

# Cargar los datos
df = pd.read_excel("FH_areas_interes.xlsx", sheet_name=0, engine="openpyxl")

# Obtener categorías únicas sin duplicados
df["Categoría"] = df["Categoría"].str.strip()
categorias_unicas = sorted(df["Categoría"].unique())

# Obtener rango de fechas de los artículos
min_year = df["Año - Volumen - Número"].str[:4].astype(int).min()
max_year = df["Año - Volumen - Número"].str[:4].astype(int).max()
rango_fechas = f"{min_year} - {max_year}"

# Inicializar la aplicación Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Diseño de la aplicación
app.layout = dbc.Container([
    
    # Encabezado con título y estadísticas en la esquina superior derecha
    dbc.Row([
        dbc.Col(html.H4("📚 Artículos de la Revista Farmacia Hospitalaria",
                        className="text-left text-primary"), width=8),
        dbc.Col(html.Div([
            html.Small(f"📅 Artículos desde {rango_fechas}", className="text-muted d-block"),
            html.Small(f"📄 Total: {len(df)} artículos", className="text-muted"),
        ], className="text-end"), width=4)
    ], align="center", className="mb-3"),

    # Botones de categorías compactos
    html.H6("📂 Filtrar por Categoría:", className="text-center mt-2 text-secondary"),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button(category, id={"type": "category-button", "index": category},
                           color="secondary", outline=True,
                           className="m-0 px-2 py-1 btn-sm text-truncate",  # Sin margen vertical
                           style={"fontSize": "10px", "minWidth": "70px", "maxWidth": "130px"})
                for category in categorias_unicas  # Evitamos duplicados
            ], className="d-flex flex-wrap justify-content-center gap-0", id="category-buttons")  # Reducción de espacios
        ])
    ], className="mb-2"),

    # Tabla con diseño más compacto
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id="articulos-table",
            columns=[
                {"name": "Año - Volumen - Número", "id": "Año - Volumen - Número"},
                {"name": "Título", "id": "Título"},
                {"name": "Categoría", "id": "Categoría"},
                {"name": "Enlace", "id": "Enlace", "presentation": "markdown"},
            ],
            style_table={'overflowX': 'auto', 'width': '100%'},
            style_cell={'textAlign': 'left', 'padding': '4px', 'whiteSpace': 'normal', 'fontSize': '12px'},
            style_header={'backgroundColor': '#0056b3', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10,
            markdown_options={"link_target": "_blank"}
        ), width=12)
    ], className="mb-4"),

    # Gráfico alineado con clics activos
    dbc.Row([
        dbc.Col(dcc.Graph(id="categoria-chart", clickData=None), width=12)
    ])
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)
