import pygame
import random
from enum import Enum
from typing import NamedTuple

# On importe l'instance settings
from snake_ai.config.settings import settings


# Configuration simple pour les coordonnées
class Point(NamedTuple):
    x: int
    y: int


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


# --- LES VARIABLES GLOBALES ONT ÉTÉ SUPPRIMÉES ICI ---
# Elles sont remplacées par settings.block_size et settings.speed


class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # Initialisation de l'affichage
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake AI - Training Mode")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # État initial du jeu
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            Point(self.head.x - settings.block_size, self.head.y),
            Point(self.head.x - (2 * settings.block_size), self.head.y),
        ]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        # Utilisation de settings.block_size pour la grille
        x = (
            random.randint(0, (self.w - settings.block_size) // settings.block_size)
            * settings.block_size
        )
        y = (
            random.randint(0, (self.h - settings.block_size) // settings.block_size)
            * settings.block_size
        )
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. Collecter l'input utilisateur (pour fermer la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. Déplacer le serpent
        self._move(action)
        self.snake.insert(0, self.head)

        # 3. Vérifier si Game Over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. Placer nouvelle nourriture ou se déplacer simplement
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. Update UI et horloge (Utilisation de settings.speed)
        self._update_ui()
        self.clock.tick(settings.speed)

        # 6. Retourner le résultat du step
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # Touche les bords (Utilisation de settings.block_size)
        if (
            pt.x > self.w - settings.block_size
            or pt.x < 0
            or pt.y > self.h - settings.block_size
            or pt.y < 0
        ):
            return True
        # Se touche lui-même
        if pt in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.display.fill((0, 0, 0))  # Noir
        for pt in self.snake:
            pygame.draw.rect(
                self.display,
                (0, 255, 0),
                pygame.Rect(pt.x, pt.y, settings.block_size, settings.block_size),
            )
        pygame.draw.rect(
            self.display,
            (255, 0, 0),
            pygame.Rect(
                self.food.x, self.food.y, settings.block_size, settings.block_size
            ),
        )
        pygame.display.flip()

    def _move(self, action):
        # action -> [tout droit, droite, gauche]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if list(action) == [1, 0, 0]:
            new_dir = clock_wise[idx]  # Pas de changement
        elif list(action) == [0, 1, 0]:
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # Tourne à droite
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # Tourne à gauche

        self.direction = new_dir

        x, y = self.head.x, self.head.y
        if self.direction == Direction.RIGHT:
            x += settings.block_size
        elif self.direction == Direction.LEFT:
            x -= settings.block_size
        elif self.direction == Direction.DOWN:
            y += settings.block_size
        elif self.direction == Direction.UP:
            y -= settings.block_size
        self.head = Point(x, y)
