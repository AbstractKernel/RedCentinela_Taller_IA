import math
import random

from optimization.problem import SmartGridOptimizationProblem
from optimization.result import Configuration, OptimizationResult


def configuration_score(
    problem: SmartGridOptimizationProblem, configuration: Configuration
) -> float:
    """
    Combina cobertura, redundancia y exposición en un puntaje a maximizar.

    Tips:
    - Use problem.score_components(configuration); ya retorna cobertura,
      redundancia y exposición en ese orden.
    """
    # TODO: Add your code here
    weight_vector = [1,-1,-1]
    components = problem.score_components(configuration)
    score = 0
    for i in range(len(weight_vector)):
        score = score + components[i]*weight_vector[i] # Producto punto para la ponderación de métricas en función de evaluación.
    return score
    
    


def hill_climbing(
    problem: SmartGridOptimizationProblem,
    initial_configuration: Configuration,
    max_iterations: int = 500,
) -> OptimizationResult:
    """
    Ejecuta ascenso de colina con mejora estricta.

    Debe examinar todos los vecinos, seleccionar el de mayor puntaje y
    conservar el orden entregado por el problema para desempatar. La búsqueda
    termina cuando no existe una mejora estricta o se alcanza el límite.

    Tips:
    - problem.neighbors(current) retorna vecinos válidos en el orden que debe
      usarse para desempatar.
    - Cada llamada a configuration_score(...) cuenta como una evaluación.
    - Inicialice los historiales con la configuración inicial y agregue solo las
      mejoras aceptadas antes de retornar el OptimizationResult.
    """
    # TODO: Add your code here
    
    #Inicialización de estado inicial
    index = 0
    current_state = initial_configuration 
    current_score = configuration_score(problem,initial_configuration)
    history = [initial_configuration]
    score_history = [current_score]
    evaluations = 1
    while True:
        
        neighborhood = problem.neighbors(current_state)
        candidate = 0
        scored_neighborhood = [] 
        
        #Busqueda de nodos en frontera con sus respectivos puntajes
        for neighbor in neighborhood:
            evaluations = evaluations + 1
            scored_neighborhood.append(configuration_score(problem,neighbor))
            
        #Se escoge el vecino con mayor puntaje, la función max e index retornan el máximo, en caso de empate se escoge el primer índice
        neighborhood_max_score = max(scored_neighborhood)
        candidate = scored_neighborhood.index(neighborhood_max_score)
        
        #Ascenso de colina con evaluación estricta, en caso de llegar a la iteración max_iterations (indexada como max_interations-1) retornar
        
        if neighborhood_max_score <= current_score or index >= max_iterations:
            return OptimizationResult(current_state,current_score,evaluations,index,history,score_history)
            
        #En caso de cumplir la mejora estricta, pasar a nuevo estado.
        current_state = neighborhood[candidate]
        current_score = neighborhood_max_score
        
        #Actualización del historial.
        history.append(current_state)
        score_history.append(current_score)
        
        #Aumento de índice
        index = index + 1
        
        


def cooling_schedule(initial_temperature: float, cooling_rate: float, iteration: int) -> float:
    """
    Retorna el programa geométrico T(t) = T0 * alpha**t.

    Esta función se invoca desde simulated_annealing en cada iteración.
    """
    # TODO: Add your code here
    if cooling_rate <= 0 or cooling_rate >= 1:
        raise ValueError("cooling_rate must be a value in the following interval: (0,1)")
    return initial_temperature * cooling_rate**iteration


