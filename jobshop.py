import random
import copy
from typing import List, Dict, Any

# ==========================================
# EVALUADOR DE SECUENCIA EN JOBSHOP
# ==========================================
def evaluar_jobshop(secuencia_operaciones: List[str], trabajos: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Decodifica una secuencia de operaciones y calcula el Makespan en un Jobshop.
    Una secuencia válida contiene el ID del trabajo tantas veces como operaciones tenga.
    Ej: ["J1", "J2", "J1"] significa: 1ra op de J1, 1ra op de J2, 2da op de J1.
    """
    # Estado actual de en qué operación va cada trabajo
    progreso_trabajo = {j: 0 for j in trabajos}
    # En qué minuto exacto se desocupa cada trabajo
    tiempo_libre_trabajo = {j: 0.0 for j in trabajos}
    
    # Máquinas (se detectan dinámicamente según lo que pidan los trabajos)
    tiempo_libre_maquina = {}
    historial_maquinas = {}
    
    for j_id in secuencia_operaciones:
        op_idx = progreso_trabajo[j_id]
        operacion = trabajos[j_id][op_idx]
        
        maq = operacion['maquina']
        dur = operacion['duracion']
        
        if maq not in tiempo_libre_maquina:
            tiempo_libre_maquina[maq] = 0.0
            historial_maquinas[maq] = []
            
        # El inicio real es cuando TANTO la máquina COMO el trabajo están libres
        inicio = max(tiempo_libre_maquina[maq], tiempo_libre_trabajo[j_id])
        fin = inicio + dur
        
        # Actualizar los "relojes"
        tiempo_libre_maquina[maq] = fin
        tiempo_libre_trabajo[j_id] = fin
        progreso_trabajo[j_id] += 1
        
        historial_maquinas[maq].append({
            'trabajo': j_id,
            'op_idx': op_idx + 1, # +1 para que sea legible por humanos (Op 1, Op 2...)
            'inicio': inicio,
            'fin': fin
        })
        
    makespan = max(tiempo_libre_maquina.values()) if tiempo_libre_maquina else 0
    
    return {
        'makespan': makespan,
        'itinerario': historial_maquinas
    }

# ==========================================
# HEURÍSTICAS DE RESOLUCIÓN
# ==========================================
def resolver_mwkr(trabajos: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Heurística MWKR (Most Work Remaining):
    Construye la secuencia dando prioridad siempre al trabajo que tiene 
    la mayor cantidad de tiempo de procesamiento restante total.
    """
    # Calcular el tiempo total requerido por cada trabajo al inicio
    trabajo_restante = {j: sum(op['duracion'] for op in ops) for j, ops in trabajos.items()}
    progreso = {j: 0 for j in trabajos}
    
    secuencia = []
    total_operaciones = sum(len(ops) for ops in trabajos.values())
    
    for _ in range(total_operaciones):
        # Filtrar solo los trabajos que no han terminado todas sus operaciones
        disponibles = [j for j in trabajos if progreso[j] < len(trabajos[j])]
        
        # Elegir el que tenga mayor trabajo restante (desempate por ID)
        elegido = max(disponibles, key=lambda j: (trabajo_restante[j], j))
        
        secuencia.append(elegido)
        
        # Actualizar progreso y restar el tiempo de la operación que acabamos de agendar
        dur_op_actual = trabajos[elegido][progreso[elegido]]['duracion']
        trabajo_restante[elegido] -= dur_op_actual
        progreso[elegido] += 1
        
    return evaluar_jobshop(secuencia, trabajos)

def resolver_multi_start_jobshop(trabajos: Dict[str, List[Dict[str, Any]]], iteraciones: int = 2000) -> Dict[str, Any]:
    """
    Metaheurística Estocástica: 
    Genera secuencias válidas barajando aleatoriamente el orden de las operaciones.
    """
    mejor_solucion = None
    mejor_makespan = float('inf')
    
    # Crear la "baraja" base. Ej si J1 tiene 3 ops y J2 tiene 2: [J1, J1, J1, J2, J2]
    secuencia_base = []
    for j, ops in trabajos.items():
        secuencia_base.extend([j] * len(ops))
        
    for _ in range(iteraciones):
        secuencia_aleatoria = secuencia_base.copy()
        random.shuffle(secuencia_aleatoria)
        
        evaluacion = evaluar_jobshop(secuencia_aleatoria, trabajos)
        
        if evaluacion['makespan'] < mejor_makespan:
            mejor_makespan = evaluacion['makespan']
            mejor_solucion = evaluacion
            
    return mejor_solucion

# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # 1. Datos simulados de Jobshop
    # Nota: Cada trabajo sigue una ruta de máquinas completamente diferente
    datos_trabajos = {
        "J1": [{"maquina": "Torno", "duracion": 3}, {"maquina": "Fresa", "duracion": 2}, {"maquina": "Pintura", "duracion": 2}],
        "J2": [{"maquina": "Torno", "duracion": 2}, {"maquina": "Pintura", "duracion": 1}, {"maquina": "Fresa", "duracion": 4}],
        "J3": [{"maquina": "Fresa", "duracion": 4}, {"maquina": "Pintura", "duracion": 3}]
    }

    # 2. Ejecutar modelos
    print("⏳ Resolviendo el problema de Jobshop...")
    resultado_mwkr = resolver_mwkr(datos_trabajos)
    resultado_estocastico = resolver_multi_start_jobshop(datos_trabajos, iteraciones=5000)

    # 3. Analizar y mostrar resultados
    print("\n=== COMPARATIVA: TALLER DE TRABAJOS (JOBSHOP) ===")
    print("-" * 60)
    print(f"Heurística MWKR (Most Work Remaining) : Makespan {resultado_mwkr['makespan']}")
    print(f"Multi-Start Estocástico (5000 iters)  : Makespan {resultado_estocastico['makespan']}")
    print("-" * 60)
    
    # Determinar ganador
    ganador = resultado_mwkr if resultado_mwkr['makespan'] <= resultado_estocastico['makespan'] else resultado_estocastico
    nombre = "Heurística MWKR" if resultado_mwkr['makespan'] <= resultado_estocastico['makespan'] else "Multi-Start"
    
    print(f"\n🏆 Ganador: {nombre}\n")
    print("Itinerario Detallado por Máquina (Ordenado cronológicamente):")
    
    maquinas_ordenadas = sorted(ganador['itinerario'].keys())
    for m in maquinas_ordenadas:
        # Ordenamos las tareas de esta máquina según a qué hora iniciaron
        historial = sorted(ganador['itinerario'][m], key=lambda x: x['inicio'])
        historial_str = " -> ".join([f"[{op['trabajo']} (Op.{op['op_idx']}): {op['inicio']} a {op['fin']}]" for op in historial])
        print(f"🏭 Máquina: {m:<10} | Línea de Tiempo: {historial_str}")