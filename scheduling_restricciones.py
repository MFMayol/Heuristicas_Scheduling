import random
import copy
from typing import List, Dict, Any, Optional

# ==========================================
# FUNCIÓN CORE DE ASIGNACIÓN
# ==========================================
def _asignar_tareas_con_restricciones(secuencia_tareas: List[Dict[str, Any]], num_maquinas: int) -> Optional[Dict[str, Any]]:
    """
    Asigna una lista de tareas a las máquinas, respetando las restricciones de compatibilidad.
    Asigna cada tarea a la máquina eligible que se desocupe más temprano.

    Args:
        secuencia_tareas: Lista de tareas donde cada una incluye 'id', 'duracion' y 'compatibles' (lista de IDs de máquinas).
        num_maquinas: Cantidad total de máquinas en el sistema.

    Returns:
        Dict con el itinerario y KPIs, o None si la secuencia genera una infactibilidad.
    """
    # Inicializamos las máquinas (IDs del 0 al num_maquinas-1)
    maquinas = [{'id_maquina': i, 'tiempo_fin': 0, 'historial_tareas': []} for i in range(num_maquinas)]
    
    for tarea in secuencia_tareas:
        # 1. Filtrar las máquinas que son capaces de procesar esta tarea
        maquinas_elegibles = [m for m in maquinas if m['id_maquina'] in tarea['compatibles']]
        
        # Si no hay ninguna máquina elegible disponible o configurada, la solución es infactible
        if not maquinas_elegibles:
            return None
        
        # 2. De las elegibles, escoger la que se libere más temprano
        maquina_asignada = min(maquinas_elegibles, key=lambda m: m['tiempo_fin'])
        
        # 3. Asignar y actualizar tiempos
        inicio = maquina_asignada['tiempo_fin']
        fin = inicio + tarea['duracion']
        
        maquina_asignada['historial_tareas'].append({
            'tarea': tarea['id'],
            'inicio': inicio,
            'fin': fin
        })
        
        maquina_asignada['tiempo_fin'] = fin

    # Calcular KPIs
    makespan = max(m['tiempo_fin'] for m in maquinas)
    
    return {
        'makespan': makespan,
        'itinerario_maquinas': maquinas
    }

# ==========================================
# HEURÍSTICAS DE RESOLUCIÓN
# ==========================================
def resolver_greedy_con_prioridades(tareas: List[Dict[str, Any]], num_maquinas: int) -> Optional[Dict[str, Any]]:
    """
    Estrategia Constructiva Híbrida:
    Ordena las tareas primero por lo "restrictivas" que son (las que tienen menos máquinas 
    compatibles van primero) y luego por duración (LPT) como criterio de desempate.
    """
    # Ordenamos primero por len(compatibles) [Ascendente] y luego por duracion [Descendente]
    tareas_ordenadas = sorted(tareas, key=lambda x: (len(x['compatibles']), -x['duracion']))
    
    return _asignar_tareas_con_restricciones(tareas_ordenadas, num_maquinas)

def resolver_multi_start_restringido(tareas: List[Dict[str, Any]], num_maquinas: int, iteraciones: int = 2000) -> Optional[Dict[str, Any]]:
    """
    Metaheurística Estocástica:
    Prueba múltiples secuencias aleatorias. Es muy útil en problemas con restricciones 
    porque los enfoques puramente constructivos suelen atascarse.
    """
    mejor_solucion = None
    mejor_makespan = float('inf')
    
    for _ in range(iteraciones):
        tareas_aleatorias = tareas.copy()
        random.shuffle(tareas_aleatorias)
        
        solucion_actual = _asignar_tareas_con_restricciones(tareas_aleatorias, num_maquinas)
        
        # Descartar si es infactible
        if solucion_actual is None:
            continue
            
        if solucion_actual['makespan'] < mejor_makespan:
            mejor_makespan = solucion_actual['makespan']
            mejor_solucion = copy.deepcopy(solucion_actual)
            
    return mejor_solucion

# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # 1. Datos simulados con RESTRICCIONES de máquinas
    # Las máquinas se identifican con IDs 0, 1 y 2.
    lista_tareas = [
        {"id": "T1", "duracion": 10, "compatibles": [0, 1, 2]}, # Muy flexible
        {"id": "T2", "duracion": 5,  "compatibles": [1]},       # SÓLO puede ir a M1 (Cuello de botella)
        {"id": "T3", "duracion": 12, "compatibles": [0, 2]},    # M0 o M2
        {"id": "T4", "duracion": 3,  "compatibles": [0]},       # SÓLO puede ir a M0
        {"id": "T5", "duracion": 8,  "compatibles": [2]},       # SÓLO puede ir a M2
        {"id": "T6", "duracion": 6,  "compatibles": [1, 2]}     # M1 o M2
    ]
    num_maquinas_disp = 3

    # 2. Ejecutar modelos
    print("⏳ Resolviendo el problema con restricciones...")
    resultado_greedy = resolver_greedy_con_prioridades(lista_tareas, num_maquinas_disp)
    resultado_estocastico = resolver_multi_start_restringido(lista_tareas, num_maquinas_disp, iteraciones=10000)

    # 3. Analizar y mostrar resultados
    print("\n=== COMPARATIVA: SCHEDULING CON RESTRICCIONES ===")
    print("-" * 60)
    
    if not resultado_greedy and not resultado_estocastico:
        print("❌ Error: No se pudo encontrar una solución factible con las restricciones actuales.")
    else:
        mk_greedy = resultado_greedy['makespan'] if resultado_greedy else 'Infactible'
        mk_est = resultado_estocastico['makespan'] if resultado_estocastico else 'Infactible'
        
        print(f"{'Modelo':<25} | {'Makespan (Tiempo Total)':<25}")
        print("-" * 60)
        print(f"{'Greedy con Prioridad':<25} | {mk_greedy:<25}")
        print(f"{'Multi-Start Estocástico':<25} | {mk_est:<25}")
        print("-" * 60)

        # Determinar ganador
        ganador = None
        if resultado_greedy and resultado_estocastico:
            ganador = resultado_estocastico if mk_est < mk_greedy else resultado_greedy
            nombre = "Multi-Start" if mk_est < mk_greedy else "Greedy con Prioridad"
        elif resultado_estocastico:
            ganador, nombre = resultado_estocastico, "Multi-Start"
        else:
            ganador, nombre = resultado_greedy, "Greedy con Prioridad"

        # Mostrar desglose del ganador
        print(f"\n🏆 Ganador: {nombre} (Makespan: {ganador['makespan']})")
        print("\nItinerario Detallado de Máquinas:")
        
        for maquina in ganador['itinerario_maquinas']:
            id_m = maquina['id_maquina']
            t_fin = maquina['tiempo_fin']
            tareas_str = ", ".join([f"{t['tarea']}({t['inicio']}-{t['fin']})" for t in maquina['historial_tareas']])
            
            if not tareas_str:
                tareas_str = "--- Sin tareas asignadas ---"
                
            print(f"🏭 Máquina {id_m} | Tiempo Ocupado: {t_fin:<3}")
            print(f"   ↳ Timeline: {tareas_str}")
