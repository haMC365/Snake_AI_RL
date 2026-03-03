import pygame
import random
from typing import Tuple
from snake_ai.core.game_state import GameState


class SnakeEngine:
    """
    Logique pure du jeu Snake (Moteur).
    Manipule uniquement un objet GameState.
    AUCUN import de Pygame ici (l'affichage est géré par le Renderer).
    """

    def __init__(self, initial_state: GameState, screen=None):
        self.state = initial_state
        self.running = True
        self.screen = screen  # On passe l'écran Pygame ici
        # Définir largeur/hauteur pour le texte centré (ex: 600x600)
        self.width = initial_state.grid_width * 20
        self.height = initial_state.grid_height * 20
        # VITESSE : 10 FPS est une vitesse réaliste pour commencer
        self.fps = 10
        # DIRECTION PAR DÉFAUT : Important pour qu'il bouge dès le lancement
        if not self.state.direction:
            self.state.direction = "RIGHT"

    def step(self, action: str) -> bool:  # On retourne True si vivant
        if not self.state.alive:
            return False

        self._update_direction(action)
        new_head = self._compute_new_head()

        if self.state.is_collision(new_head):
            self.state.alive = False
            return False

        self.state.snake.insert(0, new_head)

        if new_head == self.state.food:
            self.state.score += 1
            self._spawn_food()
        else:
            self.state.snake.pop()

        self.state.steps += 1
        return True

    def run(self):
        pygame.init()
        clock = pygame.time.Clock()

        while self.running:
            # --- 1. CADENCE ---
            # Cette ligne gère la vitesse. Si tu l'enlèves, le serpent est trop rapide.
            clock.tick(self.fps)

            # --- 2. ENTRÉES CLAVIER ---
            # On ne fait QUE changer la variable de direction ici
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self._update_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        self._update_direction("DOWN")
                    elif event.key == pygame.K_LEFT:
                        self._update_direction("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self._update_direction("RIGHT")

            # --- 3. MOUVEMENT AUTOMATIQUE (L'élément manquant) ---
            # On appelle step() avec la direction actuelle stockée dans l'état.
            # Cela arrive à chaque tour de boucle, même si tu ne touches pas au clavier.
            alive = self.step(self.state.direction)

            # --- 4. VÉRIFICATION COLLISION ---
            if not alive:
                self.show_game_over()
                self.running = False
                continue  # On sort de la boucle

            # --- 5. AFFICHAGE ---
            # TRÈS IMPORTANT : Redessiner l'écran à chaque mouvement
            if hasattr(self, "renderer"):
                self.renderer.render(self.state)
            else:
                # Si tu n'as pas de renderer séparé, appelle ta fonction de dessin ici
                self._draw_everything()

            pygame.display.flip()  # Rafraîchit l'écran Pygame

    def show_game_over(self):
        """Affiche le titre Game Over et le score final."""
        if self.screen:
            # 1. Préparation des polices
            font_large = pygame.font.SysFont("Arial", 64, bold=True)
            font_small = pygame.font.SysFont("Arial", 32)

            # 2. Création des surfaces de texte
            title_surf = font_large.render(
                "GAME OVER", True, (255, 50, 50)
            )  # Rouge vif
            score_surf = font_small.render(
                f"Score Final : {self.state.score}", True, (255, 255, 255)
            )  # Blanc

            # 3. Positionnement (centré)
            title_rect = title_surf.get_rect(
                center=(self.width // 2, self.height // 2 - 20)
            )
            score_rect = score_surf.get_rect(
                center=(self.width // 2, self.height // 2 + 40)
            )

            # 4. Dessiner un rectangle de fond pour la lisibilité
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Noir transparent (Alpha = 180)
            self.screen.blit(overlay, (0, 0))

            # 5. Affichage final
            self.screen.blit(title_surf, title_rect)
            self.screen.blit(score_surf, score_rect)

            pygame.display.flip()

            # 6. Petite pause pour laisser le temps de voir le score
            pygame.time.wait(2500)

    def _update_direction(self, new_dir: str) -> None:
        """Change la direction si elle n'est pas opposée à l'actuelle."""
        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_dir in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if new_dir != opposites.get(self.state.direction):
                self.state.direction = new_dir

    def _compute_new_head(self) -> Tuple[int, int]:
        """Calcule la coordonnée (x, y) de la prochaine tête."""
        x, y = self.state.head()
        if self.state.direction == "UP":
            y -= 1
        elif self.state.direction == "DOWN":
            y += 1
        elif self.state.direction == "LEFT":
            x -= 1
        elif self.state.direction == "RIGHT":
            x += 1
        return (x, y)

    def _spawn_food(self) -> None:
        """Place la nourriture sur une case vide aléatoire."""
        while True:
            new_food = (
                random.randint(0, self.state.grid_width - 1),
                random.randint(0, self.state.grid_height - 1),
            )
            if new_food not in self.state.snake:
                self.state.food = new_food
                break

    def get_state(self) -> GameState:
        return self.state

    def get_state_clone(self) -> GameState:
        """Retourne une copie indépendante de l'état actuel."""
        return self.state.clone()
