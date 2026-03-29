import heapq
from typing import List, Tuple, Optional
from snake_ai.core.game_state import GameState


class AStarAgent:
    """
    Agent utilisant l'algorithme A* pour trouver le chemin le plus court
    vers la nourriture dans la grille du Snake.
    """

    def get_action(self, state: GameState) -> str:
        start = state.head()
        goal = state.food
        # On inclut tout le corps comme obstacle
        obstacles = set(state.snake)

        # 1. Tenter de trouver le chemin vers la nourriture
        path = self._astar(start, goal, obstacles, state.grid_width, state.grid_height)

        # 2. Validation du chemin
        if path and len(path) > 1:
            if self._is_path_safe(state, path):
                return self._get_direction_from_coords(start, path[1])

        # 3. Si chemin vers nourriture dangereux ou inexistant -> Suivre la queue
        tail = state.snake[-1]
        path_to_tail = self._astar(
            start, tail, obstacles - {tail}, state.grid_width, state.grid_height
        )

        if path_to_tail and len(path_to_tail) > 1:
            return self._get_direction_from_coords(start, path_to_tail[1])

        # 4. Dernier recours : survie basique
        return self._survival_move(state, obstacles)

    def _astar(
        self, start, goal, obstacles, width, height
    ) -> Optional[List[Tuple[int, int]]]:
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbor in self._get_neighbors(current, width, height):
                if neighbor in obstacles and neighbor != goal:  # Le goal est autorisé
                    continue

                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
        return None

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Distance de Manhattan."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_neighbors(self, pos, width, height):
        x, y = pos
        return [
            (nx, ny)
            for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if 0 <= nx < width and 0 <= ny < height
        ]

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def _get_direction_from_coords(self, start, end):
        dx, dy = end[0] - start[0], end[1] - start[1]
        mapping = {(1, 0): "RIGHT", (-1, 0): "LEFT", (0, 1): "DOWN", (0, -1): "UP"}
        return mapping.get((dx, dy), "RIGHT")

    def _is_path_safe(self, state: GameState, path: List[Tuple[int, int]]) -> bool:
        """
        Vérifie si le chemin vers la nourriture ne mène pas à une impasse.
        On simule virtuellement la position du serpent à la fin du chemin.
        """
        # Simulation simplifiée, verifier que la tête à la nourriture peut encore atteindre la queue
        simulated_head = path[-1]
        # Après avoir mangé, le corps est le chemin parcouru + l'ancien corps (moins la queue qui bouge)
        # Pour rester simple : on vérifie si la nouvelle tête n'est pas totalement entourée
        neighbors = self._get_neighbors(
            simulated_head, state.grid_width, state.grid_height
        )

        # Si la tête est entourée d'obstacles (corps simuler) à l'arrivée, c'est un piège
        free_neighbors = [
            n for n in neighbors if n not in set(state.snake) or n == state.snake[-1]
        ]
        return len(free_neighbors) > 0

    def _survival_move(self, state, obstacles):
        head = state.head()
        # Priorité au mouvement qui offre le plus de voisins libres
        best_dir = state.direction
        max_free = -1

        for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
            nx, ny = head
            if direction == "UP":
                ny -= 1
            elif direction == "DOWN":
                ny += 1
            elif direction == "LEFT":
                nx -= 1
            elif direction == "RIGHT":
                nx += 1

            if (
                0 <= nx < state.grid_width
                and 0 <= ny < state.grid_height
                and (nx, ny) not in obstacles
            ):
                free_space = len(
                    [
                        n
                        for n in self._get_neighbors(
                            (nx, ny), state.grid_width, state.grid_height
                        )
                        if n not in obstacles
                    ]
                )
                if free_space > max_free:
                    max_free = free_space
                    best_dir = direction
        return best_dir
