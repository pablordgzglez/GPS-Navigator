# Sistema de Navegación GPS en Madrid utilizando Grafos y Datos Abiertos

Este proyecto implementa un sistema de navegación capaz de calcular rutas en la ciudad de Madrid utilizando datos oficiales del callejero y grafos construidos a partir de OpenStreetMap. El núcleo del proyecto consiste en aplicar algoritmos clásicos de teoría de grafos (Dijkstra, Prim y Kruskal) programados manualmente, y utilizarlos dentro de una aplicación tipo GPS.

El código está organizado en varios módulos que permiten descargar y procesar datos, construir el grafo de calles, buscar direcciones y calcular rutas óptimas según diferentes criterios.

## Estructura del proyecto

El repositorio contiene los siguientes archivos:

- **gps.py**  
  Script principal. Gestiona la interacción con el usuario, permite seleccionar direcciones y calcula rutas según los diferentes modos de navegación.

- **grafo_pesado.py**  
  Implementación manual de diferentes algoritmos de grafos 
  - Algoritmo de Dijkstra
  - Cálculo de caminos mínimos
  - Árbol abarcador mínimo con Prim
  - Árbol abarcador mínimo con Kruskal
  Incluye también utilidades para trabajar con grafos dirigidos y ponderados.

- **callejero.py**  
  Funciones para procesar el dataset oficial de direcciones del Ayuntamiento de Madrid, convertir coordenadas y asociar direcciones a nodos del grafo.

- **madrid.graphml**  
  Grafo de calles generado por OSMnx (si no existe, se genera automáticamente al ejecutar gps.py).

- **direcciones.csv**  
  Dataset del callejero oficial necesario para localizar direcciones.


## Requisitos

El proyecto utiliza las siguientes librerías de Python que pueden instalarse ejecutando el requirements_gps.txt:
-networkx
-osmnx
-pandas
-numpy
-matplotlib
