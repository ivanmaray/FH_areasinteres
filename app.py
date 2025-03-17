import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Cargar los datos
df = pd.read_excel("FH_areas_interes.xlsx", sheet_name="Sheet1", engine="openpyxl")

# Hacer los enlaces clicables
df["Enlace"] = df["Enlace"].apply(lambda x: f"[Ver artículo]({x})")

# Inicializar la aplicación Dash
app = dash.Dash(__name__)
server = app.server  # Necesario para Render

# Diseño de la aplicación
app.layout = html.Div([
    html.H1("📚 Artículos de la Revista Farmacia Hospitalaria", style={'textAlign': 'center', 'color': '#4A90E2'}),

    html.Label("🔎 Filtrar por Categoría:", style={'fontSize': '18px'}),
    dcc.Dropdown(
        id="categoria-filter",
        options=[{"label": cat, "value": cat} for cat in sorted(df["Categoría"].unique())],
        multi=True,
        placeholder="Selecciona una categoría...",
        style={'marginBottom': '20px'}
    ),

    dash_table.DataTable(
        id="articulos-table",
        columns=[
            {"name": "Año - Volumen - Número", "id": "Año - Volumen - Número"},
            {"name": "Título", "id": "Título"},
            {"name": "Categoría", "id": "Categoría"},
            {"name": "Enlace", "id": "Enlace", "presentation": "markdown"},
        ],
        style_table={'overflowX': 'auto', 'marginBottom': '20px'},
        style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '14px'},
        style_header={'backgroundColor': '#4A90E2', 'color': 'white', 'fontWeight': 'bold'},
        page_size=10,
        markdown_options={"link_target": "_blank"}  # Abre enlaces en nueva pestaña
    ),

    dcc.Graph(id="categoria-chart")
])

# Callback para actualizar la tabla y el gráfico
@app.callback(
    [Output("articulos-table", "data"),
     Output("categoria-chart", "figure")],
    [Input("categoria-filter", "value")]
)
def update_dashboard(selected_categories):
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
                 template="simple_white")

    fig.update_layout(xaxis_tickangle=-45)

    return filtered_df.to_dict("records"), fig

if __name__ == "__main__":
    app.run_server(debug=True)
