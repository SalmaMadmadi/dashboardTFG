# --------------------------------------------------------------------
# App web para visualización de datos
# Trabajo Final de Grado - Ing. Multimedia
# Autor: Salma Madmadi
# Instrucciones para ejecutarlo:
# 1- Abrir terminal en el directorio donde se encuentre este fichero
# 2- Activar entorno (si hay)
# 3- Ejecutar el comando python nombrefichero.py
# -------------------------------------------------------------------

import time
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import callback_context
import plotly.graph_objs as go

import sqlite3
import matplotlib.pyplot as plt
import matplotlib

# Clases propias
import vehicle
import cluster

# Ficheros a leer
db_name = "trajectories_rdb1_v3.sqlite"
pgw_name = "rdb1.pgw"

# Leer fichero pgw (aunque por ahora no se usa)
def load_pgw():
    with open(pgw_name, 'r') as f:
        lines = f.readlines()
    xWidth = float(lines[0])
    yWidth = float(lines[1])
    xHeight = float(lines[2])
    yHeight = float(lines[3])
    xCenterUTM = float(lines[4])
    yCenterUTM = float(lines[5])

    return xWidth, yWidth, xHeight, yHeight, xCenterUTM, yCenterUTM

# Leer de la base de datos filtrando por clase
def getFromDBbyClass(class_name, tablas=4):
    vehicles = {}
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for i in range(1, tablas):
        cursor.execute("SELECT OBJID as \"ObjId\", TIMESTAMP as \"Timestamp\", CLASS as \"Class\"," 
                    + "UTM_X as \"Utm_x\", UTM_Y as \"Utm_y\", UTM_ANGLE as \"Utm_a\", V as \"Vel\","
                    + "ACC as \"Acc\", ACC_LAT as \"Acc_l\", ACC_TAN as \"Acc_t\", WIDTH as \"Width\","
                    + "LENGTH as \"Length\", TRAILER_ID as \"Trailer\" "
                    + "FROM rdb1_1 WHERE CLASS = '" + class_name + "'")
        rows = cursor.fetchall()
        for row in rows:
            objid = row[0]
            timestamp = row[1]
            classv = row[2]
            utm_x = row[3]
            utm_y = row[4]
            v = row[6]
            v = v * 1000 / 3600 

            if objid not in vehicles:
                vehicles[objid] = vehicle.Vehicle(objid)

            vehicles[objid].timestamp.append(timestamp)
            vehicles[objid].utm_x.append(utm_x)
            vehicles[objid].utm_y.append(utm_y)
            vehicles[objid].v.append(v)
            vehicles[objid].v_class = classv

    return vehicles

# Leer de la base de datos por ID
def getFromDBbyID(id, tablas=2):
    vehicles = {}
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for i in range(1, tablas):
        cursor.execute("SELECT OBJID as \"ObjId\", TIMESTAMP as \"Timestamp\", CLASS as \"Class\"," 
                    + "UTM_X as \"Utm_x\", UTM_Y as \"Utm_y\", UTM_ANGLE as \"Utm_a\", V as \"Vel\","
                    + "ACC as \"Acc\", ACC_LAT as \"Acc_l\", ACC_TAN as \"Acc_t\", WIDTH as \"Width\","
                    + "LENGTH as \"Length\", TRAILER_ID as \"Trailer\" "
                    + "FROM rdb1_1 WHERE OBJID = '" + id + "'")
        rows = cursor.fetchall()
        for row in rows:
            objid = row[0]
            timestamp = row[1]
            utm_x = row[3]
            classv = row[2]
            utm_y = row[4]
            v = row[6]
            v = v * 1000 / 3600 

            if objid not in vehicles:
                vehicles[objid] = vehicle.Vehicle(objid)

            vehicles[objid].timestamp.append(timestamp)
            vehicles[objid].utm_x.append(utm_x)
            vehicles[objid].utm_y.append(utm_y)
            vehicles[objid].v.append(v)
            vehicles[objid].v_class = classv

    return vehicles

