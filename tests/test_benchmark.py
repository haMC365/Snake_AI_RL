import pytest
from benchmarks.run_duel_benchmark import run_single_duel, create_initial_state
from snake_ai.agents.astar.astar_agent import AStarAgent
from snake_ai.agents.rl.rl_agent import RLAgent


def test_single_duel_runs():
    astar = AStarAgent()
    rl = RLAgent()
    metrics = run_single_duel(astar, rl, 10)

    assert "astar_score" in metrics
    assert "rl_score" in metrics
    assert metrics["astar_steps"] > 0


def test_initial_state_no_ui():
    state = create_initial_state(20)
    assert state.grid_width == 20
    assert len(state.snake) == 3
    assert state.alive is True
