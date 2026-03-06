import copy
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
        engine_astar=engine_astar,
        engine_rl=engine_rl,
        astar_agent=astar_agent,
        rl_agent=rl_agent,
    )

    engine_manual = SnakeEngine(state)
    mode_manager = ModeManager(engine_manual, duel_manager)

    # 3. Test de transition
    mode_manager.start_duel()
    assert mode_manager.mode == GameMode.DUEL


def test_duel_states_independent():
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

    # CRUCIAL : On utilise deepcopy pour créer deux instances distinctes en mémoire
    state_astar = copy.deepcopy(state)
    state_rl = copy.deepcopy(state)

    dm = DuelManager(
        engine_astar=SnakeEngine(state_astar),
        engine_rl=SnakeEngine(state_rl),
        astar_agent=AStarAgent(),
        rl_agent=RLAgent(),
    )

    # On modifie uniquement le serpent A*
    dm.state_astar.snake.append((99, 99))

    # Maintenant, l'assertion va passer car state_rl a sa propre liste snake
    assert (99, 99) not in dm.state_rl.snake
    assert len(dm.state_astar.snake) == 2
    assert len(dm.state_rl.snake) == 1

    dm.shutdown()
