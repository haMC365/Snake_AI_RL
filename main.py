"""Module Principal"""

from typing import Any

import sys
import copy
import pygame

from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.ui.renderer import SnakeRenderer
from snake_ai.ui.charts import LivePerformanceCharts
from snake_ai.simulation.duel_manager import DuelManager
from snake_ai.simulation.mode_manager import ModeManager, GameMode
from snake_ai.config.settings import settings
from snake_ai.agents.astar.astar_agent import AStarAgent
from snake_ai.agents.rl.rl_agent import RLAgent


def get_manual_action(key: Any):
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
    """Fonctionnement principal"""
    # 1. Initialisation de l'état initial
    grid_size = 20
    initial_state = GameState(
        snake=[(5, 10), (4, 10), (3, 10)],
        direction="RIGHT",
        food=(15, 10),
        score=0,
        steps=0,
        alive=True,
        grid_width=grid_size,
        grid_height=grid_size,
    )

    # 2. Setup des composants de base
    engine = SnakeEngine(initial_state)

    # --- PRÉPARATION DU MODE DUEL ---
    state_astar = copy.deepcopy(initial_state)
    state_rl = copy.deepcopy(initial_state)

    # Création des deux moteurs séparés
    engine_astar = SnakeEngine(state_astar)
    engine_rl = SnakeEngine(state_rl)

    # Initialisation des agents
    astar_agent = AStarAgent()
    rl_agent = RLAgent(model_path="data/q_table.msgpack")

    # Initialisation du DuelManager avec ses dépendances
    duel_manager = DuelManager(
        engine_astar=engine_astar,
        engine_rl=engine_rl,
        astar_agent=astar_agent,
        rl_agent=rl_agent,
    )

    mode_manager = ModeManager(engine, duel_manager)

    # Setup du Renderer
    renderer = SnakeRenderer(
        width=grid_size * settings.block_size * 2 + 80,
        height=grid_size * settings.block_size + 160,
    )

    clock = pygame.time.Clock()
    running = True

    print("Mode MANUEL activé. Utilisez les flèches pour jouer.")
    print("Appuyez sur 'D' pour lancer le DUEL : A* (Gauche) vs RL (Droite)")

    charts = None
    current_episode = 0

    try:
        while running:
            # Gestion de la vitesse (10 FPS pour un mouvement fluide et jouable)
            clock.tick(10)

            # 3. Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    # Déclenchement du Duel
                    if event.key == pygame.K_d and mode_manager.mode == GameMode.MANUAL:
                        mode_manager.start_duel()
                    else:
                        # Changement de direction manuel
                        new_dir = get_manual_action(event.key)
                        if new_dir:
                            engine.state.direction = new_dir

            # 4. Logique de mise à jour selon le Mode
            if mode_manager.mode == GameMode.MANUAL:

                # Mouvement automatique continu
                alive = engine.step(engine.state.direction)

                if not alive:
                    print(f"Game Over! Score final: {engine.state.score}")
                    # Affichage via le moteur (si implémenté) ou simple pause
                    renderer.render(engine.get_state())
                    pygame.time.wait(2000)
                    running = False
                else:
                    renderer.render(engine.get_state())

            elif mode_manager.mode == GameMode.DUEL:
                duel_manager.step()

                # 1. Initialisation de la fenêtre de graphiques au premier pas du duel
                if charts is None:
                    print("Ouverture des graphiques de performance...")
                    charts = LivePerformanceCharts()  # On crée l'instance ici

                # 2. Récupération des métriques
                metrics = duel_manager.get_metrics()

                # Mettre en oeuvre les graphiques TOUTES les frames (ou toutes les 10 frames pour economiser le CPU)
                if metrics["astar"]["steps"] % 5 == 0:  # Toutes les 5 étapes
                    charts.update_data(
                        metrics["astar"]["steps"], metrics["astar"], metrics["rl"]
                    )

                # 3. Mise à jour des graphiques quand un serpent meurt (fin d'épisode)
                if (
                    not duel_manager.state_astar.alive
                    or not duel_manager.state_rl.alive
                ):
                    current_episode += 1
                    charts.update_data(current_episode, metrics["astar"], metrics["rl"])

                # 4. Rendu Pygame
                renderer.render_duel(
                    duel_manager.state_astar, duel_manager.state_rl, metrics
                )

            # 5. Rafraîchissement de l'écran
            pygame.display.flip()

    except Exception as e:
        print(f"Erreur critique : {e}")

    finally:
        print("Fermeture du jeu...")
        duel_manager.shutdown()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