# Function para obtener vehiculos según intérvalo de tiempo
def get_vehicles_in_time_interval(vehicles, start_time, end_time):
    vehicles_in_time_interval = {}
    for vehicle_id, vehicle in vehicles.items():
        indices = [i for i, t in enumerate(vehicle.timestamp) if float(start_time) <= float(t) <= float(end_time)]
        if indices:
            vehicles_in_time_interval[vehicle_id] = vehicle
    return vehicles_in_time_interval

# Funcion para obtener los datos en los extremos 
def get_min_utm(vehicles):
    min_utm_x = min(min(vehicle.utm_x) for vehicle in vehicles.values())
    min_utm_y = min(min(vehicle.utm_y) for vehicle in vehicles.values())
    max_utm_x = max(max(vehicle.utm_x) for vehicle in vehicles.values())
    max_utm_y = max(max(vehicle.utm_y) for vehicle in vehicles.values())
    max_v = max(max(vehicle.v) for vehicle in vehicles.values())
    min_v = min(min(vehicle.v) for vehicle in vehicles.values())
    return min_utm_x, min_utm_y, max_utm_x, max_utm_y, max_v, min_v

# Funcion para obtener posiciones en intervalo de tiempo 
def get_positions_in_time_interval(vehicles, start_time, end_time):
    positions = {}
    for vehicle_id, vehicle in vehicles.items():
        indices = [i for i, t in enumerate(vehicle.timestamp) if float(start_time) <= float(t) <= float(end_time)]
        positions[vehicle_id] = {
            'utm_x': [vehicle.utm_x[i] for i in indices],
            'utm_y': [vehicle.utm_y[i] for i in indices],
            'v': [vehicle.v[i] for i in indices],
            'time': [vehicle.timestamp[i] for i in indices]
        }
    return positions

# Funcion para dibujar la grafica de posiciones de los vehiculos
def draw_vehicle_positions(vehicles, start_time, end_time):
    positions = get_positions_in_time_interval(vehicles, start_time, end_time)
    min_x_value, min_y_value, max_x_value, max_y_value, _, _ = get_min_utm(vehicles)

    fig = go.Figure()
    cmap = px.colors.diverging.Tealrose

    # Leyenda de velocidad a la derecha
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='markers',
        marker=dict(
            colorscale=cmap,
            showscale=True,
            colorbar=dict(title='Velocity', x=0, y=0.5, len=0.4, yanchor='middle', tickvals=[0, 5, 10, 15]),
            cmin=0,  # minimo
            cmax=15,  # maximo
            color=[],
        ),
        visible=False  
    ))

    # Descripcion de cada vehiculo (derecha)
    for vehicle_id, pos in positions.items():
        fig.add_trace(go.Scatter(
            x=pos['utm_x'],
            y=pos['utm_y'],
            mode='markers',
            marker=dict(
                color=pos['v'],
                colorscale=cmap,
                size=8,
                colorbar=dict(title="Velocity", tickvals=[0, 20, 40, 60, 80, 100]),
            ),
            name=f"Vehicle {vehicle_id} - {vehicles[vehicle_id].v_class}", 
        ))

    fig.update_layout(
        xaxis=dict(range=[min_x_value - 10, max_x_value + 10]),
        yaxis=dict(range=[min_y_value - 10, max_y_value + 10]),
        title="Vehicle Positions",
        xaxis_title="UTM X",
        yaxis_title="UTM Y",
        coloraxis_colorbar_x=-0.1,  
        coloraxis_colorbar_thickness=20,  
        height=600,
        showlegend=True,
        legend=dict(x=1.1, y=1),  
    )

    return fig

# Funcion que devuelve un array con la distancia recorrida de cierto vehiculo
def get_locations(vehicle):
    loc = [0]
    for i in range(1, len(vehicle.v)):
        loc.append(loc[i-1] + vehicle.v[i]*360000/1000000)
    return loc