def simulated_annealing(
    problem: SmartGridOptimizationProblem,
    initial_configuration: Configuration,
    initial_temperature: float = 20.0,
    cooling_rate: float = 0.97,
    max_iterations: int = 500,
    rng: random.Random | None = None,
) -> OptimizationResult:
    """
    Ejecuta recocido simulado para un problema de maximización.

    Debe proponer un vecino aleatorio por iteración, aceptar siempre las
    mejoras y aplicar exp(delta / temperature) en los demás casos. El estado
    actual y el mejor estado encontrado deben conservarse por separado.

    Tips:
    - Seleccione el candidato con rng.choice(problem.neighbors(current)) y use
      exclusivamente rng para conservar la reproducibilidad.
    - Obtenga la temperatura con cooling_schedule(...) y calcule la aceptación
      con delta = puntaje_candidato - puntaje_actual y math.exp(...).
    - Mantenga separados el estado actual y el mejor encontrado; registre el
      estado actual después de cada intento, incluso si se rechaza.
    - Detenga la ejecución cuando la temperatura alcance minimum_temperature.
    """
    rng = rng or random.Random()
    minimum_temperature = 1e-9

    # TODO: Add your code here
    current_state = initial_configuration
    current_score = configuration_score(problem,initial_configuration)
    evaluations = 1
    index = 0
    history = [current_state]
    score_history = [current_score]
    maximization_state = initial_configuration
    maximization_score = current_score

    while True:
               
        #T(index) = T_0 * \alpha^{index}. Donde \alpha \in (0,1).
        temperature = cooling_schedule(initial_temperature, cooling_rate, index) #En iteración 0 obtenemos la temperatura inicial puesto que T(0) = T_0 * 1
        
        if temperature < minimum_temperature or index >= max_iterations:
            return OptimizationResult(maximization_state, maximization_score,evaluations, index,history,score_history)
        
        neighborhood = problem.neighbors(current_state)
        candidate = rng.choice(neighborhood)
        candidate_score = configuration_score(problem,candidate)
        evaluations = evaluations + 1
        
        delta_e = candidate_score - current_score
        
        
        if delta_e > 0:
            current_state = candidate #El mejora estrictamente positiva siempre se acepta. El candidato se vuelve el estado actual.
            current_score = candidate_score
        elif rng.random() <= math.e**(delta_e/temperature):
            current_state = candidate #Se escoge el candidato con probabilidad e^{delta_E/T}
            current_score = candidate_score  

        #Óptimo histórico.
        if current_score > maximization_score:
            maximization_state = current_state 
            maximization_score = current_score
                    
        #Actualizar historial
        history.append(current_state)
        score_history.append(current_score)
            
        index = index + 1
        
        
            
            
        


def one_point_crossover(
    parent1: Configuration, parent2: Configuration, rng: random.Random
) -> tuple[Configuration, Configuration]:
    """
    Realiza un cruce de un punto y retorna dos descendientes.

    La reparación de la cantidad de módulos se realiza posteriormente.

    Tips:
    - Seleccione con rng un corte interior, entre las posiciones 1 y len-1.
    - Cada descendiente combina el prefijo de un padre con el sufijo del otro.
    - Retorne tuplas y no repare aquí los descendientes.
    """
    if len(parent1) != len(parent2):
        raise ValueError("Los padres deben tener la misma longitud")
    if len(parent1) < 2:
        return parent1, parent2
        
    

    # TODO: Add your code here
    raise NotImplementedError("Punto 3: implemente one_point_crossover")


def swap_mutation(
    individual: Configuration, mutation_probability: float, rng: random.Random
) -> Configuration:
    """
    Aplica mutación por intercambio con la probabilidad indicada.

    Cuando ocurre una mutación, intercambia un bit activo y uno inactivo para
    conservar la cantidad de módulos instalados.

    Tips:
    - Use rng.random() para decidir si se aplica la mutación.
    - Identifique por separado los índices activos e inactivos y seleccione uno
      de cada grupo con rng.choice(...).
    - Si alguno de los dos grupos está vacío, no hay un intercambio posible.
    - Retorne una tupla nueva; no modifique el individuo recibido.
    """
    # TODO: Add your code here
    raise NotImplementedError("Punto 3: implemente swap_mutation")


def genetic_algorithm(
    problem: SmartGridOptimizationProblem,
    population_size: int = 40,
    generations: int = 100,
    mutation_probability: float = 0.05,
    elite_size: int = 2,
    rng: random.Random | None = None,
) -> OptimizationResult:
    """
    Ejecuta un algoritmo genético generacional.

    Debe integrar la población inicial, la selección por torneo, el cruce, la
    reparación, la mutación y el elitismo entregados por el proyecto. Retorna
    el mejor individuo encontrado durante toda la ejecución.

    Tips:
    - Use problem.initial_population(...), problem.tournament_select(...) y
      problem.repair_configuration(...) para las operaciones ya entregadas.
    - Aplique one_point_crossover(...) antes de reparar y swap_mutation(...)
      después de la reparación.
    - Conserve los mejores individuos por elitismo y registre en los historiales
      el mejor global de cada generación.
    """
    rng = rng or random.Random()
    if population_size < 2:
        raise ValueError("La población debe tener al menos dos individuos")
    if generations < 0:
        raise ValueError("El número de generaciones no puede ser negativo")
    if not 0.0 <= mutation_probability <= 1.0:
        raise ValueError("La probabilidad de mutación debe estar entre 0 y 1")
    if not 0 <= elite_size <= population_size:
        raise ValueError("elite_size debe estar entre 0 y population_size")

    # TODO: Add your code here
    raise NotImplementedError("Punto 3: implemente genetic_algorithm")
