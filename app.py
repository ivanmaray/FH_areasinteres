import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State, MATCH, ALL

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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Diseño de la aplicación
app.layout = dbc.Container([
    
    # Encabezado con título y estadísticas en la esquina superior derecha
    dbc.Row([
        dbc.Col(html.H3("📚 Artículos de la Revista Farmacia Hospitalaria",
                        className="text-left text-primary"), width=8),
        dbc.Col(html.Div([
            html.Small(f"📅 Artículos desde {rango_fechas}", className="text-muted d-block"),
            html.Small(f"📄 Total: {len(df)} artículos", className="text-muted"),
        ], className="text-end"), width=4)
    ], align="center", className="mb-3"),

    # Botones de categorías con resaltado dinámico
    html.H6("📂 Filtrar por Categoría:", className="text-center mt-2 text-secondary"),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button(category, id={"type": "category-button", "index": category},
                           color="secondary", outline=True, className="m-1 btn-sm", n_clicks=0)
                for category in categorias_unicas
            ], className="d-flex flex-wrap justify-content-center", id="category-buttons")
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

    # Gráfico alineado
    dbc.Row([
        dbc.Col(dcc.Graph(id="categoria-chart"), width=12)
    ])
], fluid=True)

# Callback para manejar la selección de categorías y actualizar la tabla y el gráfico
@app.callback(
    [Output("articulos-table", "data"),
     Output("categoria-chart", "figure"),
     Output({"type": "category-button", "index": ALL}, "color"),
     Output({"type": "category-button", "index": ALL}, "outline")],
    [Input({"type": "category-button", "index": ALL}, "n_clicks")],
    [State({"type": "category-button", "index": ALL}, "id")]
)
def update_dashboard(btn_clicks, button_ids):
    selected_categories = [button["index"] for i, button in enumerate(button_ids) if btn_clicks[i] % 2 != 0]

    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Categoría"].isin(selected_categories)]

    # Determinar qué gráfico mostrar
    if len(selected_categories) == 0:
        # Si no hay categorías seleccionadas, mostrar TODAS optimizando espacio
        category_counts = df["Categoría"].value_counts().reset_index()
        category_counts.columns = ["Categoría", "Número de Artículos"]
        
        fig = px.bar(category_counts,
                     x="Número de Artículos", y="Categoría",
                     title="📊 Número de Artículos por Categoría",
                     orientation="h",  # Horizontal para mejor uso del espacio
                     color="Número de Artículos",
                     color_continuous_scale="Blues",
                     template="plotly_white")

        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},  # Ordenar categorías de menor a mayor
            margin=dict(l=50, r=20, t=50, b=50),  # Reducir márgenes para más espacio útil
            height=700  # Ajustar altura para que se vea mejor
        )

    elif len(selected_categories) == 1:
        # Si solo hay 1 categoría seleccionada, mostrar gráfico por número de revista
        time_counts = filtered_df["Año - Volumen - Número"].value_counts().reset_index()
        time_counts.columns = ["Número de Revista", "Número de Artículos"]
        time_counts = time_counts.sort_values(by="Número de Revista")

        fig = px.line(time_counts,
                      x="Número de Revista", y="Número de Artículos",
                      title=f"📈 Evolución de Artículos en {selected_categories[0]}",
                      markers=True,
                      template="plotly_white")

    else:
        # Si hay varias categorías seleccionadas, mostrar gráfico de artículos por categoría
        category_counts = filtered_df["Categoría"].value_counts().reset_index()
        category_counts.columns = ["Categoría", "Número de Artículos"]
        fig = px.bar(category_counts,
                     x="Categoría", y="Número de Artículos",
                     title="📊 Número de Artículos por Categoría",
                     color="Número de Artículos",
                     color_continuous_scale="Blues",
                     template="plotly_white")

        fig.update_layout(xaxis_tickangle=-45, margin=dict(l=20, r=20, t=50, b=50))

    # Cambiar color de botones seleccionados
    colors = ["primary" if button["index"] in selected_categories else "secondary" for button in button_ids]
    outlines = [False if button["index"] in selected_categories else True for button in button_ids]

    return filtered_df.to_dict("records"), fig, colors, outlines

if __name__ == "__main__":
    app.run_server(debug=True)
