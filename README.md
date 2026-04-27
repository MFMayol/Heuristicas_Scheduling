# 🚀 Optimizador de Scheduling (Máquinas Paralelas Idénticas)

Este proyecto implementa un motor de resolución para el problema de **Programación de Tareas en Máquinas Paralelas Idénticas** ($P||C_{max}$), un desafío clásico en la investigación de operaciones y logística.

El sistema permite cargar una instancia de problemas mediante archivos JSON y resolverla utilizando diferentes enfoques algorítmicos, optimizando métricas de rendimiento operativo.

## 🧠 Heurísticas Implementadas

El código está diseñado bajo principios de programación modular y ofrece tres estrategias de resolución:

### 1. LPT (Longest Processing Time First)
* **Enfoque:** Greedy / Constructivo.
* **Objetivo:** Minimizar el **Makespan** ($C_{max}$).
* **Lógica:** Ordena las tareas de forma descendente por duración. Al asignar primero las tareas más largas a las máquinas disponibles, se reduce la probabilidad de que una tarea pesada extienda el tiempo total de operación al final del proceso.

### 2. SPT (Shortest Processing Time First)
* **Enfoque:** Greedy / Constructivo.
* **Objetivo:** Minimizar el **Tiempo de Flujo Promedio**.
* **Lógica:** Ordena las tareas de forma ascendente. Es la estrategia óptima para reducir el tiempo de espera promedio de los "clientes", permitiendo que las tareas rápidas se liberen de inmediato.

### 3. Multi-Start Randomized Search
* **Enfoque:** Metaheurística Estocástica.
* **Objetivo:** Exploración del espacio de soluciones para encontrar el **Óptimo Global**.
* **Lógica:** Genera múltiples permutaciones aleatorias de la lista de tareas y evalúa el desempeño de cada una. Esto permite escapar de los "óptimos locales" en los que suelen caer las heurísticas constructivas puras.

## 📁 Estructura del Archivo de Entrada (`instancia.json`)

El programa requiere un archivo JSON en el directorio raíz con el siguiente esquema:

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