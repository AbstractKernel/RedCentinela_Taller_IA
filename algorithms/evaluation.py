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
    layout = state.layout
    defender = state.defender_position
    intruder = state.intruder_position
    pending = state.pending_terminals

    cap = float(layout.height + layout.width)

    def dist(a, b) -> float:
        d = layout.distance(a, b)
        return cap if math.isinf(d) else min(float(d), cap)

    # puntaje
    value = state.get_score()

    # terminales pendientes
    if pending:
        distances = sorted(dist(defender, terminal) for terminal in pending)
        value -= 20.0 * len(pending)
        value -= 4.0 * distances[0]
        if len(distances) > 1:
            value -= 1.0 * sum(distances[1:]) / (len(distances) - 1)

    # distancia entre el intruso y el defensor
    gap = dist(intruder, defender)
    if gap <= 1:
        value -= 100.0
    else:
        value += 1.0 * min(gap, 10.0)

    # moverse según legal actions
    value += 3.0 * len(state.get_legal_actions(0))

    return max(-999.0, min(999.0, value))
    
