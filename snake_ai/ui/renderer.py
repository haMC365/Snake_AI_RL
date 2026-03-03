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
        pygame.display.set_caption("Snake AI - Tournament")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)

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

    def render_duel(self, state_a: GameState, state_rl: GameState):
        """Affichage split-screen (Mode Duel)."""
        self.display.fill((20, 20, 20))  # Fond sombre

        block = settings.block_size
        grid_pixel_w = state_a.grid_width * block

        # 1. Dessiner la partie A* (Gauche)
        self._draw_grid_content(state_a, 20, 40)
        label_a = self.font.render("AGENT A* (Recherche)", True, (0, 200, 255))
        score_a = self.small_font.render(
            f"Score: {state_a.score} | Pas: {state_a.steps}", True, (200, 200, 200)
        )
        self.display.blit(label_a, [20, 10])
        self.display.blit(score_a, [20, grid_pixel_w + 45])

        # 2. Dessiner la partie RL (Droite)
        offset_rl = grid_pixel_w + 40
        self._draw_grid_content(state_rl, offset_rl, 40)
        label_rl = self.font.render("AGENT RL (Cerveau)", True, (255, 165, 0))
        score_rl = self.small_font.render(
            f"Score: {state_rl.score} | Pas: {state_rl.steps}", True, (200, 200, 200)
        )
        self.display.blit(label_rl, [offset_rl, 10])
        self.display.blit(score_rl, [offset_rl, grid_pixel_w + 45])

        pygame.display.flip()

    def wait(self):
        """Gère la vitesse d'exécution."""
        self.clock.tick(settings.speed)

    def close(self):
        pygame.quit()

    def display_game_over(self, score):
        font = pygame.font.SysFont("Arial", 64, bold=True)
        text = font.render("GAME OVER", True, (255, 0, 0))
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(2000)
