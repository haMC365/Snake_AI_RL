import time
import random
from tensorboardX import SummaryWriter


def run_simulation():
    # On crée un dossier spécifique pour ce test
    writer = SummaryWriter("logs/test_session")
    print("🚀 Simulation d'entraînement en cours... Regarde ton navigateur !")

    epsilon = 1.0
    avg_reward = 0

    for epoch in range(100):
        # Simulation : Le score augmente lentement avec du bruit
        reward = (epoch * 0.5) + random.uniform(-2, 2)
        avg_reward = (avg_reward * 0.9) + (reward * 0.1)

        # Simulation : L'exploration (epsilon) diminue
        epsilon *= 0.96

        # Enregistrement des métriques
        writer.add_scalar("Performance/Average_Reward", avg_reward, epoch)
        writer.add_scalar("Exploration/Epsilon", epsilon, epoch)

        time.sleep(0.15)  # Pour simuler le temps de calcul

    writer.close()
    print("✅ Simulation terminée. Rafraîchis http://localhost:6006")


if __name__ == "__main__":
    run_simulation()
