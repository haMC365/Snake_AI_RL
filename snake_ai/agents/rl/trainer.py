import os
import random
import msgpack
import numpy as np
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
import sys

from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.agents.rl.encoders import StateEncoder


class RLMonitor:
    """Gère l'enregistrement des métriques pour TensorBoard."""

    def __init__(self, log_dir):
        self.writer = SummaryWriter(log_dir)

    def log_metrics(self, episode, reward, score, steps, epsilon):
        self.writer.add_scalar("Reward/Total", reward, episode)
        self.writer.add_scalar("Game/Score", score, episode)
        self.writer.add_scalar("Game/Steps", steps, episode)
        self.writer.add_scalar("Exploration/Epsilon", epsilon, episode)

    def close(self):
        self.writer.close()


class QTrainer:
    def __init__(
        self,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=0.9995,
    ):

        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_end
        self.decay = epsilon_decay

        self.encoder = StateEncoder()
        self.q_table = {}  # Format: { "state_str": [q_straight, q_right, q_left] }

        # Configuration du monitoring
        log_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.monitor = RLMonitor(f"logs/train_{log_name}")

    def get_action_idx(self, state_key):
        """Choisit une action (0, 1, 2) selon la stratégie Epsilon-Greedy."""
        if random.random() < self.epsilon:
            return random.randint(0, 2)

        q_values = self.q_table.get(state_key, [0.0, 0.0, 0.0])
        return np.argmax(q_values)

    def update_q_table(self, state, action, reward, next_state):
        """Applique l'équation de Bellman pour mettre à jour la Q-Table."""
        state_key = str(state)
        next_state_key = str(next_state)

        # Initialisation si état inconnu
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0, 0.0, 0.0]
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0.0, 0.0, 0.0]

        # Q-Learning : Q(s,a) = Q(s,a) + lr * [reward + gamma * max(Q(s',a')) - Q(s,a)]
        old_value = self.q_table[state_key][action]
        next_max = max(self.q_table[next_state_key])

        new_value = old_value + self.lr * (reward + self.gamma * next_max - old_value)
        self.q_table[state_key][action] = new_value

    def train(self, num_episodes=10000, save_path="data/q_table.msgpack"):
        print(f"🚀 Décollage de l'entraînement pour {num_episodes} épisodes...")

        for episode in range(num_episodes):
            initial_state = GameState(
                snake=[(5, 10), (4, 10), (3, 10)],
                direction="RIGHT",
                food=(15, 10),
                score=0,
                steps=0,
                alive=True,
                grid_width=20,
                grid_height=20,
            )

            engine = SnakeEngine(initial_state)
            total_reward = 0
            done = False

            while not done:
                current_state = engine.get_state()
                state_vec = self.encoder.encode(current_state)

                # 1. Choisir l'action
                action_idx = self.get_action_idx(str(state_vec))

                # 2. Préparer la direction (Conversion relative -> absolue)
                directions = ["UP", "RIGHT", "DOWN", "LEFT"]
                curr_idx = directions.index(current_state.direction)
                if action_idx == 0:
                    next_dir = current_state.direction
                elif action_idx == 1:
                    next_dir = directions[(curr_idx + 1) % 4]
                else:
                    next_dir = directions[(curr_idx - 1) % 4]

                # 3. Calculer la distance AVANT le pas
                head_before = current_state.head()
                dist_before = abs(head_before[0] - current_state.food[0]) + abs(
                    head_before[1] - current_state.food[1]
                )

                # 4. EXÉCUTER LE PAS (Une seule fois !)
                alive = engine.step(next_dir)

                # 5. Calcul de la récompense
                reward = 0
                if not alive:
                    reward = -10
                    done = True
                elif engine.state.score > current_state.score:
                    reward = 20  # Gros bonus pour la nourriture
                else:
                    # Calcul de la distance APRÈS le pas
                    head_after = engine.state.head()
                    dist_after = abs(head_after[0] - engine.state.food[0]) + abs(
                        head_after[1] - engine.state.food[1]
                    )

                    if dist_after < dist_before:
                        reward = 1.0  # Encourage à s'approcher
                    else:
                        reward = -1.5  # Décourage de s'éloigner ou de boucler

                # 6. Mise à jour Q-Table
                next_state_vec = self.encoder.encode(engine.get_state())
                self.update_q_table(state_vec, action_idx, reward, next_state_vec)

                total_reward += reward

            # Decay epsilon (hors de la boucle while)
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.decay

            # Logging
            if episode % 100 == 0:
                print(
                    f"Episode {episode} | Score: {engine.state.score} | Epsilon: {self.epsilon:.2f}"
                )
                self.monitor.log_metrics(
                    episode,
                    total_reward,
                    engine.state.score,
                    engine.state.steps,
                    self.epsilon,
                )

        # 5. Sauvegarde finale
        self.save(save_path)
        self.monitor.close()

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            msgpack.pack(self.q_table, f)
        print(f"✅ Modèle sauvegardé sous {path}")


if __name__ == "__main__":
    trainer = QTrainer()
    episodes = 15000
    if len(sys.argv) > 1:
        try:
            episodes = int(sys.argv[1])
        except ValueError:
            if "--episodes" in sys.argv:
                idx = sys.argv.index("--episodes")
                episodes = int(sys.argv[idx + 1])
    trainer.train(num_episodes=episodes)
