import math

from world.game_state import GameState


def base_evaluation_function(state: GameState) -> float:
    """
    Retorna la evaluación base entregada para desarrollar el punto 4.

    Esta función no forma parte del código que debe modificar el estudiante y
    permite probar Minimax antes de desarrollar la heurística del punto 5.
    """
    if state.is_win():
        return 1000.0
    if state.is_lose():
        return -1000.0
    return float(state.get_score())


def evaluation_function(state: GameState) -> float:
    """
    Evalúa un estado desde la perspectiva del defensor MAX.

    Debe conservar las utilidades terminales de la evaluación base y diseñar
    una valoración no trivial para estados de corte. Minimax y alfa-beta usan
    esta misma función al comparar sus decisiones en el punto 5.

    Tips:
    - Los estados terminales ya se resuelven antes del bloque TODO; diseñe allí
      únicamente la valoración de estados no terminales.
    - Consulte state.defender_position, state.intruder_position,
      state.pending_terminals, state.get_score() y state.get_legal_actions(0).
    - state.layout.distance(start, goal) calcula y almacena en caché la distancia
      real por el mapa respetando los muros.
    - Maneje conjuntos vacíos y distancias infinitas, y mantenga todo estado no
      terminal estrictamente entre -1000 y +1000.
    """
    if state.is_win() or state.is_lose():
        return base_evaluation_function(state)

    # TODO: Add your code here
    pos_defensor = state.defender_position
    pos_intruso = state.intruder_position
    terminales = state.pending_terminals
    puntaje_base = state.get_score()
    
    min_dist_terminal = float("inf")
    for terminal in terminales:
      distancia = state.layout.distance(pos_defensor, terminal)
      if distancia < min_dist_terminal:
        min_dist_terminal = distancia
    dist_intruso = state.layout.distance(pos_defensor, pos_intruso)
    
    atraccion = 0
    if min_dist_terminal != float("inf"):
      atraccion = 10 / (min_dist_terminal + 1)
    repulsion = 0
    if dist_intruso <= 2:
      repulsion = 50 / (dist_intruso + 1)
      
    valor_heuristica = puntaje_base + atraccion - repulsion
    return max(-999, min(999, valor_heuristica))
