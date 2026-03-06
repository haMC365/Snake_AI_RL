import numpy as np
import msgpack
import os
from typing import Dict
from snake_ai.core.game_state import GameState
from snake_ai.agents.rl.encoders import StateEncoder


class RLAgent:
    """
    Agent utilisant l'apprentissage par renforcement (Q-Learning).
    Il utilise une Q-Table pour décider de la meilleure action à prendre.
    """

    def __init__(self, model_path: str = "data/q_table.msgpack"):
        self.model_path = model_path
        self.encoder = StateEncoder()
        self.q_table = self._load_q_table()

        # Mapping des index d'actions (0, 1, 2) vers des directions relatives
        # 0: Continuer tout droit, 1: Tourner à droite, 2: Tourner à gauche
        self.actions = [0, 1, 2]

    def _load_q_table(self) -> Dict:
        """Charge la Q-Table depuis un fichier MsgPack."""
        if not os.path.exists(self.model_path):
            print(
                f"⚠️ Modèle non trouvé à {self.model_path}. Initialisation d'une table vide."
            )
            return {}

        with open(self.model_path, "rb") as f:
            # On utilise strict_map_key=False car les clés sont des tuples/strings
            return msgpack.unpack(f, strict_map_key=False)

    def load(self, path):
        """Charge la Q-Table depuis un fichier msgpack."""
        if os.path.exists(path):
            with open(path, "rb") as f:
                # msgpack.unpackb ou unpack selon ta version
                self.q_table = msgpack.unpack(f)
            print(f"✅ Q-Table chargée ({len(self.q_table)} états connus)")
        else:
            print(f"⚠️ Fichier {path} introuvable. Q-Table vide.")

    def get_action(self, state: GameState) -> str:
        """
        Détermine la meilleure direction (UP, DOWN, LEFT, RIGHT)
        en fonction de la Q-Table.
        """
        # 1. Encodage de l'état (le vecteur de 11 bits)
        state_key = str(self.encoder.encode(state))

        # 2. Récupération des valeurs Q pour cet état
        # Si l'état est inconnu, on initialise avec des zéros [0.0, 0.0, 0.0]
        q_values = self.q_table.get(state_key, [0.0, 0.0, 0.0])

        # 3. Choix de l'action avec la valeur Q maximale (Exploitation)
        action_idx = np.argmax(q_values)

        # 4. Conversion de l'action relative en direction absolue
        return self._get_direction_from_action(state.direction, action_idx)

    def _get_direction_from_action(self, current_dir: str, action_idx: int) -> str:
        """
        Convertit une action relative (0, 1, 2) en direction (UP, DOWN, LEFT, RIGHT).
        0: Tout droit
        1: Droite (horaire)
        2: Gauche (anti-horaire)
        """
        directions = ["UP", "RIGHT", "DOWN", "LEFT"]
        idx = directions.index(current_dir)

        if action_idx == 0:  # Tout droit
            return current_dir
        elif action_idx == 1:  # Tourner à droite
            new_idx = (idx + 1) % 4
            return directions[new_idx]
        elif action_idx == 2:  # Tourner à gauche
            new_idx = (idx - 1) % 4
            return directions[new_idx]

        return current_dir

    def update_model_path(self, new_path: str):
        """Permet de changer de modèle à la volée."""
        self.model_path = new_path
        self.q_table = self._load_q_table()
