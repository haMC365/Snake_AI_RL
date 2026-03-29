from snake_ai.config.settings import settings


def test_config():
    print("--- Configuration IA ---")
    print(f"Alpha: {settings.alpha}")
    print(f"Gamma: {settings.gamma}")
    print(f"Epsilon Decay: {settings.epsilon_decay}")
    print(f"Taille des blocs: {settings.block_size}")

    if settings.alpha == 0.1:
        print("\nConfiguration chargée avec succès !")


if __name__ == "__main__":
    test_config()
