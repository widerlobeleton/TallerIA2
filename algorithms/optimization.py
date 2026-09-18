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
    cobertura,redundancia,exposicion = problem.score_components(configuration)
    return cobertura- redundancia-exposicion


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
    actual = initial_configuration
    score_actual = configuration_score(problem, actual)

    evaluar = 1
    rondas = 0
    history = [actual]
    buscar = True

    while rondas < max_iterations and buscar:
        vecinos = problem.neighbors(actual)

        if not vecinos:
            buscar = False
        else:
            best_neighbor = actual
            best_neighbor_score = float("-inf")

            for neighbor in vecinos:
                score = configuration_score(problem, neighbor)
                evaluar += 1
                if score > best_neighbor_score:
                    best_neighbor_score = score
                    best_neighbor = neighbor

            rondas += 1

            if best_neighbor_score > score_actual:
                actual = best_neighbor
                score_actual = best_neighbor_score
                history.append(actual)
            else:
                buscar = False

    return OptimizationResult(
        best_configuration=actual,
        best_score=score_actual,
        evaluations=evaluar,
        iterations=rondas,
        history=history,
    )


def cooling_schedule(initial_temperature: float, cooling_rate: float, iteration: int) -> float:
    """
    Retorna el programa geométrico T(t) = T0 * alpha**t.

    Esta función se invoca desde simulated_annealing en cada iteración.
    """
    # TODO: Add your code here
    return initial_temperature * (cooling_rate**iteration)


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
    actual = initial_configuration
    score_actual = configuration_score(problem, actual)

    best_configuration = actual
    best_score = score_actual

    evaluar = 1
    rondas = 0
    history = [actual]
    buscar = True

    while rondas < max_iterations and buscar:
        temperatura = cooling_schedule(initial_temperature, cooling_rate, rondas)
        if temperatura < minimum_temperature:
            buscar = False
        else:
            vecinos = problem.neighbors(actual)
            if not vecinos:
                buscar = False
            else:
                candidato = rng.choice(vecinos)
                score_candidato = configuration_score(problem, candidato)
                evaluar += 1
                delta = score_candidato - score_actual
                aceptar = False
                if delta > 0:
                    aceptar = True
                else:
                    probabilidad = math.exp(delta / temperatura)
                    if rng.random() < probabilidad:
                        aceptar = True
                if aceptar:
                    actual = candidato
                    score_actual = score_candidato
                    if score_actual > best_score:
                        best_configuration = actual
                        best_score = score_actual
                history.append(actual)
                rondas += 1
    return OptimizationResult(
        best_configuration=best_configuration,
        best_score=best_score,
        evaluations=evaluar,
        iterations=rondas,
        history=history,
    )

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
    cut_point = rng.randint(1, len(parent1) -1)
    child1 = parent1[:cut_point] + parent2[cut_point:]
    child2 = parent2[:cut_point] + parent1[cut_point:]
    tupla = child1, child2
    return tupla


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
    mutation_prob = rng.random()
    if mutation_prob < mutation_probability:
        cut = rng.randint(0, len(individual) -1)
        lista0 = []
        lista1 = []
        i = 0
        for ADN in individual:
            if ADN == 0:
                lista0.append(i)
            else:
                lista1.append(i)
            i += 1
        if lista1 == [] or lista0 == []:
            return individual
        rng1 = rng.choice(lista0)
        rng2 = rng.choice(lista1)
        rng1_copy = rng1
        temp = list(individual)
        temp[rng1] = individual[rng2]
        temp[rng2] = individual[rng1_copy]
        return tuple(temp)
    return individual
            

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
    mejor_de_todos = None
    mejor_puntaje = float("-inf")
    historial_mejores = []
    population = problem.initial_population(population_size, rng)
    while generations > 0:
        generations -= 1
        population.sort(key = lambda ind: configuration_score(problem, ind), reverse = True)
        mejor_local = population[0]
        mejor_puntaje_local = configuration_score(problem, mejor_local)
        if mejor_de_todos is None or mejor_puntaje < mejor_puntaje_local:
            mejor_de_todos = mejor_local
            mejor_puntaje = mejor_puntaje_local
        historial_mejores.append(mejor_puntaje)
        nueva_poblacion = population[:elite_size]
        while len(nueva_poblacion) < population_size:
            parent1 = problem.tournament_select(population, rng)
            parent2 = problem.tournament_select(population, rng)
            child1, child2 = one_point_crossover(parent1, parent2, rng)
            child1 = problem.repair_configuration(child1, rng)
            child2 = problem.repair_configuration(child2, rng)
            child1 = swap_mutation(child1, mutation_probability, rng)
            child2 = swap_mutation(child2, mutation_probability, rng)
            nueva_poblacion.append(child1)
            if len(nueva_poblacion) < population_size:
                nueva_poblacion.append(child2)
        population = nueva_poblacion

            
    return OptimizationResult(configuration = mejor_de_todos, score = mejor_puntaje, evaluation = len(historial_mejores), iterations = len(historial_mejores), history = historial_mejores)
