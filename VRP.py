import math
import random
import copy
from typing import List, Dict, Any, Optional

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def calcular_distancia(nodo1: Dict[str, Any], nodo2: Dict[str, Any]) -> float:
    """Calcula la distancia Euclidiana entre dos nodos (puntos en un plano 2D)."""
    return math.hypot(nodo1['x'] - nodo2['x'], nodo1['y'] - nodo2['y'])

def _evaluar_secuencia_vrp(secuencia_clientes: List[Dict[str, Any]], 
                           deposito: Dict[str, Any], 
                           num_vehiculos: int, 
                           capacidad_max: int) -> Optional[Dict[str, Any]]:
    """
    Función core que construye las rutas basándose en una secuencia de clientes.
    Va llenando el vehículo actual hasta que se agota su capacidad, luego pasa al siguiente.
    
    Args:
        secuencia_clientes: Lista de clientes en el orden en que se intentarán visitar.
        deposito: Diccionario con las coordenadas del punto de partida/llegada.
        num_vehiculos: Flota disponible.
        capacidad_max: Capacidad máxima de carga por vehículo.
        
    Returns:
        Dict con los KPIs y el itinerario, o None si la secuencia viola las restricciones.
    """
    # Inicializar el estado de la flota
    flota = [{'id_vehiculo': i, 'ruta': [deposito], 'carga_actual': 0, 'distancia_recorrida': 0.0} 
             for i in range(num_vehiculos)]
    
    indice_vehiculo = 0
    
    # Proceso de ruteo
    for cliente in secuencia_clientes:
        vehiculo = flota[indice_vehiculo]
        
        # Si el cliente no cabe, cerramos la ruta actual y pasamos al siguiente vehículo
        if vehiculo['carga_actual'] + cliente['demanda'] > capacidad_max:
            indice_vehiculo += 1
            if indice_vehiculo >= num_vehiculos:
                return None  # Solución infactible: nos quedamos sin vehículos
            vehiculo = flota[indice_vehiculo]
            
        # Asignar cliente al vehículo actual
        vehiculo['ruta'].append(cliente)
        vehiculo['carga_actual'] += cliente['demanda']

    # Calcular KPIs finales (cerrar rutas volviendo al depósito)
    distancia_total = 0.0
    
    for vehiculo in flota:
        vehiculo['ruta'].append(deposito) # Todo vehículo debe volver a la base
        distancia_ruta = 0.0
        
        # Calcular la distancia paso a paso en la ruta de este vehículo
        for i in range(len(vehiculo['ruta']) - 1):
            nodo_actual = vehiculo['ruta'][i]
            siguiente_nodo = vehiculo['ruta'][i+1]
            distancia_ruta += calcular_distancia(nodo_actual, siguiente_nodo)
            
        vehiculo['distancia_recorrida'] = round(distancia_ruta, 2)
        distancia_total += distancia_ruta

    # El Makespan en ruteo es la ruta más larga (determina la hora de fin de toda la operación)
    makespan = max(v['distancia_recorrida'] for v in flota)

    return {
        'distancia_total': round(distancia_total, 2),
        'makespan': round(makespan, 2),
        'itinerario_flota': flota
    }

# ==========================================
# MODELOS DE SOLUCIÓN
# ==========================================
def resolver_con_vecino_mas_cercano(clientes: List[Dict[str, Any]], 
                                    deposito: Dict[str, Any], 
                                    num_vehiculos: int, 
                                    capacidad_max: int) -> Optional[Dict[str, Any]]:
    """
    Heurística Constructiva: Nearest Neighbor (Vecino Más Cercano).
    Equivalente al LPT/SPT en Scheduling. Construye la ruta eligiendo siempre 
    el cliente más cercano al nodo actual que aún tenga capacidad disponible.
    """
    clientes_no_visitados = clientes.copy()
    flota = [{'id_vehiculo': i, 'ruta': [deposito], 'carga_actual': 0, 'distancia_recorrida': 0.0} 
             for i in range(num_vehiculos)]
    
    indice_vehiculo = 0
    distancia_total = 0.0
    
    while clientes_no_visitados:
        vehiculo = flota[indice_vehiculo]
        nodo_actual = vehiculo['ruta'][-1]
        
        # Filtrar clientes que caben en el camión
        clientes_viables = [c for c in clientes_no_visitados if vehiculo['carga_actual'] + c['demanda'] <= capacidad_max]
        
        if not clientes_viables:
            # Si nadie cabe, cerramos este camión y abrimos el siguiente
            vehiculo['ruta'].append(deposito)
            indice_vehiculo += 1
            if indice_vehiculo >= num_vehiculos:
                return None # Flota insuficiente
            continue
            
        # Elegir el más cercano
        cliente_mas_cercano = min(clientes_viables, key=lambda c: calcular_distancia(nodo_actual, c))
        
        # Actualizar estado
        vehiculo['ruta'].append(cliente_mas_cercano)
        vehiculo['carga_actual'] += cliente_mas_cercano['demanda']
        clientes_no_visitados.remove(cliente_mas_cercano)

    # Cerrar las rutas de los vehículos que quedaron a medias
    for vehiculo in flota:
        if vehiculo['ruta'][-1]['id'] != 'DEPOSITO':
            vehiculo['ruta'].append(deposito)
            
        # Calcular distancias
        dist = sum(calcular_distancia(vehiculo['ruta'][i], vehiculo['ruta'][i+1]) for i in range(len(vehiculo['ruta'])-1))
        vehiculo['distancia_recorrida'] = round(dist, 2)
        distancia_total += dist

    return {
        'distancia_total': round(distancia_total, 2),
        'makespan': max(v['distancia_recorrida'] for v in flota),
        'itinerario_flota': flota
    }

