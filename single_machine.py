from typing import List, Dict, Any

# ==========================================
# EVALUADOR DE SECUENCIA EN 1 MÁQUINA
# ==========================================
def _evaluar_secuencia(secuencia: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Procesa las tareas en orden secuencial en una única máquina.
    """
    tiempo_actual = 0
    historial = []
    lateness_max = 0
    suma_completitud = 0

    for tarea in secuencia:
        inicio = tiempo_actual
        fin = inicio + tarea['duracion']
        
        # El "Lateness" (Tardanza) ocurre si terminamos después de la fecha comprometida (due_date)
        due_date = tarea.get('due_date', float('inf'))
        lateness = max(0, fin - due_date)
        
        historial.append({
            'tarea': tarea['id'],
            'inicio': inicio,
            'fin': fin,
            'lateness': lateness
        })
        
        tiempo_actual = fin
        suma_completitud += fin
        if lateness > lateness_max:
            lateness_max = lateness

    return {
        'makespan': tiempo_actual,
        'tiempo_total_completitud': suma_completitud,
        'lateness_max': lateness_max,
        'historial_tareas': historial
    }

def resolver_spt(tareas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Minimiza el tiempo promedio de completitud (Shortest Processing Time)."""
    secuencia = sorted(tareas, key=lambda x: x['duracion'])
    return _evaluar_secuencia(secuencia)

def resolver_edd(tareas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Minimiza el retraso máximo (Earliest Due Date)."""
    secuencia = sorted(tareas, key=lambda x: x.get('due_date', float('inf')))
    return _evaluar_secuencia(secuencia)

if __name__ == "__main__":
    lista_tareas = [
        {"id": "T1", "duracion": 10, "due_date": 15},
        {"id": "T2", "duracion": 5, "due_date": 6},
        {"id": "T3", "duracion": 12, "due_date": 20},
        {"id": "T4", "duracion": 3, "due_date": 8}
    ]
    
    print("=== SINGLE MACHINE SCHEDULING ===")
    res_spt = resolver_spt(lista_tareas)
    print(f"SPT (Min Completitud) -> Tiempo de Flujo Total: {res_spt['tiempo_total_completitud']} | Lateness Max: {res_spt['lateness_max']}")
    res_edd = resolver_edd(lista_tareas)
    print(f"EDD (Min Lateness)    -> Tiempo de Flujo Total: {res_edd['tiempo_total_completitud']} | Lateness Max: {res_edd['lateness_max']}")