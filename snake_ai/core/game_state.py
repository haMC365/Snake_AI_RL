"""
Gestion de l'état de jeu Snake pour l'apprentissage par Renforcement.

Ce module définit la classe GameState (@dataclass) qui représente l'état complet d'un partie:
- Position d'un serpent, nourriture, dimensions de la grille, score, étapes, états de la vie.
- Méthodes utilitaires: clonage profond, détection des collisions, validation des limites

Utilise par:
- Agent RL (snake_ai/agents/rl/) pour l'entrainement Q-learning.
- Agent A* (snake_ai/agents/astar/) et simulations (snake_ai/simulation/)

Exemple d'instantiation:
    state = GameState(snake=[(5, 5)], direction = 'RIGHT', food = (10,10), grid_weight = 20, grid_height = 20)

Classes principales:
- GameState: Etat immuable du jeu avec méthodes de validation

Fichiers liés:
- snake_ai/core/game_state.py : Ce module
- tests/test_game_state.py : Tests unitaires

"""

from dataclasses import dataclass
from typing import List, Tuple
from copy import deepcopy


@dataclass
class GameState:
    """Représente l'etat complet d'une partie de Snake pour l'apprentissage par renforcement"""

    snake: List[Tuple[int, int]]
    direction: str
    food: Tuple[int, int]
    grid_width: int
    grid_height: int

    # Valeurs par défaut pour simplifier l'instanciation
    score: int = 0
    steps: int = 0
    alive: bool = True

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
