import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Cargar los datos
df = pd.read_excel("FH_areas_interes.xlsx", sheet_name="Sheet1")

# Inicializar la aplicación Dash
app = dash.Dash(__name__)
server = app.server  # Necesario para Render

app.layout = html.Div([
    html.H1("Artículos de la Revista Farmacia Hospitalaria 📚"),
    
    dcc.Dropdown(
        id="categoria-filter",
        options=[{"label": cat, "value": cat} for cat in df["Categoría"].unique()],
        multi=True,
        placeholder="Selecciona una categoría..."
    ),
    
    dash_table.DataTable(
        id="articulos-table",
        columns=[
            {"name": "Año - Volumen - Número", "id": "Año - Volumen - Número"},
            {"name": "Título", "id": "Título"},
            {"name": "Categoría", "id": "Categoría"},
            {"name": "Enlace", "id": "Enlace", "presentation": "markdown"},
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        page_size=10,
    ),
    
    dcc.Graph(id="categoria-chart")
])

@app.callback(
    [Output("articulos-table", "data"),
     Output("categoria-chart", "figure")],
    [Input("categoria-filter", "value")]
)
def update_dashboard(selected_categories):
    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Categoría"].isin(selected_categories)]
    
    category_counts = filtered_df["Categoría"].value_counts().reset_index()
    category_counts.columns = ["Categoría", "Número de Artículos"]
    fig = px.bar(category_counts, x="Categoría", y="Número de Artículos", title="Número de Artículos por Categoría")
    
    return filtered_df.to_dict("records"), fig

if __name__ == "__main__":
    app.run_server(debug=True)