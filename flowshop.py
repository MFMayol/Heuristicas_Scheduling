import random
import copy
from typing import List, Dict, Any, Tuple

# ==========================================
# EVALUADOR DE SECUENCIA EN FLOWSHOP
# ==========================================
def evaluar_flowshop(secuencia: List[str], tiempos: Dict[str, List[float]], num_maquinas: int) -> Dict[str, Any]:
    """
    Calcula el tiempo de finalización (Makespan) de una secuencia específica de tareas
    en un entorno Flowshop (todas las tareas pasan por las máquinas en el mismo orden).
    
    Args:
        secuencia: Lista de IDs de tareas ordenadas según se van a procesar.
        tiempos: Diccionario con los tiempos de procesamiento de cada tarea por máquina.
        num_maquinas: Cantidad total de máquinas en la línea.
    """
    n = len(secuencia)
    # Matriz para guardar el tiempo en que la tarea 'i' termina en la máquina 'm'
    matriz_fin = [[0.0] * num_maquinas for _ in range(n)]
    historial = {m: [] for m in range(num_maquinas)}

    for i in range(n):
        tarea = secuencia[i]
        for m in range(num_maquinas):
            tiempo_proc = tiempos[tarea][m]
            
            # Caso 1: Primera tarea en la primera máquina
            if i == 0 and m == 0:
                inicio = 0.0
            # Caso 2: Primera tarea en máquinas subsecuentes (espera a la máquina anterior)
            elif i == 0:
                inicio = matriz_fin[i][m-1]
            # Caso 3: Tareas subsecuentes en la primera máquina (espera a la tarea anterior)
            elif m == 0:
                inicio = matriz_fin[i-1][m]
            # Caso 4: Caso general (debe esperar a que la máquina se libere Y a que la tarea termine en la máquina previa)
            else:
                inicio = max(matriz_fin[i-1][m], matriz_fin[i][m-1])
                
            fin = inicio + tiempo_proc
            matriz_fin[i][m] = fin
            
            historial[m].append({
                'tarea': tarea,
                'inicio': round(inicio, 2),
                'fin': round(fin, 2)
            })

    return {
        'makespan': matriz_fin[-1][-1] if n > 0 else 0,
        'secuencia': secuencia,
        'itinerario': historial
    }

# ==========================================
# HEURÍSTICAS DE RESOLUCIÓN
# ==========================================
def resolver_con_neh(tareas: List[str], tiempos: Dict[str, List[float]], num_maquinas: int) -> Dict[str, Any]:
    """
    Heurística NEH (Nawaz, Enscore, Ham):
    1. Ordena las tareas de mayor a menor según la suma de sus tiempos de procesamiento.
    2. Toma la primera tarea.
    3. Iterativamente toma la siguiente tarea y prueba insertarla en todas las posiciones
       posibles de la secuencia actual, guardando la que genere el menor Makespan parcial.
    """
    if not tareas:
        return evaluar_flowshop([], tiempos, num_maquinas)
        
    # 1. Ordenamiento inicial por suma total de tiempos
    tareas_ordenadas = sorted(tareas, key=lambda t: sum(tiempos[t]), reverse=True)
    
    # 2. Inicializar con la primera tarea
    secuencia_actual = [tareas_ordenadas[0]]
    
    # 3. Inserciones iterativas
    for tarea in tareas_ordenadas[1:]:
        mejor_makespan = float('inf')
        mejor_secuencia = []
        
        # Probar la tarea en todas las posiciones posibles (de 0 a len(secuencia_actual))
        for pos in range(len(secuencia_actual) + 1):
            secuencia_candidata = secuencia_actual[:pos] + [tarea] + secuencia_actual[pos:]
            evaluacion = evaluar_flowshop(secuencia_candidata, tiempos, num_maquinas)
            
            if evaluacion['makespan'] < mejor_makespan:
                mejor_makespan = evaluacion['makespan']
                mejor_secuencia = secuencia_candidata
                
        secuencia_actual = mejor_secuencia
        
    return evaluar_flowshop(secuencia_actual, tiempos, num_maquinas)

def resolver_multi_start_flowshop(tareas: List[str], tiempos: Dict[str, List[float]], num_maquinas: int, iteraciones: int = 2000) -> Dict[str, Any]:
    """
    Metaheurística Estocástica: Prueba miles de secuencias aleatorias y se queda con la mejor.
    """
    mejor_solucion = None
    mejor_makespan = float('inf')
    
    for _ in range(iteraciones):
        secuencia_aleatoria = tareas.copy()
        random.shuffle(secuencia_aleatoria)
        
        evaluacion = evaluar_flowshop(secuencia_aleatoria, tiempos, num_maquinas)
        
        if evaluacion['makespan'] < mejor_makespan:
            mejor_makespan = evaluacion['makespan']
            mejor_solucion = evaluacion
            
    return mejor_solucion

# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # 1. Datos simulados de Flowshop
    # Las tareas pasan por las máquinas en orden: M0 -> M1 -> M2
    tareas_lista = ["J1", "J2", "J3", "J4", "J5"]
    num_maq = 3
    
    # Tiempos de procesamiento: "ID_Tarea": [tiempo_M0, tiempo_M1, tiempo_M2]
    tiempos_proc = {
        "J1": [5, 4, 3],
        "J2": [3, 5, 2],
        "J3": [6, 2, 5],
        "J4": [1, 7, 4],
        "J5": [4, 1, 6]
    }

    # 2. Ejecutar modelos
    print("⏳ Resolviendo el problema de Flowshop...")
    resultado_neh = resolver_con_neh(tareas_lista, tiempos_proc, num_maq)
    resultado_estocastico = resolver_multi_start_flowshop(tareas_lista, tiempos_proc, num_maq, iteraciones=2000)

    # 3. Analizar y mostrar resultados
    print("\n=== COMPARATIVA: LÍNEA DE ENSAMBLAJE (FLOWSHOP) ===")
    print("-" * 65)
    print(f"{'Modelo':<25} | {'Makespan':<15} | {'Secuencia Elegida'}")
    print("-" * 65)
    print(f"{'Heurística NEH':<25} | {resultado_neh['makespan']:<15} | {' -> '.join(resultado_neh['secuencia'])}")
    print(f"{'Multi-Start Estocástico':<25} | {resultado_estocastico['makespan']:<15} | {' -> '.join(resultado_estocastico['secuencia'])}")
    print("-" * 65)
    
    # Detalle de la mejor opción
    ganador = resultado_neh if resultado_neh['makespan'] <= resultado_estocastico['makespan'] else resultado_estocastico
    nombre = "Heurística NEH" if resultado_neh['makespan'] <= resultado_estocastico['makespan'] else "Multi-Start"
    
    print(f"\n🏆 Ganador: {nombre}")
    for m in range(num_maq):
        historial = " ".join([f"[{t['tarea']}: {t['inicio']}->{t['fin']}]" for t in ganador['itinerario'][m]])
        print(f"🏭 Máquina {m} | {historial}")
