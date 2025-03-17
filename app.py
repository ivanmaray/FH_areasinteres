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

# Convertir enlaces en texto clicable con icono
df["Enlace"] = df["Enlace"].apply(lambda x: f"[🔗 Ver artículo]({x})" if pd.notna(x) else "")

# Obtener rango de fechas de los artículos
min_year = df["Año - Volumen - Número"].str[:4].astype(int).min()
max_year = df["Año - Volumen - Número"].str[:4].astype(int).max()
rango_fechas = f"{min_year} - {max_year}"

# Inicializar Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Diseño de la aplicación
app.layout = dbc.Container([
    
# Título con enlace y numero de articulos y fechas
    dbc.Row([
        dbc.Col(html.H4([
            "📚 Artículos de la ",
            html.A("Revista Farmacia Hospitalaria", href="https://www.revistafarmaciahospitalaria.es/", target="_blank", className="text-primary fw-bold text-decoration-none")
        ], className="text-left"), width=8),
        dbc.Col(html.Div([
            html.Small(f"📅 Artículos desde {rango_fechas}", className="text-muted d-block"),
            html.Small(f"📄 Total: {len(df)} artículos", className="text-muted"),
        ], className="text-end"), width=4)
    ], align="center", className="mb-3"),

    # Botones de categorías compactos
    html.H6("📂 Filtrar por Categoría:", className="text-center mt-2 text-secondary"),
    dbc.Row([
        dbc.Col(html.Div([
            dbc.Button(category, id={"type": "category-button", "index": category},
                       color="secondary", outline=True, className="m-1 px-2 py-1 btn-sm text-truncate",
                       style={"fontSize": "11px", "minWidth": "90px", "maxWidth": "140px"})
            for category in categorias_unicas
        ], className="d-flex flex-wrap justify-content-center gap-1"), width=12)
    ], className="mb-2"),

    # Tabla con enlaces clicables
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

    # Gráfico interactivo
    dbc.Row([dbc.Col(dcc.Graph(id="categoria-chart", clickData=None), width=12)]),

], fluid=True)

# Callback para filtrado
@app.callback(
    [Output("articulos-table", "data"),
     Output("categoria-chart", "figure"),
     Output({"type": "category-button", "index": ALL}, "color"),
     Output({"type": "category-button", "index": ALL}, "outline")],
    [Input({"type": "category-button", "index": ALL}, "n_clicks"),
     Input("categoria-chart", "clickData")],
    [State({"type": "category-button", "index": ALL}, "id")]
)
def update_dashboard(btn_clicks, clickData, button_ids):
    if not btn_clicks:
        btn_clicks = [0] * len(button_ids)

    # Selección de categorías desde los botones
    selected_categories = [button["index"] for i, button in enumerate(button_ids) if btn_clicks[i] and btn_clicks[i] % 2 != 0]

    # Selección desde el gráfico
    if clickData and "points" in clickData:
        clicked_category = clickData["points"][0]["y"]
        if clicked_category in selected_categories:
            selected_categories.remove(clicked_category)
        else:
            selected_categories.append(clicked_category)

    # Filtrar datos
    filtered_df = df if not selected_categories else df[df["Categoría"].isin(selected_categories)]

    # Mostrar gráfico por fecha si hay solo una categoría
    if len(selected_categories) == 1:
        time_counts = filtered_df["Año - Volumen - Número"].value_counts().reset_index()
        time_counts.columns = ["Número de Revista", "Número de Artículos"]
        time_counts = time_counts.sort_values(by="Número de Revista")

        fig = px.line(time_counts, x="Número de Revista", y="Número de Artículos",
                      title=f"📈 Evolución de {selected_categories[0]}",
                      markers=True, template="plotly_white")
    else:
        category_counts = df["Categoría"].value_counts().reset_index()
        category_counts.columns = ["Categoría", "Número de Artículos"]
        
        fig = px.bar(category_counts, x="Número de Artículos", y="Categoría",
                     title="📊 Artículos por Categoría",
                     orientation="h", color="Número de Artículos",
                     color_continuous_scale="Blues", template="plotly_white")

        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=700)

    # Cambiar color de botones seleccionados
    colors = ["primary" if button["index"] in selected_categories else "secondary" for button in button_ids]
    outlines = [False if button["index"] in selected_categories else True for button in button_ids]

    return filtered_df.to_dict("records"), fig, colors, outlines

if __name__ == "__main__":
    app.run_server(debug=True)
