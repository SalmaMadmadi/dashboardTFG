import numpy as np

entrada0 = {'x': 619282.0, 'y': 5809118.0}
entrada1 = {'x': 619358.0, 'y': 5809164.0}
entrada2 = {'x': 619288.0, 'y': 5809174.0}
salida3 = {'x': 619269.0, 'y': 5809117.0}
salida4 = {'x': 619360.0, 'y': 5809164.0}
salida5 = {'x': 619291.0, 'y': 5809181.0}

def buscar_entrada(vehicle):
    global entrada0
    global entrada1
    global entrada2
    min_dist = 100000000
    entrada = 0

    dist = np.sqrt((vehicle.utm_x[0] - entrada0['x'])**2 + (vehicle.utm_y[0] - entrada0['y'])**2)
    if dist < min_dist:
        min_dist = dist
        entrada = 0
    dist = np.sqrt((vehicle.utm_x[0] - entrada1['x'])**2 + (vehicle.utm_y[0] - entrada1['y'])**2)
    if dist < min_dist:
        min_dist = dist
        entrada = 1
    dist = np.sqrt((vehicle.utm_x[0] - entrada2['x'])**2 + (vehicle.utm_y[0] - entrada2['y'])**2)
    if dist < min_dist:
        min_dist = dist
        entrada = 2
    
    return entrada

def buscar_salida(vehicle):
    global salida3
    global salida4
    global salida5
    min_dist = 100000000
    salida = 0
    ultimo_indice = vehicle.utm_x.__len__() - 1

    dist = np.sqrt((vehicle.utm_x[ultimo_indice] - salida3['x'])**2 + (vehicle.utm_y[ultimo_indice] - salida3['y'])**2)
    if dist < min_dist:
        min_dist = dist
        salida = 3
    dist = np.sqrt((vehicle.utm_x[ultimo_indice] - salida4['x'])**2 + (vehicle.utm_y[ultimo_indice] - salida4['y'])**2)
    if dist < min_dist:
        min_dist = dist
        salida = 4
    dist = np.sqrt((vehicle.utm_x[ultimo_indice] - salida5['x'])**2 + (vehicle.utm_y[ultimo_indice] - salida5['y'])**2)
    if dist < min_dist:
        min_dist = dist
        salida = 5
    
    return salida

def clusterizar_datos(vehicles):
    # Hay 3 entradas y 3 salidas, por lo que pueden haber 9 rutas diferentes
    # Primero buscar entrada mas cercana al punto
    # Segundo buscar salida mas cercana al punto
    for vehicle_id in vehicles:
        entrada = buscar_entrada(vehicles[vehicle_id])
        salida = buscar_salida(vehicles[vehicle_id])
        if(entrada == 0 and salida == 3):
            vehicles[vehicle_id].tipo_ruta = 1
        elif(entrada == 0 and salida == 4):
            vehicles[vehicle_id].tipo_ruta = 2
        elif(entrada == 0 and salida == 5):
            vehicles[vehicle_id].tipo_ruta = 3
        elif(entrada == 1 and salida == 3):
            vehicles[vehicle_id].tipo_ruta = 4
        elif(entrada == 1 and salida == 4):
            vehicles[vehicle_id].tipo_ruta = 5
        elif(entrada == 1 and salida == 5):
            vehicles[vehicle_id].tipo_ruta = 6
        elif(entrada == 2 and salida == 3):
            vehicles[vehicle_id].tipo_ruta = 7
        elif(entrada == 2 and salida == 4):
            vehicles[vehicle_id].tipo_ruta = 8
        elif(entrada == 2 and salida == 5):
            vehicles[vehicle_id].tipo_ruta = 9
        #print("Vehicle " + str(vehicle_id) + " is in route " + str(vehicles[vehicle_id].tipo_ruta) + ".")

    return vehicles