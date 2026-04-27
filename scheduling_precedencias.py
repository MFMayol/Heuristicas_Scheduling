import random
import copy
from typing import List, Dict, Any, Optional

# ==========================================
# GENERADOR DE ORDENAMIENTO LÓGICO
# ==========================================
def generar_secuencia_valida(tareas: List[Dict[str, Any]], estrategia: str = "LPT") -> Optional[List[Dict[str, Any]]]:
    """
    Genera un orden de ejecución válido respetando las dependencias (Ordenamiento Topológico).
    
    Args:
        tareas: Lista de tareas con atributos 'id', 'duracion' y 'dependencias' (lista de IDs).
        estrategia: "LPT" para priorizar las más largas, o "RANDOM" para metaheurísticas.
    """
    pendientes = copy.deepcopy(tareas)
    completadas = set()
    secuencia_final = []
    
    while pendientes:
        # 1. Buscar todas las tareas que ya tienen sus dependencias cumplidas
        disponibles = []
        for tarea in pendientes:
            dependencias = tarea.get('dependencias', [])
            # Si todas sus dependencias están en el set 'completadas', se puede ejecutar
            if all(dep in completadas for dep in dependencias):
                disponibles.append(tarea)
                
        # Si quedan tareas pero ninguna está disponible, hay un ciclo infinito o un error lógico
        if not disponibles:
            print("⚠️ Error: Se detectó un ciclo infinito o una dependencia imposible.")
            return None
            
        # 2. Elegir cuál tarea disponible agendar a continuación
        if estrategia == "LPT":
            # Desempate LPT (las más largas primero para evitar cuellos de botella al final)
            disponibles.sort(key=lambda x: x['duracion'], reverse=True)
            tarea_elegida = disponibles[0]
        else:
            # RANDOM para el Multi-Start
            tarea_elegida = random.choice(disponibles)
            
        # 3. Registrar la tarea como completada lógicamente
        secuencia_final.append(tarea_elegida)
        completadas.add(tarea_elegida['id'])
        
        # Remover de la lista de pendientes
        pendientes = [t for t in pendientes if t['id'] != tarea_elegida['id']]
        
    return secuencia_final

# ==========================================
# FUNCIÓN CORE DE ASIGNACIÓN A MÁQUINAS
# ==========================================
def _asignar_tareas_con_precedencias(secuencia_valida: List[Dict[str, Any]], num_maquinas: int) -> Dict[str, Any]:
    """
    Asigna las tareas a las máquinas tomando en cuenta en qué minuto terminaron sus dependencias.
    """
    maquinas = [{'id_maquina': i, 'tiempo_fin': 0, 'historial_tareas': []} for i in range(num_maquinas)]
    tiempos_fin_tareas = {} # Diccionario para consultar a qué hora exacta terminó cada tarea
    
    for tarea in secuencia_valida:
        id_tarea = tarea['id']
        
        # 1. ¿A qué hora está permitida empezar esta tarea? (Tiempo de Liberación)
        # Es el máximo tiempo de finalización de todas sus dependencias.
        tiempo_liberacion = 0
        for dep in tarea.get('dependencias', []):
            tiempo_liberacion = max(tiempo_liberacion, tiempos_fin_tareas[dep])
            
        # 2. Buscar la máquina ideal. 
        # Buscamos la máquina que nos permita iniciar la tarea lo MÁS PRONTO posible.
        mejor_maquina = None
        mejor_inicio_real = float('inf')
        
        for m in maquinas:
            # La máquina puede empezar la tarea cuando esté libre y además la tarea esté liberada
            inicio_posible = max(m['tiempo_fin'], tiempo_liberacion)
            
            if inicio_posible < mejor_inicio_real:
                mejor_inicio_real = inicio_posible
                mejor_maquina = m
                
        # 3. Asignar en la máquina encontrada
        inicio = mejor_inicio_real
        fin = inicio + tarea['duracion']
        
        mejor_maquina['historial_tareas'].append({
            'tarea': id_tarea,
            'inicio': inicio,
            'fin': fin
        })
        
        mejor_maquina['tiempo_fin'] = fin
        tiempos_fin_tareas[id_tarea] = fin # Guardar hora de fin para las futuras dependencias

    makespan = max(m['tiempo_fin'] for m in maquinas)
    
    return {
        'makespan': makespan,
        'itinerario_maquinas': maquinas
    }

