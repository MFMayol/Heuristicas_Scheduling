# 🚀 Motor de Optimización de Scheduling y Logística

Este proyecto es un motor integral de resolución algorítmica para problemas clásicos de la **Investigación de Operaciones, Manufactura y Logística**. Utilizando Python puro, implementa soluciones basadas en heurísticas constructivas y metaheurísticas estocásticas para asignar recursos limitados de la forma más eficiente posible.

El código está modularizado en distintos archivos, cada uno enfocado en un entorno industrial particular.

---

## 🏭 1. Entornos de Máquina Única y Paralelas

### Single Machine ($1 || \dots$) - `single_machine.py`
El caso fundamental: agendar una fila de tareas en un único procesador.
* **SPT (Shortest Processing Time):** Minimiza el tiempo de completitud promedio y el flujo total.
* **EDD (Earliest Due Date):** Minimiza el retraso máximo (Lateness) respecto a la fecha de entrega prometida.

### Máquinas Paralelas Idénticas ($P_m || C_{max}$) - `heuristicas_simples.py`
Tareas que pueden ir a cualquier máquina, y todas operan a la misma velocidad.
* **LPT (Longest Processing Time):** Heurística clásica para minimizar el Makespan (tiempo total).
* **SPT:** Para minimizar el tiempo de espera promedio.
* **Multi-Start:** Metaheurística estocástica que baraja secuencias masivamente buscando el óptimo global.

### Máquinas Paralelas Uniformes ($Q_m || C_{max}$) - `uniform_parallel_machines.py`
Las máquinas son iguales, pero corren a diferentes velocidades (ej. una es el doble de rápida).
* **LPT Uniforme:** Adapta el LPT ponderando la duración de la tarea por el factor de velocidad de la máquina a la que se evalúa.

### Máquinas Paralelas No Relacionadas ($R_m || C_{max}$) - `unrelated_parallel_machines.py`
El tiempo que toma una tarea depende completamente de la máquina (ej. Windows vs Mac).
* **Min-Min:** Analiza toda la matriz de tiempos, busca la combinación Tarea-Máquina más rápida disponible, la asigna, y repite.

---

## ⛓️ 2. Restricciones Complejas

### Restricciones de Elegibilidad ($P_m | M_j | C_{max}$) - `scheduling_restricciones.py`
No todas las máquinas están capacitadas para hacer todas las tareas.
* **Greedy Híbrido con Prioridades:** Da prioridad absoluta a las tareas que son "cuello de botella" (las que tienen menos máquinas compatibles). Desempata usando LPT.
* **Multi-Start Restringido:** Genera combinaciones y filtra rápidamente las infactibles.

### Restricciones de Precedencia ($P_m | prec | C_{max}$) - `scheduling_precedencias.py`
Existen dependencias lógicas: la tarea B no puede empezar hasta que acabe la tarea A.
* **Ordenamiento Topológico + LPT:** Construye un grafo de dependencias para garantizar una secuencia lógica válida sin ciclos. Las máquinas esperan pasivamente a que las dependencias se liberen.
* **Multi-Start Topológico:** Aleatoriza las tareas siempre y cuando respeten su orden lógico jerárquico.

---

## ⚙️ 3. Entornos Shop (Manufactura en Cadena)

### Flowshop ($F_m || C_{max}$) - `flowshop.py`
Todos los trabajos deben pasar por todas las máquinas exactamente en el mismo orden (ej. Ensamblaje). El reto no es asignar, sino definir el orden de entrada.
* **Heurística NEH (Nawaz, Enscore, Ham):** Considerada la mejor constructiva para Flowshop. Ordena los trabajos por su peso total e itera probando cada trabajo nuevo en todas las posiciones de la secuencia parcial para encontrar el mejor encastre.
* **Multi-Start Flowshop.**

### Jobshop ($J_m || C_{max}$) - `jobshop.py`
El entorno más caótico: cada trabajo tiene su propia ruta y orden personalizado entre las máquinas.
* **Secuencia de Operaciones:** El motor decodifica listas de intenciones (ej. operar el Trabajo 1, luego el 2, luego el 1 de nuevo).
* **Heurística MWKR (Most Work Remaining):** Da prioridad en las máquinas a los trabajos a los que les falte la mayor cantidad de tiempo de procesamiento global.
* **Multi-Start Jobshop.**

---

## 🚚 4. Ruteo y Logística Física

### Problema de Ruteo de Vehículos (CVRP) - `VRP.py`
Flota de camiones con capacidad limitada que deben entregar mercancía a clientes en un plano 2D.
* **Vecino Más Cercano (Nearest Neighbor):** Construye la ruta de cada camión enviándolo siempre al cliente factible más próximo espacialmente (distancia euclidiana).
* **Multi-Start VRP:** Evalúa rutas aleatorias para esquivar los cruzamientos ineficientes de caminos típicos de las heurísticas constructivas.

---

## 💻 Cómo ejecutar el proyecto

Cada problema está encapsulado en su propio archivo Python y contiene datos simulados pre-cargados (mock data) en su bloque de ejecución principal. 

Para ejecutar cualquiera de los módulos y ver el reporte de KPIs y cronogramas, simplemente utiliza:

```bash
python nombre_del_archivo.py
```

*(Nota: El archivo `heuristicas_simples.py` puede integrarse para consumir datos externos desde un archivo `instancia.json`)*.

## 📊 Resumen de KPIs Calculados
Dependiendo del problema, los scripts analizan y muestran en terminal:
* **Makespan ($C_{max}$):** Tiempo transcurrido hasta que todo el sistema termina.
* **Tiempo de Flujo Promedio:** Velocidad media con la que las tareas fluyen por el sistema.
* **Lateness / Tardanza máxima:** Qué tan tarde se entregaron los pedidos.
* **Tiempo Ocioso:** Tiempo que las máquinas pasan vacías esperando tareas (o dependencias).
* **Distancia Total Recorrida:** Optimización de combustible (VRP).
* **Itinerarios (Líneas de Tiempo):** En qué minuto exacto empieza y termina cada operación.

```json
{
    "parametros": {
        "num_maquinas": 2
    },
    "tareas": [
        {"id": "T1", "duracion": 10},
        {"id": "T2", "duracion": 5},
        {"id": "T3", "duracion": 12},
        {"id": "T4", "duracion": 3}
    ]
}