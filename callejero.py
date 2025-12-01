"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############

def convertir_coordenada(coord):
    """
    Convierte una coordenada en formato 'grados minutos segundos' a decimal.
    
    Args:
        coord (str): Coordenada en formato '3º42'24.69"W'.
    
    Returns:
        float: Coordenada en formato decimal.
    
    """
    #Separamos en dos variables mediante '°'
    grados, resto = coord.split('°')    

    #Pasamos la coordenada a decimal sumando los grados, los minutos y segundos pasados a decimal
    decimal = float(grados) + float(resto.split("'")[0])/60 + float(resto.split("'")[1])/3600

    #Con un 'if' nos aseguramos de cambiar el signo a las coordenadas que sean 'S' o 'W'
    if "S" in coord or "W" in coord:
        decimal = -decimal
    
    #Devolvemos la coordenada decimal con el signo correspondiente
    return decimal



def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None
    Returns:
        pd.DataFrame: Devuelve un DataFrame con los datos procesados y las coordenadas convertidas a decimal.
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    #Ponemos en una lista las columnas que queremos que coja del csv nuestro df
    columnas = ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]

    #Hacemos una excepción por si no existe el csv
    try:
        #Creamos el df leeyendo el csv y poniendo el separador correspondiente y el 'latin1' para coger ciertos carácteres
        df = pd.read_csv(STREET_FILE_NAME, sep=";", encoding="latin1")
    except FileNotFoundError as error:
        raise error
    
    #Filtramos por las columnas que queremos
    df = df[columnas]
    
    #Convertimos la latitud y la longitud a decimal
    df["LATITUD"] = df["LATITUD"].apply(convertir_coordenada)
    df["LONGITUD"] = df["LONGITUD"].apply(convertir_coordenada)
    
    #Devolvemos el df
    return df

def busca_direccion(direccion:str, callejero):
    """ Función que busca una dirección, dada en el formato
        calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    hubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    #Pone la dirreción en mayúsculas como está en el df de callejero
    direccion=direccion.upper()
    print(direccion)
    #cogemos el número de la dirección para comprobarlo después
    numero = ''
    for i in range(len(direccion)):
        i += 1
        caracter = direccion[-i]
        if caracter.isdecimal() == False:
            break
        numero =  direccion[-i]  + numero 
    try:
        callejero_filtrado = callejero[callejero['NUMERO'] == int(numero)]
        #Iteramos cada una de las líneas para ver si coincide con la dirección dada, y en caso de que sí, devolver las coordenadas de esa dirección
        for i, linea in callejero_filtrado.iterrows():  
            if (linea['VIA_CLASE'] + ' ') in direccion and (' ' + linea['VIA_NOMBRE'] + ',') in direccion:
                return (np.float64(linea['LATITUD']), np.float64(linea["LONGITUD"]))
        raise AdressNotFoundError(f"La dirección '{direccion}' no existe")
        
        #Si no existe que devuelva que no existe la calle
    except ValueError or AdressNotFoundError:
        raise AdressNotFoundError(f"La dirección '{direccion}' no existe")



############## Parte 4 ##############


def carga_grafo() -> nx.MultiDiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """

    """
    Función que recupera el grafo de calles de Madrid desde OpenStreetMap o desde un archivo local.

    Si el archivo "madrid.graphml" ya existe, carga el grafo desde ese archivo. Si no existe,
    lo descarga de OpenStreetMap usando la función graph_from_place, lo guarda en el archivo
    "madrid.graphml" y lo retorna.

    Returns:
        nx.MultiDiGraph: Grafo de calles de Madrid (MultiDiGraph).
    Raises:
        RuntimeError: Si ocurre algún error al descargar o cargar el grafo.
    """
    #Ponemos en una variable la ruta del archivo
    filepath = "madrid.graphml" 

    #Ponemos una excepción para cualquier fallo que se de al cargar el grafo
    try:
        #Si el archivo existe lo guardamos en la variable grafo 
        if os.path.exists(filepath):
            grafo = ox.load_graphml(filepath)
        else:
            #Si no existe descargamos el grafo desde OpenStreetMap y lo guardamos
            grafo = ox.graph_from_place("Madrid, Spain", network_type="drive")
            ox.save_graphml(grafo, filepath)
        
        #Devolvemos lo cargado en la varibale grafo 
        return grafo
    except Exception as e:
        raise RuntimeError("Error al cargar o descargar el grafo de calles de Madrid.") from e





def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles asociado al multidigrafo dado.
    Raises: None
    """
    #Primero convertimos el multidigrafo a digrafo
    digrafo = ox.utils_graph.convert.to_digraph(multidigrafo)

    #Sacamos la lista de bucles y los eliminamos
    bucles = list(nx.selfloop_edges(digrafo))
    digrafo.remove_edges_from(bucles)

    #Devolvemos el digrafo 
    return digrafo


def dibuja_grafo(grafo: nx.DiGraph, ruta: list = None) -> None:
    """
    Función que dibuja el grafo dirigido usando las posiciones geográficas de los nodos.
    Resalta la ruta si se proporciona.

    Args:
        grafo (nx.DiGraph): Grafo dirigido de las calles, con información geográfica en los nodos.
        ruta (list, opcional): Lista de nodos que forman la ruta a resaltar. Por defecto, None.
    
    Returns:
        None: La función dibuja el grafo y no devuelve ningún valor.
    """
    #Extraemos las posiciones geográficas de los nodos y las introducimos en un diccionario
    posiciones = {}
    for nodo, data in grafo.nodes(data=True):
        posiciones[nodo] = (data['x'], data['y'])

    plt.figure(figsize=(10, 10))

    #Dibuja todas las calles en gris
    nx.draw(
        grafo,
        pos=posiciones,
        node_size=0,       
        edge_color="gray",
        width=0.5,        
        alpha=0.8,  
        #Quitamos las flechas del nodo para verlo con más claridad y que no se vea tan gordo     
        arrows=False  
    )

    #Crear una lista de pares con las aristas de la ruta
    aristas_ruta = []
    for i in range(len(ruta) - 1):
        aristas_ruta.append((ruta[i], ruta[i + 1]))

    #Dibujar las aristas de la ruta en rojo para poder visualizarlo
    nx.draw_networkx_edges(
        grafo,
        pos=posiciones,
        edgelist=aristas_ruta,
        edge_color="red",
        width=1.5, 
        #Quitamos las flechas del nodo para verlo con más claridad y que no se vea tan gordo 
        arrows=False   
    )

    #Resaltar el nodo de origen (primer nodo de la ruta) en verde
    nx.draw_networkx_nodes(
        grafo,
        pos=posiciones,
        #Primer nodo (origen)
        nodelist=[ruta[0]],
        node_size=50,
        node_color="red",
        label="Origen"
    )

    #Resaltar el nodo de destino (último nodo de la ruta) en azul
    nx.draw_networkx_nodes(
        grafo,
        pos=posiciones,
        #último nodo (destino)
        nodelist=[ruta[-1]],
        node_size=50,
        node_color="green",
        label="Destino"
    )

    plt.title("Mapa con ruta")
    plt.show()


