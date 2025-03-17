import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Cargar los datos
df = pd.read_excel("FH_areas_interes.xlsx", sheet_name="Sheet1", engine="openpyxl")

# Hacer los enlaces clicables
df["Enlace"] = df["Enlace"].apply(lambda x: f"[🔗 Ver artículo]({x})")

# Obtener lista única de categorías
categorias_unicas = sorted(df["Categoría"].unique())

# Obtener rango de fechas de los artículos
min_year = df["Año - Volumen - Número"].str[:4].astype(int).min()
max_year = df["Año - Volumen - Número"].str[:4].astype(int).max()
rango_fechas = f"{min_year} - {max_year}"

# Inicializar la aplicación Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])  # Estilo elegante
server = app.server  # Necesario para Render

# Diseño mejorado con distribución limpia
app.layout = dbc.Container([
    
    # Encabezado con título y estadísticas en una sola línea
    dbc.Row([
        dbc.Col(html.H3("📚 Artículos de la Revista Farmacia Hospitalaria",
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
                           color="secondary", outline=True, className="m-1 btn-sm", n_clicks=0)
                for category in categorias_unicas
            ], className="d-flex flex-wrap justify-content-center")
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
            style_cell={'textAlign': 'left', 'padding': '6px', 'whiteSpace': 'normal', 'fontSize': '12px'},
            style_header={'backgroundColor': '#0056b3', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10,
            markdown_options={"link_target": "_blank"}
        ), width=12)
    ], className="mb-4"),

    # Gráfico mejor alineado
    dbc.Row([
        dbc.Col(dcc.Graph(id="categoria-chart"), width=12)
    ])
], fluid=True)

# Callback para manejar la selección de categorías
@app.callback(
    [Output("articulos-table", "data"),
     Output("categoria-chart", "figure")],
    [Input({"type": "category-button", "index": category}, "n_clicks") for category in categorias_unicas]
)
def update_dashboard(*btn_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        selected_categories = []
    else:
        selected_categories = [categorias_unicas[i] for i, n in enumerate(btn_clicks) if n % 2 != 0]  # Alterna selección

    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Categoría"].isin(selected_categories)]

    # Crear gráfico mejorado
    category_counts = filtered_df["Categoría"].value_counts().reset_index()
    category_counts.columns = ["Categoría", "Número de Artículos"]
    fig = px.bar(category_counts,
                 x="Categoría", y="Número de Artículos",
                 title="📊 Número de Artículos por Categoría",
                 color="Número de Artículos",
                 color_continuous_scale="Blues",
                 template="plotly_white")

    fig.update_layout(xaxis_tickangle=-45, margin=dict(l=20, r=20, t=50, b=50))

    return filtered_df.to_dict("records"), fig

if __name__ == "__main__":
    app.run_server(debug=True)
