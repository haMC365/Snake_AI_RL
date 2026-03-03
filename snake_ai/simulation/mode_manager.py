from enum import Enum
from snake_ai.engine.game import SnakeEngine


class GameMode(Enum):
    MANUAL = "manual"
    DUEL = "duel"


class ModeManager:
    """
    Chef d'orchestre de la simulation.
    Bascule entre le contrôle humain et la compétition IA.
    """

    def __init__(self, engine: SnakeEngine, duel_manager):
        self.mode = GameMode.MANUAL
        self.engine = engine
        self.duel_manager = duel_manager

    def start_duel(self):
        """Transition du mode manuel vers le duel d'IA."""
        # 1. On capture l'instant T (clone profond pour l'indépendance)
        initial_state = self.engine.get_state_clone()

        # 2. On injecte cet état dans le gestionnaire de duel
        self.duel_manager.start(initial_state)

        # 3. On bascule officiellement le mode
        self.mode = GameMode.DUEL
        print("🚀 Transition : Mode Duel activé !")
