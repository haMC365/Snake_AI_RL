"""
Ce module sert pour declencher l'entrainement
"""

import sys
from datetime import datetime
from typing import List, Dict

import os
import random
import msgpack  # type: ignore
import numpy as np

from torch.utils.tensorboard import SummaryWriter
from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.agents.rl.encoders import StateEncoder


class RLMonitor:
    """Gère l'enregistrement des métriques pour TensorBoard."""

    def __init__(self, log_dir: str):
        self.writer: SummaryWriter = SummaryWriter(log_dir)

    def log_metrics(
        self,
        episode: int,
        reward: float,
        score: int,
        steps: int,
        epsilon: float,
        q_table_size: int,
        avg_loss: float,
    ):
        """Regroupement par dossier pour une interface propre"""
        self.writer.add_scalar("1_Performance/Score", score, episode)
        self.writer.add_scalar("1_Performance/Total_Reward", reward, episode)

        self.writer.add_scalar("2_Efficiency/Steps_per_Episode", steps, episode)

        self.writer.add_scalar("3_RL_Internals/Epsilon", epsilon, episode)
        self.writer.add_scalar("3_RL_Internals/Q_Table_Entries", q_table_size, episode)

        if avg_loss > 0:
            self.writer.add_scalar("3_RL_Internals/Avg_Loss", avg_loss, episode)

    def close(self):
        self.writer.flush()
        self.writer.close()


class QTrainer:
    """
    Agent d'entrainement par Q-Learning pour le jeu Snake.

    Cette classe gère le cycle de vie de l'apprentissage, incluant l'exploration
    via une stratagie Epsilon-Greedy, la mise à jour de la Q-Table via l'equation
    de Bellman, et le monitoring de performances via Tensorboard.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.9995,
    ):

        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_end
        self.decay = epsilon_decay

        self.encoder = StateEncoder()

        # Format: { "state_str": [q_straight, q_right, q_left] }
        self.q_table: Dict[str, List[float]] = {}

        # Configuration du monitoring
        log_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.monitor = RLMonitor(f"logs/train_{log_name}")

    def get_action_idx(self, state_key: str):
        """Choisit une action (0, 1, 2) selon la stratégie Epsilon-Greedy."""
        if random.random() < self.epsilon:
            return random.randint(0, 2)

        q_values: List[float] = self.q_table.get(state_key, [0.0, 0.0, 0.0])
        return np.argmax(q_values)

    def update_q_table(self, state_vec, action, reward, next_state_vec):
        """Applique l'équation de Bellman pour mettre à jour la Q-Table."""
        state_key = str(state_vec)
        next_state_key = str(next_state_vec)

        # Initialisation si état inconnu
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0, 0.0, 0.0]
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0.0, 0.0, 0.0]

        # Q-Learning : Q(s,a) = Q(s,a) + lr * [reward + gamma * max(Q(s',a')) - Q(s,a)]
        old_value = self.q_table[state_key][action]
        next_max = max(self.q_table[next_state_key])

        # Formule de Bellman
        new_value = old_value + self.lr * (reward + self.gamma * next_max - old_value)
        self.q_table[state_key][action] = new_value

        # Retourner l'erreur (Temporal Difference Error)
        return abs(new_value - old_value)

    def train(self, num_episodes: int = 10000, save_path: str = "data/q_table.msgpack"):
        """Fonction pour declencher l'entrainement"""
        print(f"Décollage de l'entraînement pour {num_episodes} épisodes...")

        for episode in range(num_episodes):
            episode_loss = []

            # Initilisation de l'état
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

                # 2. Conversion direction (Conversion relative -> absolue)
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

                # 4. EXÉCUTER LE PAS
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
                    reward = 1.0 if dist_after < dist_before else -1.5

                next_state_vec = self.encoder.encode(engine.get_state())
                loss = self.update_q_table(
                    state_vec, action_idx, reward, next_state_vec
                )
                episode_loss.append(loss)
                total_reward += reward

            avg_loss = sum(episode_loss) / len(episode_loss) if episode_loss else 0

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
                    len(self.q_table),
                    avg_loss,
                )
                self.monitor.writer.add_scalar(
                    "3_RL_Internals/Avg_Loss", avg_loss, episode
                )
        # 5. Sauvegarde finale
        self.monitor.close()
        self.save(save_path)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            msgpack.pack(self.q_table, f)
        print(f"✅ Modèle sauvegardé sous {path}")


if __name__ == "__main__":
    trainer: QTrainer = QTrainer()
    episodes: int = 15000
    if len(sys.argv) > 1:
        try:
            episodes = int(sys.argv[1])
        except ValueError:
            if "--episodes" in sys.argv:
                idx: int = sys.argv.index("--episodes")
                episodes = int(sys.argv[idx + 1])
    trainer.train(num_episodes=episodes)
