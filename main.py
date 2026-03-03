import pygame
import sys
from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.ui.renderer import SnakeRenderer
from snake_ai.simulation.duel_manager import DuelManager
from snake_ai.simulation.mode_manager import ModeManager, GameMode
from snake_ai.config.settings import settings

def get_manual_action(key):
    """Traduit les touches du clavier en directions pour le moteur."""
    if key in [pygame.K_UP, pygame.K_w]:
        return "UP"
    if key in [pygame.K_DOWN, pygame.K_s]:
        return "DOWN"
    if key in [pygame.K_LEFT, pygame.K_a]:
        return "LEFT"
    if key in [pygame.K_RIGHT, pygame.K_d]:
        return "RIGHT"
    return None

def main():
    # 1. Initialisation de l'état initial (Grille 20x20 par défaut)
    grid_size = 20
    initial_state = GameState(
        snake=[(5, 10), (4, 10), (3, 10)],
        direction="RIGHT",
        food=(15, 10),
        score=0,
        steps=0,
        alive=True,
        grid_width=grid_size,
        grid_height=grid_size
    )

    # 2. Setup des composants
    engine = SnakeEngine(initial_state)
    duel_manager = DuelManager()
    mode_manager = ModeManager(engine, duel_manager)
    
    # On ajuste la taille de la fenêtre pour le mode Duel (deux grilles)
    renderer = SnakeRenderer(
        width=grid_size * settings.block_size * 2 + 40, # x2 pour deux grilles + marge
        height=grid_size * settings.block_size + 60
    )

    clock = pygame.time.Clock()

    running = True
    print("🎮 Mode MANUEL activé. Utilisez les flèches pour jouer.")

    while running:

        clock.tick(10)
        
        # 3. Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d and mode_manager.mode == GameMode.MANUAL:
                    mode_manager.start_duel()
                else:
                    # On met à jour la direction dans l'état, mais on ne fait pas le step ici
                    new_dir = get_manual_action(event.key)
                    if new_dir:
                        engine.state.direction = new_dir

        # 4. Logique de mise à jour selon le Mode
        if mode_manager.mode == GameMode.MANUAL:
            # --- CORRECTION ICI : Mouvement automatique ---
            # On appelle step() à chaque tour de boucle avec la direction actuelle
            alive = engine.step(engine.state.direction)
            
            if not alive:
                # Gestion du Game Over
                print(f"💀 Game Over! Score final: {engine.state.score}")
                # Optionnel : appeler une fonction de rendu Game Over ici
                pygame.time.wait(2000)
                running = False 
            
            renderer.render(engine.get_state())
            
        elif mode_manager.mode == GameMode.DUEL:
            duel_manager.step()
            renderer.render_duel(duel_manager.state_astar, duel_manager.state_rl)

        # 5. Contrôle du FPS (définit la vitesse)
        renderer.wait()

    # Petit délai pour voir le dernier état avant de fermer
    pygame.time.wait(1000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
