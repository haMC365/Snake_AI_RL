import pytest
import copy
from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.simulation.duel_manager import DuelManager
from snake_ai.agents.astar.astar_agent import AStarAgent
from snake_ai.agents.rl.rl_agent import RLAgent


@pytest.fixture
def setup_duel():
    """Prépare un environnement de duel avec des états profonds (indépendants)."""
    grid_size = 20  # On augmente la taille pour éviter de mourir trop vite
    state = GameState(
        snake=[(10, 10), (9, 10), (8, 10)],
        direction="RIGHT",
        food=(15, 15),
        grid_width=grid_size,
        grid_height=grid_size,
    )

    engine_astar = SnakeEngine(copy.deepcopy(state))
    engine_rl = SnakeEngine(copy.deepcopy(state))

    astar_agent = AStarAgent()
    rl_agent = RLAgent()

    duel = DuelManager(engine_astar, engine_rl, astar_agent, rl_agent)
    return duel


def test_multithread_step_runs(setup_duel):
    duel = setup_duel
    duel.step()
    assert duel.state_astar is not None
    assert duel.state_rl is not None


def test_states_independence(setup_duel):
    duel = setup_duel

    # Modifier la nourriture de l'un
    duel.state_astar.food = (1, 1)
    duel.state_rl.food = (19, 19)  # (9,9) était trop proche du bord

    # Verifier AVANT le step que les IDs sont différents
    assert id(duel.state_astar) != id(duel.state_rl)

    duel.step()

    # Vérification que les nourritures sont restées distinctes
    assert duel.state_astar.food == (1, 1)
    assert duel.state_rl.food == (19, 19)


def test_multiple_consecutive_steps(setup_duel):
    """Fonction pour tester les test multiples steps"""
    duel = setup_duel
    num_steps = 5  # On réduit à 5 pour être sûr de ne pas toucher de mur

    for _ in range(num_steps):
        duel.step()

    # Verifier que les deux ont avancé du même nombre de pas
    assert duel.state_astar.steps == num_steps
    assert duel.state_rl.steps == num_steps
    assert duel.state_astar.alive is True


def test_duel_shutdown(setup_duel):
    duel = setup_duel
    duel.step()
    duel.shutdown()

    # Utilisation d'une vérification publique de l'état de l'executor
    # pylint: disable=protected-access
    assert duel.executor._shutdown is True
