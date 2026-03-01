from typing import Tuple
from snake_ai.engine.game import Direction, Point, SnakeGameAI


class StateEncoder:
    """
    Transforme l'état complexe du SnakeGameAI en un tuple de 11 booléens (0 ou 1).
    Espace d'état : 2^11 = 2048 combinaisons possibles.
    """

    def encode(self, game: SnakeGameAI) -> Tuple[int, ...]:
        head = game.head

        # Points adjacents à la tête pour détecter les dangers
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        # Direction actuelle (One-hot encoding)
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # 1. DANGER DEVANT (1 bit)
            (dir_r and game.is_collision(point_r))
            or (dir_l and game.is_collision(point_l))
            or (dir_u and game.is_collision(point_u))
            or (dir_d and game.is_collision(point_d)),
            # 2. DANGER À DROITE (1 bit) - Relatif à l'orientation actuelle
            (dir_u and game.is_collision(point_r))
            or (dir_d and game.is_collision(point_l))
            or (dir_l and game.is_collision(point_u))
            or (dir_r and game.is_collision(point_d)),
            # 3. DANGER À GAUCHE (1 bit) - Relatif à l'orientation actuelle
            (dir_d and game.is_collision(point_r))
            or (dir_u and game.is_collision(point_l))
            or (dir_r and game.is_collision(point_u))
            or (dir_l and game.is_collision(point_d)),
            # 4. DIRECTION ACTUELLE (4 bits)
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            # 5. POSITION DE LA NOURRITURE (4 bits - Relatif à la tête)
            game.food.x < head.x,  # La nourriture est à gauche
            game.food.x > head.x,  # La nourriture est à droite
            game.food.y < head.y,  # La nourriture est en haut
            game.food.y > head.y,  # La nourriture est en bas
        ]

        # On convertit les booléens True/False en entiers 1/0
        return tuple(map(int, state))
