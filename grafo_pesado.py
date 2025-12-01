"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys
import random 
import heapq #Librería para la creación de colas de prioridad

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""

def dijkstra(G: Union[nx.Graph, nx.DiGraph], peso: Union[Callable[[nx.Graph, object, object], float], Callable[[nx.DiGraph, object, object], float]], origen: object) -> Dict[object, object]:
    """
    Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        G (Union[nx.Graph, nx.DiGraph]): Grafo (dirigido o no dirigido).
        peso (Union[Callable[[nx.Graph, object, object], float], Callable[[nx.DiGraph, object, object], float]]): Función de peso de las aristas.
        origen (object): vértice del grafo de origen.
    
    Returns:
        Dict[object, object]: Diccionario que indica, para cada vértice alcanzable desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    
    Raises:
        TypeError: Si "origen" no es un vértice válido.
    """
    #Inicializamos las variables necesarias
    padre = {}
    distancias = {}
    visitado = {}
    
    #Para cada nodo, no tiene padre, distancia infinita, no visitado inicialmente
    for v in G.nodes:
        padre[v] = None   
        distancias[v] = float('inf') 
        visitado[v] = False  
    
    #Ponemos que la distancia al origen es 0 y que no tiene padre
    distancias[origen] = 0      
    padre[origen] = None   

    #Incializamos la lista de prioridad de origen ordenada por d
    Q = [(0, random.randint(1,100000), origen)]


    #Mientras que exista Q
    while Q:
        #Extraemos el nodo con la menor distancia y la distancia mínima
        d_v, _, v = heapq.heappop(Q)

        #Recorremos los vecinos de v
        for x in G.neighbors(v): 

            #Obtenemos el peso de la arista
            if G.has_edge(v, x):
                peso_arista = peso(G, v, x)  
            else: 
                peso_arista = 0

            #Si encontramos una mejor distancia la cambiamos
            if distancias[x] > distancias[v] + peso_arista:
                distancias[x] = distancias[v] + peso_arista
                padre[x] = v 
                heapq.heappush(Q, (distancias[x], random.randint(1, 100000), x))
    #Devolvemos el padre
    return padre

def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """
    #Sacamos el padre usando la función dijkstra
    padre = dijkstra(G, peso, origen)

    #Comprobamos si el destino esta en el padre, sino lanzamos el error 
    if destino not in padre:
        raise ValueError("No existe camino entre origen y destino.")

    #Metemos en una lista el camino pero al revés, es decir desde el destino hasta el origen
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = padre.get(actual)
    #Devolvemos el camino pero invertido, para que sea desde el origen hasta el destino 
    return camino[::-1] 

def prim(G: nx.Graph, peso: Callable[[nx.Graph, object, object], float]) -> Dict[object, object]:
    """
    Calcula un Árbol Abarcador Mínimo para el grafo pesado usando el algoritmo de Prim.

    Args:
        G (nx.Graph): Grafo de NetworkX.
        peso (Callable[[nx.Graph, object, object], float]): Función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta.

    Returns:
        Dict[object, object]: Diccionario que indica, para cada vértice, qué vértice es su padre en el árbol abarcador mínimo.
    """
    #Inicializamos las variables
    padre = {}  
    coste_minimo = {} 
    visitado = {} 
    
    #Para cada nodo, no tiene padre, coste mínimo infinito, no visitado inicialmente
    for v in G.nodes:
        padre[v] = None 
        coste_minimo[v] = float('inf')  
        visitado[v] = False 
    
    #Empezamos desde un vértice cualquiera en este caso el primero por ejemplo
    origen = list(G.nodes)[0]
    #Coste desde el origen es 0
    coste_minimo[origen] = 0 
    
    #Inicializamos la cola de prioridad ordenada por coste mínimo
    Q = [(0, random.randint(1,100000), origen)]

    #Mientras que exista Q
    while Q:

        #Extraemos el vértice con el menor coste 
        coste_v, _, v = heapq.heappop(Q)

        #Recorremos los vecinos 
        for x in G.neighbors(v):
            #Obtenemos el peso 
            peso_arista = peso(G, v, x)
            
            #Si encontramos una mejor arista la cambiamos
            if peso_arista < coste_minimo[x]:
                coste_minimo[x] = peso_arista
                padre[x] = v 
                heapq.heappush(Q, (coste_minimo[x], random.randint(1, 100000), x))
    #Devolvemos el padre
    return padre       


def kruskal(G: nx.Graph, peso: Callable[[nx.Graph, object, object], float]) -> List[Tuple[object, object]]:
    """
    Calcula un Árbol Abarcador Mínimo para el grafo usando el algoritmo de Kruskal.

    Args:
        G (nx.Graph): Grafo de NetworkX.
        peso (Callable[[nx.Graph, object, object], float]): Función que recibe un grafo y dos vértices del grafo
                y devuelve el peso de la arista que los conecta.

    Returns:
        List[Tuple[object, object]]: Lista de los pares de vértices que forman las aristas del árbol abarcador mínimo.
    """
    #Creamos la lista de aristas y las ordenamos por peso
    aristas = [(u, v, peso(G, u, v)) for u, v in G.edges()]
    aristas.sort(key=lambda x: x[2])

    #Inicializamos padres y rangos
    padres = {node: node for node in G.nodes()}  
    rangos = {node: 0 for node in G.nodes()}  

    #Inicializamos la lista de aristas mínimas
    aristas_minimas = []

    #Iteramos las aristas
    for u, v, w in aristas:
        while padres[u] != u:
            u = padres[u]

        while padres[v] != v:
            v = padres[v]

        #Si los nodos no están en la misma componente
        if u != v:
            #Los añadimos a la lista de aristas mínimas
            aristas_minimas.append((u, v))
            
            #Los unimos
            if rangos[u] > rangos[v]:
                padres[v] = u
            elif rangos[u] < rangos[v]:
                padres[u] = v
            else:
                padres[v] = u
                rangos[u] += 1
    #Devolvemos la lista de aristas mínimas
    return aristas_minimas