def resolver_con_multi_start(clientes: List[Dict[str, Any]], 
                             deposito: Dict[str, Any], 
                             num_vehiculos: int, 
                             capacidad_max: int, 
                             iteraciones: int = 5000) -> Optional[Dict[str, Any]]:
    """
    Metaheurística estocástica. 
    Baraja aleatoriamente el orden de los clientes y los evalúa para escapar de óptimos locales.
    Busca minimizar la Distancia Total.
    """
    mejor_solucion = None
    mejor_distancia = float('inf')
    
    for _ in range(iteraciones):
        clientes_aleatorios = clientes.copy()
        random.shuffle(clientes_aleatorios)
        
        solucion_actual = _evaluar_secuencia_vrp(clientes_aleatorios, deposito, num_vehiculos, capacidad_max)
        
        # Descartamos soluciones que superan la capacidad de la flota
        if solucion_actual is None:
            continue
            
        if solucion_actual['distancia_total'] < mejor_distancia:
            mejor_distancia = solucion_actual['distancia_total']
            mejor_solucion = copy.deepcopy(solucion_actual)

    return mejor_solucion

# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # 1. Datos simulados de Logística (X, Y y Demanda en cajas/pallets)
    deposito_central = {"id": "DEPOSITO", "x": 50, "y": 50, "demanda": 0}
    
    lista_clientes = [
        {"id": "C1", "x": 10, "y": 20, "demanda": 5},
        {"id": "C2", "x": 30, "y": 80, "demanda": 8},
        {"id": "C3", "x": 90, "y": 10, "demanda": 3},
        {"id": "C4", "x": 80, "y": 90, "demanda": 6},
        {"id": "C5", "x": 50, "y": 60, "demanda": 4},
        {"id": "C6", "x": 20, "y": 40, "demanda": 7}
    ]
    
    flota_disponible = 2
    capacidad_camion = 20 # Cajas máximas por camión

    demanda_total = sum(c['demanda'] for c in lista_clientes)
    
    # 2. Ejecutar modelos
    resultado_nn = resolver_con_vecino_mas_cercano(lista_clientes, deposito_central, flota_disponible, capacidad_camion)
    resultado_estocastico = resolver_con_multi_start(lista_clientes, deposito_central, flota_disponible, capacidad_camion, iteraciones=10000)

    # 3. Mostrar comparativa extendida
    print("\n=== THE OPTIMAL PARTNER: COMPARATIVA DE RUTEOS (CVRP) ===")
    print("-" * 75)
    print(f"{'Métrica':<25} | {'Vecino Más Cercano':<20} | {'Multi-Start Estocástico':<20}")
    print("-" * 75)
    
    # Validar que se encontraron soluciones (que la capacidad alcanzó)
    if not resultado_nn or not resultado_estocastico:
        print("Error: No hay suficientes vehículos para satisfacer la demanda.")
    else:
        # Extraer variables
        dist_nn, dist_est = resultado_nn['distancia_total'], resultado_estocastico['distancia_total']
        mk_nn, mk_est = resultado_nn['makespan'], resultado_estocastico['makespan']
        
        print(f"{'Distancia Total':<25} | {dist_nn:<20} | {dist_est:<20}")
        print(f"{'Makespan (Ruta Larga)':<25} | {mk_nn:<20} | {mk_est:<20}")
        
        # Calcular utilización de capacidad
        capacidad_total = flota_disponible * capacidad_camion
        utilizacion_porcentaje = round((demanda_total / capacidad_total) * 100, 2)
        print(f"{'Utilización de Flota':<25} | {f'{utilizacion_porcentaje}%':<20} | {f'{utilizacion_porcentaje}%':<20}")
        print("-" * 75)

        # 4. Conclusiones y detalle de rutas del ganador
        print("\n=== ANÁLISIS DEL MEJOR MODELO ===")
        mejor_modelo = resultado_estocastico if dist_est < dist_nn else resultado_nn
        nombre_ganador = "Multi-Start" if dist_est < dist_nn else "Vecino Más Cercano"
        
        print(f"🏆 Ganador: {nombre_ganador} (Distancia Total: {mejor_modelo['distancia_total']})")
        print("\nItinerario Detallado:")
        
        for vehiculo in mejor_modelo['itinerario_flota']:
            ruta_str = " -> ".join([nodo['id'] for nodo in vehiculo['ruta']])
            print(f"🚚 Vehículo {vehiculo['id_vehiculo']} | Carga: {vehiculo['carga_actual']}/{capacidad_camion} | Dist: {vehiculo['distancia_recorrida']}")
            print(f"   Ruta: {ruta_str}")