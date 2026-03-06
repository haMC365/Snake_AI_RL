from snake_ai.core.game_state import GameState
from snake_ai.agents.rl.encoders import StateEncoder


def test():
    # On crée un état de jeu manuel pour le test
    state = GameState(
        snake=[(5, 5), (4, 5)],
        direction="RIGHT",
        food=(10, 10),
        score=0,
        steps=0,
        alive=True,
        grid_width=20,
        grid_height=20,
    )

    encoder = StateEncoder()

    # On encode l'état
    encoded_state = encoder.encode(state)

    print(f"Vecteur d'état généré : {encoded_state}")
    print(f"Taille du vecteur : {len(encoded_state)} bits")

    if len(encoded_state) == 11:
        print("✅ Validation réussie : L'encodeur fonctionne avec GameState !")


if __name__ == "__main__":
    test()
