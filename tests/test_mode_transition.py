import pytest
from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.simulation.mode_manager import ModeManager, GameMode
from snake_ai.simulation.duel_manager import DuelManager

def test_mode_switch():
    state = GameState(snake=[(5,5)], direction="RIGHT", food=(10,10), 
                      score=0, steps=0, alive=True, grid_width=20, grid_height=20)
    engine = SnakeEngine(state)
    duel_manager = DuelManager()
    mode_manager = ModeManager(engine, duel_manager)
    
    mode_manager.start_duel()
    assert mode_manager.mode == GameMode.DUEL
    assert duel_manager.running is True

def test_duel_states_independent():
    initial = GameState(snake=[(5,5)], direction="RIGHT", food=(10,10), 
                        score=0, steps=0, alive=True, grid_width=20, grid_height=20)
    dm = DuelManager()
    dm.start(initial)

    # On modifie artificiellement l'état A*
    dm.state_astar.snake.append((99, 99))

    # L'état RL ne doit pas avoir reçu cette modification
    assert (99, 99) not in dm.state_rl.snake
    assert len(dm.state_astar.snake) != len(dm.state_rl.snake)