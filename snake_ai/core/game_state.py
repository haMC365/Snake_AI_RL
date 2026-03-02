from dataclasses import dataclass
from typing import List, Tuple
from copy import deepcopy


@dataclass
class GameState:
    """
    Représentation pure et sérialisable de l'état du jeu Snake.
    Indépendante de toute logique d'affichage ou de bibliothèque tierce.
    """

    snake: List[Tuple[int, int]]
    direction: str
    food: Tuple[int, int]
    score: int
    steps: int
    alive: bool
    grid_width: int
    grid_height: int

    def clone(self) -> "GameState":
        """
        Retourne une copie profonde (deepcopy) de l'état actuel.
        Indispensable pour la simulation et la recherche de chemin.
        """
        return deepcopy(self)

    def head(self) -> Tuple[int, int]:
        """Retourne la position actuelle de la tête du serpent."""
        return self.snake[0]

    def is_inside_grid(self, position: Tuple[int, int]) -> bool:
        """Vérifie si une position donnée est dans les limites de la grille."""
        x, y = position
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    def is_collision(self, position: Tuple[int, int]) -> bool:
        """
        Vérifie si une position entraîne une collision.
        Collision = Sortie de grille OU contact avec le corps du serpent.
        """
        if not self.is_inside_grid(position):
            return True
        if position in self.snake:
            return True
        return False
