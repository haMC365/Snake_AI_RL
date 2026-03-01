from snake_ai.engine.game import SnakeGameAI
from snake_ai.agents.rl.encoders import StateEncoder


def test():
    game = SnakeGameAI()
    encoder = StateEncoder()

    # On fait un pas de jeu vide
    state = encoder.encode(game)

    print(f"Vecteur d'état généré : {state}")
    print(f"Taille du vecteur : {len(state)} bits")

    if len(state) == 11:
        print("✅ Validation réussie : L'encodeur produit le bon format !")


if __name__ == "__main__":
    test()