# Funcion que dibuja las trayectorias de uno o más vehiculos
def draw_trajectories(vehicles, trayectoria=3):
    fig = go.Figure()

    # Obtener valores mínimos y máximos de velocidad para la escala de colores
    _, _, _, _, max_v, min_v = get_min_utm(vehicles)

    # Crear una escala de colores usando un mapa de colores
    cmap = px.colors.sequential.Cividis

    for vehicle_id, vehicle in vehicles.items():
        # Verificar si vehicle.tipo_ruta no es None
        if vehicle.tipo_ruta is not None and int(vehicle.tipo_ruta) == int(trayectoria):
            loc = get_locations(vehicle)
            for i in range(1, len(loc)):
                fig.add_trace(go.Scatter(
                    x=vehicle.timestamp[i-1:i+1],
                    y=loc[i-1:i+1],
                    mode='lines'
                ))

    # Ajustar diseño del gráfico
    fig.update_layout(
        xaxis_title='Tiempo (s)',
        yaxis_title='Ubicación (km)',
        title='Trayectorias de Vehículos',
        coloraxis_colorbar=dict(
            title='Velocidad',
            tickvals=[0, 255],
            ticktext=[f'{min_v:.2f}', f'{max_v:.2f}'],
            len=0.4,
            yanchor='middle',
            y=0.5,
            thickness=20,
        ),
        height=600,
        showlegend=False,
        legend=dict(x=1.1, y=1), 
    )

    return fig

# -------------------------------------------
# -------------------------------------------
#                INTERFAZ DASH
# -------------------------------------------
# -------------------------------------------

# Inicialización de server
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Estilos
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '26rem',
    'padding': '2rem 1rem',
    'background-color': '#f8f9fa',
    'overflow-y': 'auto', 
    'max-height': '100vh',  
}

CONTENT_STYLE = {
    "margin-left": "28rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "margin-top": "4rem"
}

# Div filtro (izquierda)
sidebar = html.Div(
    [
        html.H3("Filtros", style={'text-align': 'center'}),
        html.Hr(),
        html.P("Parámetros a configurar", className="lead", style={'text-align': 'center'}),
        dbc.Row(
            [
                dbc.Col([
                    dbc.Label("Tipos de vehículos", className='text-center'),
                    dcc.Dropdown(
                        id='vehicle',
                        placeholder='Select a vehicle',
                        options=[
                            {'label': 'Car', 'value': 'Car'},
                            {'label': 'Heavy Vehicle', 'value': 'Heavy Vehicle'},
                            {'label': 'Bus', 'value': 'Bus'},
                            {'label': 'Motorcycle', 'value': 'Motorcycle'},
                            {'label': 'Bicycle', 'value': 'Bicycle'},
                            {'label': 'Pedestrian', 'value': 'Pedestrian'},
                            {'label': 'Medium Vehicle', 'value': 'Medium Vehicle'}
                        ],
                        value=['Heavy Vehicle', 'Car', 'Bus'],
                        multi=True
                    ),
                ], style={'text-align': 'center'}),
            ]
        ),
        html.P("Intérvalo de tiempo", className="lead", style={'text-align': 'center', 'margin-top': '2rem'}),
        html.Div([
            dcc.Slider(
                min=0,
                max=1400,
                step=10,
                value=10,
                id='timestamp-slider-input',
                marks=None,
            ),
            html.Div(id='timestamp-slider-output', style={'text-align': 'center', 'margin-top': '1px'})
        ]),
        dbc.Row(
            [
                dbc.Col([
                    html.P("Selecciona la trayectoria", className="lead", style={'text-align': 'center', 'margin-top': '2rem'}),
                    dbc.Col(
                        html.Img(src=app.get_asset_url('Salidas.png'), style={'width': '100%', 'height': 'auto'}),
                        style={'text-align': 'center'}
                    ),
                    dcc.Dropdown(
                        id='trajectory',
                        options=[{'label': str(i), 'value': i} for i in range(0, 9)],
                        value='1'  
                    )
                ], style={'text-align': 'center'}),
            ], style={'margin-top': '1rem'}
        ),
        dbc.Row(
            [
                dbc.Col([
                    dbc.Label("ID del vehículo", className='text-center', style={'margin-right': '5px'}),
                    
                    dcc.Input(
                        id='vehicle-id-input',
                        type='number',
                        placeholder='ID por ejemplo 1',
                        debounce=True,
                        min=1,
                    )
                ], style={'text-align': 'center'})
            ],
            style={'margin-top': '1rem'}
        ),
        dbc.Row(
            [
                dbc.Col([
                    dbc.Label("Selecciona los vehículos que quieras ver a la derecha"),
                    dcc.Markdown(id='plant_summary')
                ], style={'text-align': 'center'})
            ], style={'margin-top': '1rem'}
        ),
        dbc.Row(
        [

        ], style={'margin-top': '1rem'}
        )
    ],
    style=SIDEBAR_STYLE,
)

