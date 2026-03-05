from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.simulation.mode_manager import ModeManager, GameMode
from snake_ai.simulation.duel_manager import DuelManager

from snake_ai.agents.astar.astar_agent import AStarAgent
from snake_ai.agents.rl.rl_agent import RLAgent


def test_mode_switch():
    state = GameState(
        snake=[(5, 5)],
        direction="RIGHT",
        food=(10, 10),
        score=0,
        steps=0,
        alive=True,
        grid_width=20,
        grid_height=20,
    )

    # 1. Creation des dependances requises par DuelManager
    engine_astar = SnakeEngine(state)
    engine_rl = SnakeEngine(state)
    astar_agent = AStarAgent()
    rl_agent = RLAgent()  # Utilise la Q-Table par defaut ou une table vide

    duel_manager = DuelManager(
        engine_star=engine_astar,
        engine_rl=engine_rl,
        astar_agent=astar_agent,
        rl_agent=rl_agent,
    )

    engine_manual = SnakeGame(state)
    mode_manager = ModeManager(engine, duel_manager)

    # 3. Test de transition
    mode_manager.start_duel()
    assert mode_manager.mode == GameMode.DUEL


def test_duel_states_independent():
    initial = GameState(
        snake=[(5, 5)],
        direction="RIGHT",
        food=(10, 10),
        score=0,
        steps=0,
        alive=True,
        grid_width=20,
        grid_height=20,
    )
    dm = DuelManager()
    dm.start(initial)

    # On modifie artificiellement l'état A*
    dm.state_astar.snake.append((99, 99))

    # L'état RL ne doit pas avoir reçu cette modification
    assert (99, 99) not in dm.state_rl.snake
    assert len(dm.state_astar.snake) != len(dm.state_rl.snake)
