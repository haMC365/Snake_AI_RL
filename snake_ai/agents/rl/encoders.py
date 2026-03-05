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

        # 1. Définir les points adjacents
        p_left = (head[0] - 1, head[1])
        p_right = (head[0] + 1, head[1])
        p_up = (head[0], head[1] - 1)
        p_down = (head[0], head[1] + 1)

        # 2. Directions actuelles
        d_l = state.direction == "LEFT"
        d_r = state.direction == "RIGHT"
        d_u = state.direction == "UP"
        d_d = state.direction == "DOWN"

        # 3. Calcul du 12ème bit : La pomme est-elle adjacente ?
        # (Distance de Manhattan == 1)
        is_food_adjacent = (abs(head[0] - food[0]) + abs(head[1] - food[1])) == 1

        state_vector = [
            # --- 1. DANGER IMMÉDIAT (Relatif à la direction actuelle) ---
            # Danger devant
            (d_r and self._is_unsafe(p_right, state))
            or (d_l and self._is_unsafe(p_left, state))
            or (d_u and self._is_unsafe(p_up, state))
            or (d_d and self._is_unsafe(p_down, state)),
            # Danger à droite
            (d_u and self._is_unsafe(p_right, state))
            or (d_d and self._is_unsafe(p_left, state))
            or (d_l and self._is_unsafe(p_up, state))
            or (d_r and self._is_unsafe(p_down, state)),
            # Danger à gauche
            (d_d and self._is_unsafe(p_right, state))
            or (d_u and self._is_unsafe(p_left, state))
            or (d_r and self._is_unsafe(p_up, state))
            or (d_l and self._is_unsafe(p_down, state)),
            # --- 2. DIRECTION ACTUELLE (One-hot) ---
            d_l,
            d_r,
            d_u,
            d_d,
            # --- 3. POSITION NOURRITURE ---
            state.food[0] < head[0],  # Food Left
            state.food[0] > head[0],  # Food Right
            state.food[1] < head[1],  # Food Up
            state.food[1] > head[1],  # Food Down
            # --- Le 12ème BIT : proximité promme ---
            is_food_adjacent,
        ]

        return tuple(int(x) for x in state_vector)

    def _is_unsafe(self, pt: Tuple[int, int], state: GameState) -> bool:
        """Détection stricte: Murs + Tout le corps"""
        x, y = pt
        # Mur
        if x < 0 or x >= state.grid_width or y < 0 or y >= state.grid_height:
            return True
        # Corps (on ignore le dernier segment de la queue car il va bouger)
        if pt in state.snake:
            return True
        return False
