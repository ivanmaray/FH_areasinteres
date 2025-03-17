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

# Inicializar la aplicación Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # Puedes cambiar el tema
server = app.server  # Necesario para Render

# Diseño mejorado con Bootstrap y botones de categoría
app.layout = dbc.Container([
    
    # Encabezado con estilo
    dbc.Row([
        dbc.Col(html.H1("📚 Artículos de la Revista Farmacia Hospitalaria",
                        className="text-center text-primary mb-4"), width=12)
    ]),

    # Tarjeta con estadísticas
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("📄 Total de Artículos", className="card-title"),
                html.H2(f"{len(df)}", className="text-primary")
            ])
        ], color="dark", outline=True, className="mb-4"), width=4)
    ], justify="center"),

    # Botones de categorías en lugar de dropdown
    html.H5("📂 Filtrar por Categoría:", className="text-center mt-3 text-light"),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button(category, id={"type": "category-button", "index": category},
                           color="info", outline=True, className="m-1", n_clicks=0)
                for category in categorias_unicas
            ], className="d-flex flex-wrap justify-content-center")
        ])
    ], className="mb-3"),

    # Tabla con diseño responsivo
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
            style_cell={'textAlign': 'left', 'padding': '8px', 'whiteSpace': 'normal'},
            style_header={'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10,
            markdown_options={"link_target": "_blank"}
        ), width=12)
    ]),

    # Gráfico alineado
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
