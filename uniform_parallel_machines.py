from typing import List, Dict, Any

def _asignar_tareas_uniformes(secuencia: List[Dict[str, Any]], maquinas_info: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Inicializamos las máquinas con su respectivo factor de velocidad
    maquinas = [{'id_maquina': m['id'], 'velocidad': m['velocidad'], 'tiempo_fin': 0, 'historial': []} for m in maquinas_info]
    
    for tarea in secuencia:
        mejor_maquina = None
        mejor_tiempo_fin = float('inf')
        
        # Buscamos qué máquina terminará esta tarea más temprano
        for m in maquinas:
            # TIEMPO REAL = TAREA BASE / VELOCIDAD
            tiempo_procesamiento_real = tarea['duracion_base'] / m['velocidad']
            posible_fin = m['tiempo_fin'] + tiempo_procesamiento_real
            
            if posible_fin < mejor_tiempo_fin:
                mejor_tiempo_fin = posible_fin
                mejor_maquina = m
                
        inicio = mejor_maquina['tiempo_fin']
        mejor_maquina['historial'].append({
            'tarea': tarea['id'],
            'inicio': round(inicio, 2),
            'fin': round(mejor_tiempo_fin, 2)
        })
        mejor_maquina['tiempo_fin'] = mejor_tiempo_fin
        
    makespan = max(m['tiempo_fin'] for m in maquinas)
    return {'makespan': round(makespan, 2), 'maquinas': maquinas}

def resolver_lpt_uniforme(tareas: List[Dict[str, Any]], maquinas_info: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Ordenamos LPT usando la duración base
    secuencia = sorted(tareas, key=lambda x: x['duracion_base'], reverse=True)
    return _asignar_tareas_uniformes(secuencia, maquinas_info)

if __name__ == "__main__":
    lista_tareas = [
        {"id": "T1", "duracion_base": 10},
        {"id": "T2", "duracion_base": 5},
        {"id": "T3", "duracion_base": 12},
        {"id": "T4", "duracion_base": 3}
    ]
    
    maquinas_disp = [
        {"id": "M1", "velocidad": 1.0}, # Máquina Normal
        {"id": "M2", "velocidad": 2.0}  # Máquina que procesa el doble de rápido
    ]
    
    res = resolver_lpt_uniforme(lista_tareas, maquinas_disp)
    print("=== UNIFORM PARALLEL MACHINES ===")
    print(f"Makespan: {res['makespan']}\n")
    for m in res['maquinas']:
        print(f"🏭 Máquina {m['id_maquina']} (v={m['velocidad']}): Fin en {round(m['tiempo_fin'], 2)}")
        for t in m['historial']:
            print(f"   ↳ {t['tarea']} ({t['inicio']} -> {t['fin']})")