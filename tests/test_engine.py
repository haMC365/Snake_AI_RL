import pytest
from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine

def test_continuous_movement_logic():
    # Setup : Serpent en (5,5), direction RIGHT
    state = GameState(grid_width=10, grid_height=10)
    state.snake = [(5, 5), (4, 5)]
    state.direction = "RIGHT"
    engine = SnakeEngine(state)
    
    # Exécuter un pas sans changer la direction
    alive = engine.step("RIGHT")
    
    # Vérification : La tête doit être en (6,5)
    assert alive is True
    assert state.head() == (6, 5)
    assert len(state.snake) == 2

def test_game_over_detection():
    # Setup : Serpent contre le mur gauche, direction LEFT
    state = GameState(grid_width=10, grid_height=10)
    state.snake = [(0, 5)]
    state.direction = "LEFT"
    engine = SnakeEngine(state)
    
    # Exécuter le pas fatal
    alive = engine.step("LEFT")
    
    # Vérification
    assert alive is False
    assert state.alive is False