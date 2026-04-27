from typing import List, Dict, Any

def resolver_min_min_unrelated(tiempos_matriz: Dict[str, Dict[str, float]], maquinas_ids: List[str]) -> Dict[str, Any]:
    """
    Heurística constructiva Min-Min: 
    Busca de entre todas las tareas pendientes, aquella que se termine de ejecutar
    lo más pronto posible en alguna de las máquinas.
    """
    tareas_pendientes = list(tiempos_matriz.keys())
    maquinas = [{'id_maquina': m, 'tiempo_fin': 0, 'historial': []} for m in maquinas_ids]
    
    while tareas_pendientes:
        mejor_tarea = None
        mejor_maquina = None
        mejor_tiempo_fin = float('inf')
        
        # Evaluar qué combinación Tarea-Máquina es la que termina más rápido
        for tarea_id in tareas_pendientes:
            for m in maquinas:
                tiempo_proc_especifico = tiempos_matriz[tarea_id][m['id_maquina']]
                posible_fin = m['tiempo_fin'] + tiempo_proc_especifico
                
                if posible_fin < mejor_tiempo_fin:
                    mejor_tiempo_fin = posible_fin
                    mejor_maquina = m
                    mejor_tarea = tarea_id
                    
        # Asignar la combinación ganadora
        inicio = mejor_maquina['tiempo_fin']
        mejor_maquina['historial'].append({
            'tarea': mejor_tarea,
            'inicio': round(inicio, 2),
            'fin': round(mejor_tiempo_fin, 2)
        })
        mejor_maquina['tiempo_fin'] = mejor_tiempo_fin
        tareas_pendientes.remove(mejor_tarea)
        
    makespan = max(m['tiempo_fin'] for m in maquinas)
    return {'makespan': round(makespan, 2), 'maquinas': maquinas}

if __name__ == "__main__":
    maquinas = ["M1_Windows", "M2_Mac"]
    
    # Matriz de tiempos: Cuánto tarda cada tarea dependiendo del SO de la máquina
    tiempos = {
        "Compilar_App": {"M1_Windows": 15, "M2_Mac": 5},
        "Render_Video": {"M1_Windows": 8,  "M2_Mac": 20},
        "Escribir_Doc": {"M1_Windows": 10, "M2_Mac": 10},
        "Test_Sistema": {"M1_Windows": 12, "M2_Mac": 8}
    }
    
    res = resolver_min_min_unrelated(tiempos, maquinas)
    print("=== UNRELATED PARALLEL MACHINES ===")
    print(f"Makespan (Min-Min): {res['makespan']}\n")
    for m in res['maquinas']:
        print(f"🏭 Máquina {m['id_maquina']}: Tiempo Ocupado: {round(m['tiempo_fin'], 2)}")
        for t in m['historial']:
            print(f"   ↳ {t['tarea']} ({t['inicio']} -> {t['fin']})")