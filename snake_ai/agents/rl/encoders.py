from typing import Tuple
from snake_ai.core.game_state import GameState


class StateEncoder:
    """
    Transforme l'état en 11 bits.
    Optimisé pour que l'IA comprenne le danger RELATIF (Devant, Droite, Gauche).
    """

    def encode(self, state: GameState) -> Tuple[int, ...]:
        head = state.head()
        food = state.food

        # 1. Directions (Boléens)
        d_l, d_r = state.direction == "LEFT", state.direction == "RIGHT"
        d_u, d_d = state.direction == "UP", state.direction == "DOWN"

        # 2. Points de vue (Radar)
        # On regarde à 1 case (Danger immédiat) et 2 cases (Danger proche)
        # p_f1 = self._get_relative_point(head, state.direction, 1)  # Devant 1
        p_f2 = self._get_relative_point(head, state.direction, 2)  # Devant 2

        state_vector = [
            # --- 1. DANGERS RELATIFS (4 bits) ---
            self._is_unsafe(
                self._get_relative_point(head, state.direction, 1, "STRAIGHT"), state
            ),
            self._is_unsafe(
                self._get_relative_point(head, state.direction, 1, "RIGHT"), state
            ),
            self._is_unsafe(
                self._get_relative_point(head, state.direction, 1, "LEFT"), state
            ),
            self._is_unsafe(p_f2, state),  # Danger à 2 cases devant (Anticipation)
            # --- 2. DIRECTION ACTUELLE (4 bits - One-hot) ---
            d_l,
            d_r,
            d_u,
            d_d,
            # --- 3. POSITION NOURRITURE (4 bits) ---
            food[0] < head[0],  # Food Left
            food[0] > head[0],  # Food Right
            food[1] < head[1],  # Food Up
            food[1] > head[1],  # Food Down
            # --- 4. ANALYSE SPATIALE (4 bits) ---
            # Le serpent est-il aligné horizontalement avec la pomme ?
            food[0] == head[0],
            # Le serpent est-il aligné verticalement avec la pomme ?
            food[1] == head[1],
            # Proximité immédiate (12ème bit original)
            (abs(head[0] - food[0]) + abs(head[1] - food[1])) == 1,
            # Le corps est-il long ? (Change la stratégie de virage)
            len(state.snake) > 10,
        ]

        return tuple(int(x) for x in state_vector)

    def _get_relative_point(self, head, direction, dist, turn="STRAIGHT"):
        """Calcule un point dans le futur selon la direction et un virage."""
        x, y = head
        # Traduction de la direction relative en absolue
        if turn == "STRAIGHT":
            if direction == "UP":
                return (x, y - dist)
            if direction == "DOWN":
                return (x, y + dist)
            if direction == "LEFT":
                return (x - dist, y)
            if direction == "RIGHT":
                return (x + dist, y)
        elif turn == "RIGHT":
            if direction == "UP":
                return (x + dist, y)
            if direction == "DOWN":
                return (x - dist, y)
            if direction == "LEFT":
                return (x, y - dist)
            if direction == "RIGHT":
                return (x, y + dist)
        elif turn == "LEFT":
            if direction == "UP":
                return (x - dist, y)
            if direction == "DOWN":
                return (x + dist, y)
            if direction == "LEFT":
                return (x, y + dist)
            if direction == "RIGHT":
                return (x, y - dist)
        return (x, y)

    def _is_unsafe(self, pt: Tuple[int, int], state: GameState) -> bool:
        x, y = pt
        if x < 0 or x >= state.grid_width or y < 0 or y >= state.grid_height:
            return True
        if pt in state.snake:
            return True
        return False
