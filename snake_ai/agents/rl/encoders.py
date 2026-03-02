from typing import Tuple

# from snake_ai.engine.game import Direction, Point, SnakeGameAI
from snake_ai.core.game_state import GameState


class StateEncoder:
    """
    Transforme l'état complexe du SnakeGameAI en un tuple de 11 booléens (0 ou 1).
    Espace d'état : 2^11 = 2048 combinaisons possibles.
    """

    # def encode(self, game: SnakeGameAI) -> Tuple[int, ...]:
    def encode(self, state: GameState) -> Tuple[int, ...]:
        head = state.head()

        # Calcul des points adjacents (Haut, Bas, Gauche, Droite)
        point_l = (head[0] - 1, head[1])
        point_r = (head[0] + 1, head[1])
        point_u = (head[0], head[1] - 1)
        point_d = (head[0], head[1] + 1)

        # Points adjacents à la tête pour détecter les dangers
        # point_l = Point(head.x - settings.block_size, head.y)
        # point_r = Point(head.x + settings.block_size, head.y)
        # point_u = Point(head.x, head.y - settings.block_size)
        # point_d = Point(head.x, head.y + settings.block_size)

        # Vérification des directions actuelles
        dir_l = state.direction == "LEFT"
        dir_r = state.direction == "RIGHT"
        dir_u = state.direction == "UP"
        dir_d = state.direction == "DOWN"

        # Direction actuelle (One-hot encoding)
        # dir_l = game.direction == Direction.LEFT
        # dir_r = game.direction == Direction.RIGHT
        # dir_u = game.direction == Direction.UP
        # dir_d = game.direction == Direction.DOWN

        state_vector = [
            # 1. Danger immédiat (Tout droit, Droite, Gauche)
            (dir_r and state.is_collision(point_r))
            or (dir_l and state.is_collision(point_l))
            or (dir_u and state.is_collision(point_u))
            or (dir_d and state.is_collision(point_d)),
            (dir_u and state.is_collision(point_r))
            or (dir_d and state.is_collision(point_l))
            or (dir_l and state.is_collision(point_u))
            or (dir_r and state.is_collision(point_d)),
            (dir_d and state.is_collision(point_r))
            or (dir_u and state.is_collision(point_l))
            or (dir_r and state.is_collision(point_u))
            or (dir_l and state.is_collision(point_d)),
            # 2. Mouvement actuel
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            # 3. Position de la nourriture (Gauche, Droite, Haut, Bas)
            state.food[0] < head[0],  # food left
            state.food[0] > head[0],  # food right
            state.food[1] < head[1],  # food up
            state.food[1] > head[1],  # food down
        ]

        return tuple(int(x) for x in state_vector)
