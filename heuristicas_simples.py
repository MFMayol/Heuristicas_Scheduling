import json
from typing import List, Dict, Any
import random
import copy

def _asignar_tareas_a_maquinas(tareas_ordenadas: List[Dict[str, Any]], num_maquinas: int) -> Dict[str, Any]:
    """
    Función auxiliar (core) que asigna una lista de tareas ordenadas a las máquinas disponibles.
    Utiliza una lógica greedy: asigna la siguiente tarea a la máquina que se desocupe primero.

    Args:
        tareas_ordenadas (List[Dict[str, Any]]): Lista de diccionarios con las tareas ya ordenadas.
            Se espera que cada diccionario contenga las llaves 'id' y 'duracion'.
        num_maquinas (int): Cantidad de máquinas en paralelo disponibles.

    Returns:
        Dict[str, Any]: Un diccionario con los KPIs del modelo y el detalle del itinerario.
            - 'makespan' (int): Tiempo total hasta que la última máquina se apaga.
            - 'tiempo_promedio_flujo' (float): Tiempo promedio de finalización de las tareas.
            - 'itinerario_maquinas' (List[Dict]): Detalle de las tareas asignadas a cada máquina.
    """
    # Inicializar el estado de las máquinas
    maquinas = [{'id_maquina': i, 'tiempo_fin': 0, 'historial_tareas': []} for i in range(num_maquinas)]
    tiempos_finalizacion = []

    # Proceso de asignación
    for tarea in tareas_ordenadas:
        # Encontrar la máquina que se libera más temprano
        maquina_libre = min(maquinas, key=lambda m: m['tiempo_fin'])
        
        inicio = maquina_libre['tiempo_fin']
        fin = inicio + tarea['duracion']
        
        # Registrar la asignación
        maquina_libre['historial_tareas'].append({
            'tarea': tarea['id'],
            'inicio': inicio,
            'fin': fin
        })
        
        # Actualizar contadores
        maquina_libre['tiempo_fin'] = fin
        tiempos_finalizacion.append(fin)

    # Calcular KPIs
    makespan = max(m['tiempo_fin'] for m in maquinas)
    tiempo_prom = sum(tiempos_finalizacion) / len(tiempos_finalizacion) if tiempos_finalizacion else 0.0

    return {
        'makespan': makespan,
        'tiempo_promedio_flujo': tiempo_prom,
        'itinerario_maquinas': maquinas
    }

def resolver_con_lpt(tareas: List[Dict[str, Any]], num_maquinas: int) -> Dict[str, Any]:
    """
    Resuelve el problema de scheduling usando la heurística LPT (Longest Processing Time first).
    Ideal para minimizar el Makespan (tiempo total de la operación).

    Args:
        tareas (List[Dict[str, Any]]): Lista cruda de tareas con sus duraciones.
        num_maquinas (int): Número de máquinas disponibles.

    Returns:
        Dict[str, Any]: Resultados de la asignación y KPIs.
    """
    # LPT requiere ordenar de mayor a menor duración
    tareas_lpt = sorted(tareas, key=lambda x: x['duracion'], reverse=True)
    return _asignar_tareas_a_maquinas(tareas_lpt, num_maquinas)

def resolver_con_spt(tareas: List[Dict[str, Any]], num_maquinas: int) -> Dict[str, Any]:
    """
    Resuelve el problema de scheduling usando la heurística SPT (Shortest Processing Time first).
    Ideal para minimizar el tiempo de espera promedio (Average Flow Time) de los clientes.

    Args:
        tareas (List[Dict[str, Any]]): Lista cruda de tareas con sus duraciones.
        num_maquinas (int): Número de máquinas disponibles.

    Returns:
        Dict[str, Any]: Resultados de la asignación y KPIs.
    """
    # SPT requiere ordenar de menor a mayor duración
    tareas_spt = sorted(tareas, key=lambda x: x['duracion'], reverse=False)
    return _asignar_tareas_a_maquinas(tareas_spt, num_maquinas)




def resolver_con_multi_start(tareas: List[Dict[str, Any]], num_maquinas: int, iteraciones: int = 1000) -> Dict[str, Any]:
    """
    Resuelve el problema de scheduling usando una heurística estocástica de múltiples inicios.
    Explora el espacio de soluciones evaluando miles de permutaciones aleatorias para escapar 
    de los óptimos locales que generan las heurísticas constructivas puras.

    Args:
        tareas (List[Dict[str, Any]]): Lista cruda de tareas con sus duraciones.
        num_maquinas (int): Número de máquinas disponibles.
        iteraciones (int, optional): Cantidad de escenarios aleatorios a simular. Por defecto 1000.

    Returns:
        Dict[str, Any]: El mejor resultado de asignación encontrado en todas las iteraciones.
    """
    mejor_solucion = None
    mejor_makespan = float('inf') # Inicializamos con "infinito" para que cualquier valor lo mejore
    
    # Bucle de exploración
    for _ in range(iteraciones):
        # 1. Hacemos una copia profunda (deepcopy) o superficial para no alterar la lista original
        tareas_aleatorias = tareas.copy()
        
        # 2. Barajamos las tareas en un orden aleatorio
        random.shuffle(tareas_aleatorias)
        
        # 3. Evaluamos este orden usando nuestro módulo core (¡Reusabilidad al máximo!)
        solucion_actual = _asignar_tareas_a_maquinas(tareas_aleatorias, num_maquinas)
        
        # 4. Si encontramos un Makespan más pequeño, guardamos este itinerario como el nuevo campeón
        if solucion_actual['makespan'] < mejor_makespan:
            mejor_makespan = solucion_actual['makespan']
            # Hacemos una copia del diccionario ganador para no perderlo en la siguiente vuelta
            mejor_solucion = copy.deepcopy(solucion_actual)

    return mejor_solucion

    # Función auxiliar para calcular utilización media de la planta