# ==========================================
# HEURÍSTICAS DE RESOLUCIÓN
# ==========================================
def resolver_greedy_dependencias(tareas: List[Dict[str, Any]], num_maquinas: int) -> Optional[Dict[str, Any]]:
    """Resuelve usando ordenamiento topológico determinista priorizando LPT."""
    secuencia = generar_secuencia_valida(tareas, estrategia="LPT")
    if not secuencia:
        return None
    return _asignar_tareas_con_precedencias(secuencia, num_maquinas)

def resolver_multi_start_dependencias(tareas: List[Dict[str, Any]], num_maquinas: int, iteraciones: int = 2000) -> Optional[Dict[str, Any]]:
    """Prueba múltiples secuencias topológicas aleatorias buscando el óptimo global."""
    mejor_solucion = None
    mejor_makespan = float('inf')
    
    for _ in range(iteraciones):
        secuencia_aleatoria = generar_secuencia_valida(tareas, estrategia="RANDOM")
        if not secuencia_aleatoria:
            return None # Falla rápido si el generador detecta un error de datos
            
        solucion_actual = _asignar_tareas_con_precedencias(secuencia_aleatoria, num_maquinas)
        
        if solucion_actual['makespan'] < mejor_makespan:
            mejor_makespan = solucion_actual['makespan']
            mejor_solucion = copy.deepcopy(solucion_actual)
            
    return mejor_solucion

# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # 1. Datos simulados con DEPENDENCIAS LÓGICAS
    lista_tareas = [
        {"id": "T1", "duracion": 4, "dependencias": []},         # Puede empezar de inmediato
        {"id": "T2", "duracion": 2, "dependencias": ["T1"]},     # Espera a T1
        {"id": "T3", "duracion": 7, "dependencias": []},         # Puede empezar de inmediato
        {"id": "T4", "duracion": 5, "dependencias": ["T1"]},     # Espera a T1
        {"id": "T5", "duracion": 1, "dependencias": ["T2", "T3"]}, # Necesita T2 y T3
        {"id": "T6", "duracion": 3, "dependencias": ["T4", "T5"]}  # La última en la cadena
    ]
    num_maquinas_disp = 2

    # 2. Ejecutar modelos
    print("⏳ Resolviendo el problema de precedencias...")
    resultado_greedy = resolver_greedy_dependencias(lista_tareas, num_maquinas_disp)
    resultado_estocastico = resolver_multi_start_dependencias(lista_tareas, num_maquinas_disp, iteraciones=5000)

    # 3. Analizar y mostrar resultados
    print("\n=== COMPARATIVA: SCHEDULING CON PRECEDENCIAS ===")
    print("-" * 65)
    
    if not resultado_greedy:
        print("❌ Error: Ciclo lógico o falla estructural en las dependencias.")
    else:
        mk_greedy = resultado_greedy['makespan']
        mk_est = resultado_estocastico['makespan']
        
        print(f"{'Modelo':<25} | {'Makespan (Tiempo Total)':<25}")
        print("-" * 65)
        print(f"{'Topológico + LPT':<25} | {mk_greedy:<25}")
        print(f"{'Multi-Start Estocástico':<25} | {mk_est:<25}")
        print("-" * 65)

        # Determinar ganador y mostrar detalles
        ganador = resultado_estocastico if mk_est < mk_greedy else resultado_greedy
        nombre = "Multi-Start Estocástico" if mk_est < mk_greedy else "Topológico + LPT"

        print(f"\n🏆 Ganador: {nombre} (Makespan: {ganador['makespan']})")
        print("\nItinerario Detallado (Atención a los espacios en blanco por esperas):")
        
        for maquina in ganador['itinerario_maquinas']:
            id_m = maquina['id_maquina']
            t_fin = maquina['tiempo_fin']
            tareas_str = " -> ".join([f"[{t['tarea']}: {t['inicio']} a {t['fin']}]" for t in maquina['historial_tareas']])
            print(f"🏭 Máquina {id_m} | Línea de tiempo: {tareas_str}")