# Div de contenido (derecha)
content = html.Div(
    children=[
        dcc.Graph(id='map', clickData={'points': [{'hovertext': 'Chelsea'}]}),
        dcc.Graph(id='graph')
    ],
    style=CONTENT_STYLE
)

# Barra de navegación
navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('icono.png'), height="48px")),
                    dbc.Col(dbc.NavbarBrand("TFG", className="ml-2"), style={'text-decoration': 'none'}),
                ],
                align="center",
                className="no-gutters",
            ),
            href="https://plot.ly",
            style={'margin-left': '2rem'}
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Graphics", href="#")),
                    dbc.NavItem(dbc.NavLink("Visualization", href="#")),
                ],
                className="ml-auto",
                navbar=True
            ),
            id="navbar-collapse",
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
    sticky="top"
)

# Layout de la app
app.layout = html.Div([navbar, sidebar, content])

# --------------------------------------
# --------------------------------------
#         FUNCIONES DE CALLBACK
# --------------------------------------
# --------------------------------------

# Callback to update timestamp slider output
@app.callback(
    Output('timestamp-slider-output', 'children'),
    Input('timestamp-slider-input', 'value'))
def update_output(value):
    return 'Timestamp from 0 to {}'.format(value)

# Callback to update graphs based on selected vehicle types, timestamp, and trajectory
@app.callback(
    [Output('map', 'figure'), Output('graph', 'figure')],
    [Input('vehicle', 'value'), Input('timestamp-slider-input', 'value'), Input('trajectory', 'value'), Input('vehicle-id-input', 'value')])
def update_graphs(vehicle_types, timestamp, trajectory, vehicle_id):
    cont_ini = time.time()

    if trajectory is None:
        trajectory = 1

    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    vehicles = {}

    if triggered_id == 'vehicle-id-input':
        v_data = getFromDBbyID(str(vehicle_id))
        vehicles.update(v_data)
        vehicles_t = cluster.clusterizar_datos(vehicles)
        start_time = 0
        end_time = timestamp
        traj_fig = draw_trajectories(vehicles_t, vehicles_t[vehicle_id].tipo_ruta)
    else:
        for v_type in vehicle_types:
            v_data = getFromDBbyClass(v_type)
            vehicles.update(v_data)

        vehicles_t = cluster.clusterizar_datos(vehicles)
        start_time = 0
        end_time = timestamp
        traj_fig = draw_trajectories(vehicles_t, trajectory)

    map_fig = draw_vehicle_positions(vehicles, start_time, end_time)

    cont_fin = time.time()
    print(f"Tiempo de ejecución: {cont_fin - cont_ini} segundos")

    return map_fig, traj_fig

if __name__ == '__main__':
    app.run_server(debug=True)