def calcular_utilizacion(makespan):
    return (tiempo_total_procesamiento / (makespan * num_maquinas_disp)) * 100 if makespan > 0 else 0


# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL (Actualizado)
# ==========================================
if __name__ == "__main__":
    # 1. Datos simulados (Puedes usar tu json.load aquí)
    lista_tareas = [
        {"id": "T1", "duracion": 4}, {"id": "T2", "duracion": 2},
        {"id": "T3", "duracion": 7}, {"id": "T4", "duracion": 5},
        {"id": "T5", "duracion": 1}, {"id": "T6", "duracion": 3}
    ]
    num_maquinas_disp = 2

    # Calcular tiempo total de procesamiento para métricas extra (Utilización y Ocio)
    tiempo_total_procesamiento = sum(t['duracion'] for t in lista_tareas)

    # 2. Ejecutar modelos
    resultado_lpt = resolver_con_lpt(lista_tareas, num_maquinas_disp)
    resultado_spt = resolver_con_spt(lista_tareas, num_maquinas_disp)
    
    # Ejecutamos 5000 iteraciones aleatorias buscando vencer al LPT
    resultado_estocastico = resolver_con_multi_start(lista_tareas, num_maquinas_disp, iteraciones=5000)


    # 3. Mostrar comparativa extendida
    print("=== COMPARATIVA DE HEURÍSTICAS Y MÉTRICAS ===")
    print("-" * 70)
    print(f"{'Métrica':<25} | {'LPT':<12} | {'SPT':<12} | {'Estocástico':<12}")
    print("-" * 70)
    
    # Extraer variables para la tabla
    mk_lpt, mk_spt, mk_est = resultado_lpt['makespan'], resultado_spt['makespan'], resultado_estocastico['makespan']
    tf_lpt = round(resultado_lpt['tiempo_promedio_flujo'], 2)
    tf_spt = round(resultado_spt['tiempo_promedio_flujo'], 2)
    tf_est = round(resultado_estocastico['tiempo_promedio_flujo'], 2)
    
    # Imprimir Makespan
    print(f"{'Makespan (Total)':<25} | {mk_lpt:<12} | {mk_spt:<12} | {mk_est:<12}")
    
    # Imprimir Tiempo Promedio de Flujo
    print(f"{'Tiempo Prom. de Flujo':<25} | {tf_lpt:<12} | {tf_spt:<12} | {tf_est:<12}")

    # Imprimir Utilización de máquinas (%)
    ut_lpt = round(calcular_utilizacion(mk_lpt), 2)
    ut_spt = round(calcular_utilizacion(mk_spt), 2)
    ut_est = round(calcular_utilizacion(mk_est), 2)
    print(f"{'Utilización Media (%)':<25} | {f'{ut_lpt}%':<12} | {f'{ut_spt}%':<12} | {f'{ut_est}%':<12}")
    
    # Imprimir Tiempo ocioso total (Idle time)
    # Fórmula: (Makespan * N° Máquinas) - Suma de todas las duraciones
    id_lpt = (mk_lpt * num_maquinas_disp) - tiempo_total_procesamiento
    id_spt = (mk_spt * num_maquinas_disp) - tiempo_total_procesamiento
    id_est = (mk_est * num_maquinas_disp) - tiempo_total_procesamiento
    print(f"{'Tiempo Ocioso Total':<25} | {id_lpt:<12} | {id_spt:<12} | {id_est:<12}")
    print("-" * 70)
    
    # 4. Conclusiones
    print("\n=== ANÁLISIS DE RESULTADOS ===")
    if mk_est < mk_lpt:
        print("🏆 ¡ÉXITO! La heurística estocástica logró encontrar un mejor Makespan que LPT.")
    else:
        print("⚖️ EMPATE EN MAKESPAN. LPT ya había encontrado un valor excelente para esta instancia.")
        
    if tf_spt < tf_lpt and tf_spt < tf_est:
        print("⚡ SPT demuestra ser el rey minimizando el Tiempo Promedio de Flujo (ideal para despachar rápido).")