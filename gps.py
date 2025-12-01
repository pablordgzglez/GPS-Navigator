import os
import callejero
from grafo_pesado import camino_minimo
from typing import Callable, List, Tuple
import networkx as nx
import osmnx as ox
import math
from threading import Thread


def calcular_peso_distancia(G: nx.DiGraph, u: object, v: object) -> float:
    """Calcula el peso basado en la distancia de la arista."""
    return G[u][v].get("length", 1)


def calcular_peso_tiempo(G: nx.DiGraph, u: object, v: object) -> float:
    """Calcula el peso basado en el tiempo estimado."""
    tipo_via = G[u][v].get("highway", "otro")
    if type(tipo_via) != str:
        tipo_via = tipo_via[0]
    #Asume 50 km/h si no hay información
    velocidad = callejero.MAX_SPEEDS.get(tipo_via, 50)
    velocidad = float(velocidad)
    #Longitud de la arista en metros y si no hay información asume 1
    longitud = G[u][v].get("length", 1)
    longitud = float(longitud)
    #Distancia/velocidad = tiempo
    return int(longitud / (velocidad * 1000 / 3600)) 


def calcular_peso_semaforos(G: nx.DiGraph, u: object, v: object) -> float:
    """Calcula el peso considerando semáforos."""
    tiempo_base = calcular_peso_tiempo(G, u, v)
    prob_semaforo = 0.8
    tiempo_semaforo = 30 
    return tiempo_base + prob_semaforo * tiempo_semaforo

def calcular_angulo(v1: Tuple, v2: Tuple) -> float:
    """
    Calcula el ángulo entre dos vectores en un plano para conocer si el giro es a la izquierda o a la derecha.
    
    Args:
        v1 (tuple): Vector 1 como (x, y).
        v2 (tuple): Vector 2 como (x, y).
    
    Returns:
        float: Ángulo en grados entre -180 y 180.
    """
    angulo = math.degrees(math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0]))
    if angulo > 180:
        angulo -= 360
    elif angulo < -180:
        angulo += 360
    return angulo




def generar_instrucciones(G: nx.DiGraph, ruta: List) -> List:
    """Genera instrucciones de navegación para la ruta."""
    instrucciones = []
    calle_actual = None
    #Para acumular la longitud de la calle y que no escriba intrucciones seguidas de pocos metros en la misma calle 
    longitud_acumulada = 0 
    contador = 1
    for i in range(len(ruta) - 1):
        u, v = ruta[i], ruta[i + 1]
        nombre_calle = G[u][v].get("name", "Calle desconocida")
        longitud = G[u][v].get("length")

        #Si estamos en una nueva calle, generar la instrucción anterior y reiniciar las variables
        if nombre_calle != calle_actual:
            if calle_actual is not None:
                #Calcular el giro entre los segmentos
                nodo_anterior = ruta[i - 1]
                coords_anterior = (G.nodes[nodo_anterior]['x'], G.nodes[nodo_anterior]['y'])
                coords_actual = (G.nodes[u]['x'], G.nodes[u]['y'])
                coords_siguiente = (G.nodes[v]['x'], G.nodes[v]['y'])

                vector1 = (coords_actual[0] - coords_anterior[0], coords_actual[1] - coords_anterior[1])
                vector2 = (coords_siguiente[0] - coords_actual[0], coords_siguiente[1] - coords_actual[1])

                angulo = calcular_angulo(vector1, vector2)

                #Según los grados del ángulo para conocer si el giro es hacia un lado o hacia el otro
                #Suponemos que entre -45 y 45 es seguir recto, >45 a la izquierda y <45 a la derecha
                if -45 <= angulo <= 45:
                    giro = "Continúa recto"
                elif angulo > 45:
                    giro = "Gira a la izquierda"
                else:
                    giro = "Gira a la derecha"

                instrucciones.append(f"{contador} -> {giro} hacia {calle_actual} y continúa por ella durante {int(longitud_acumulada)} metros.")
                contador += 1
            #Reiniciar longitud acumulada y actualizar la calle actual
            longitud_acumulada = longitud
            calle_actual = nombre_calle
        else:
            #Si seguimos en la misma calle, acumulamos la longitud
            longitud_acumulada += longitud

    instrucciones.append(f"Has llegado a tu destino.")
    
    return instrucciones

def pedir_opcion() -> str:
    #Printeamos las opciones
    print(' ')
    print("*************************TIPO_RUTA*************************")
    print('*                                                         *')
    print("*          1 -> Ruta más corta(distancia)                 *")
    print("*          2 -> Ruta más rápida(tiempo)                   *")
    print("*          3 -> Ruta más rápida optimizando semáforos     *")
    print('*                                                         *')
    print("***********************************************************")

    #Hacemos que elija una, corrigiendo en caso de no introducir lo deseado
    opcion = input("Elige el numero de la opcion que desea: ")
    while opcion not in ["1","2","3"]:
        opcion = input("ERROR: Introduce una opción válida(1, 2 o 3): ")
    return opcion 

def pedir_direcciones(df):
        #Solicitar direcciones. Un bucle que mientras se introduzcan direcciones inválidas, se vuelvan a pedir los nombres
        validas = False
        while not validas:
            print("INTRODUCE LAS DIRECCIONES DE ORIGEN Y DESTINO.")
            try:
                origen = input("Dirección de origen Formato -> ('CLASE PARTÍCULA NOMBRE, NÚMERO'): ")
                destino = input("Dirección de destino Formato -> ('CLASE PARTÍCULA NOMBRE, NÚMERO'): ")
                coord_origen = callejero.busca_direccion(origen, df)
                coord_destino = callejero.busca_direccion(destino, df)
                validas = True
            except callejero.AdressNotFoundError as e:
                print(f'-ERROR: {e}')
                print()
                validas = False
        return coord_origen, coord_destino

if __name__ == "__main__":
    #Cargar datos y grafo
    df = callejero.carga_callejero()
    G = callejero.procesa_grafo(callejero.carga_grafo())
    repetir = True
    while repetir == True:
        #Pedimos las coordenadas de origen y de destino
        coord_origen, coord_destino = pedir_direcciones(df)

        #Encontramos los nodos más cercanos
        nodo_origen = ox.distance.nearest_nodes(G, coord_origen[1], coord_origen[0])
        nodo_destino = ox.distance.nearest_nodes(G, coord_destino[1], coord_destino[0])

        #Pedimos la opción
        opcion = pedir_opcion()

        #Metemos las distintas funciones para que coja una en funcion de la opcion elegida
        pesos = [calcular_peso_distancia, calcular_peso_tiempo, calcular_peso_semaforos]

        #Sacamos la ruta, llamando a la funcion camino_minimo
        ruta = camino_minimo(G, pesos[int(opcion) - 1], nodo_origen, nodo_destino)

        #Generamos instrucciones
        instrucciones = generar_instrucciones(G, ruta)
        print()
        print()
        print("INSTRUCCIONES PARA LLEGAR A TU DESTINO: ")
        print('*************************************************************************')
        print('*************************************************************************')
        for instruccion in instrucciones:
            print(instruccion)
        print('*************************************************************************')
        print('*************************************************************************')

        #Visualizamos la ruta
        callejero.dibuja_grafo(G, ruta)


        #Preguntamos si desea repetir el proceso
        print()
        opcion2 = input("¿Deseas calcular otra ruta? (s/n): ")
        while opcion2.lower() != 'n ' and opcion2.lower() != 's':
            opcion2 = input('ERROR: Parametro no valido (s/n)')
        if opcion2.lower() == "n":
            repetir = False
    print("¡Gracias por usar el GPS!")
            