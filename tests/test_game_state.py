from snake_ai.core.game_state import GameState


def test_clone_independence():
    """Vérifie que modifier le clone ne modifie pas l'original (Deep Copy)."""
    state = GameState(
        snake=[(5, 5), (5, 6)],
        direction="UP",
        food=(2, 2),
        score=1,
        steps=10,
        alive=True,
        grid_width=20,
        grid_height=20,
    )

    clone = state.clone()

    # Action : On ajoute un segment au clone uniquement
    clone.snake.append((5, 7))

    # Assert : L'original doit rester intact
    assert len(state.snake) == 2, "L'original a été modifié par erreur !"
    assert len(clone.snake) == 3, "Le clone n'a pas été mis à jour correctement."
    assert state.snake != clone.snake


def test_collision_wall():
    """Vérifie que la sortie de grille est détectée comme une collision."""
    state = GameState(
        snake=[(0, 0)],
        direction="UP",
        food=(5, 5),
        score=0,
        steps=0,
        alive=True,
        grid_width=10,
        grid_height=10,
    )

    # Test aux limites
    assert state.is_collision((-1, 0)) is True, "Collision mur gauche non détectée"
    assert state.is_collision((10, 0)) is True, "Collision mur droit non détectée"
    assert state.is_collision((0, -1)) is True, "Collision mur haut non détectée"
    assert state.is_collision((0, 10)) is True, "Collision mur bas non détectée"
    assert (
        state.is_collision((5, 5)) is False
    ), "Position valide détectée comme collision"


def test_collision_body():
    """Vérifie que percuter son propre corps est détecté comme une collision."""
    state = GameState(
        snake=[(5, 5), (5, 6), (5, 7)],
        direction="UP",
        food=(2, 2),
        score=0,
        steps=0,
        alive=True,
        grid_width=20,
        grid_height=20,
    )

    # La tête est en (5,5). On teste une collision sur le corps en (5,6)
    assert state.is_collision((5, 6)) is True, "Collision avec le corps non détectée"
    assert (
        state.is_collision((2, 2)) is False
    ), "Position de la nourriture détectée comme collision"


def test_head_utility():
    """Vérifie que la méthode head() renvoie bien le premier élément."""
    state = GameState(
        snake=[(10, 10), (10, 11)],
        direction="RIGHT",
        food=(15, 15),
        score=0,
        steps=0,
        alive=True,
        grid_width=20,
        grid_height=20,
    )
    assert state.head() == (10, 10)
