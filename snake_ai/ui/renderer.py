import pygame
from snake_ai.core.game_state import GameState
from snake_ai.config.settings import settings


class SnakeRenderer:
    """
    Responsable de l'affichage du jeu.
    Supporte le mode solo (manuel) et le mode duel (split-screen).
    """

    def __init__(self, width: int = 640, height: int = 480):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake AI - Tournament & Analytics")
        self.clock = pygame.time.Clock()

        # Polices optimisées
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.title_font = pygame.font.SysFont("arial", 16)

    def draw_metrics(self, screen, metrics, x, y, color=(200, 200, 200)):
        """Affiche le bloc de metrics pour l'agent donné."""
        # Multiplication par 1000 pour afficher en millisecondes (ms)
        lines = [
            f"Score: {metrics.get('score', 0)}",
            f"Steps: {metrics.get('steps', 0)}",
            f"Avg Latency: {metrics.get('avg_latency', 0)*1000:.2f} ms",
            f"Max Latency: {metrics.get('max_latency', 0)*1000:.2f} ms",
            f"Runtime: {metrics.get('runtime', 0):.1f}",
        ]

        for i, text in enumerate(lines):
            surface = self.small_font.render(text, True, color)
            screen.blit(surface, (x, y + i * 20))

    def _draw_grid_content(self, state: GameState, offset_x: int, offset_y: int):
        """Méthode interne pour dessiner le contenu d'une grille à une position donnée."""
        block = settings.block_size

        # Dessiner le serpent
        for i, pt in enumerate(state.snake):
            # Tête en vert clair, corps en vert classique
            color = (50, 255, 50) if i == 0 else (34, 139, 34)
            pygame.draw.rect(
                self.display,
                color,
                pygame.Rect(
                    offset_x + pt[0] * block,
                    offset_y + pt[1] * block,
                    block - 1,
                    block - 1,
                ),
            )

        # Dessiner la nourriture
        pygame.draw.rect(
            self.display,
            (255, 0, 0),
            pygame.Rect(
                offset_x + state.food[0] * block,
                offset_y + state.food[1] * block,
                block,
                block,
            ),
        )

        # Dessiner les bordures de la grille
        grid_rect = pygame.Rect(
            offset_x, offset_y, state.grid_width * block, state.grid_height * block
        )
        pygame.draw.rect(self.display, (100, 100, 100), grid_rect, 1)

    def render(self, state: GameState):
        """Affichage classique (Mode Manuel)."""
        self.display.fill((0, 0, 0))
        self._draw_grid_content(state, 20, 40)

        # UI Manuel
        text = self.font.render(f"HUMAIN - Score: {state.score}", True, (255, 255, 255))
        self.display.blit(text, [20, 10])
        pygame.display.flip()

    def render_duel(self, state_a: GameState, state_rl: GameState, metrics: dict):
        """Affichage split-screen (Mode Duel) avec metriques en temps réel"""
        self.display.fill((20, 20, 20))  # Fond sombre

        block = settings.block_size
        grid_pixel_w = state_a.grid_width * block
        y_grid = 50

        # Positionner les metriques sous la grille
        y_metrics = y_grid + grid_pixel_w + 20

        # 1. Dessiner la partie Agents A* (Gauche)
        x_a = 20
        self._draw_grid_content(state_a, x_a, y_grid)
        label_a = self.font.render("Agent A* (Recherche)", True, (0, 200, 255))
        self.display.blit(label_a, [x_a, 15])

        # Affichage des metriques A*
        if "astar" in metrics:
            self.draw_metrics(
                self.display, metrics["astar"], x_a, y_metrics, color=(0, 200, 255)
            )

        # 2. Dessiner l'agent RL (Droite)
        x_rl = grid_pixel_w + 60  # un peu plus d'espace entre les deux
        self._draw_grid_content(state_rl, x_rl, y_grid)
        label_rl = self.font.render("AGENT RL (Q-Table)", True, (255, 165, 0))
        self.display.blit(label_rl, [x_rl, 15])

        if "rl" in metrics:
            self.draw_metrics(
                self.display, metrics["rl"], x_rl, y_metrics, color=(255, 165, 0)
            )

        pygame.display.flip()

    def wait(self):
        """Gère la vitesse d'exécution."""
        self.clock.tick(settings.speed)

    def close(self):
        """Close Pygame"""
        pygame.quit()

    def display_game_over(self, score):
        """Fonction pour montrer al fenetre OVER"""
        font = pygame.font.SysFont("Arial", 64, bold=True)
        text = font.render("GAME OVER", True, (255, 0, 0))
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(2000)
