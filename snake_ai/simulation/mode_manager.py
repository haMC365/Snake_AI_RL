import copy
from enum import Enum
from snake_ai.engine.game import SnakeEngine


class GameMode(Enum):
    MANUAL = "manual"
    DUEL = "duel"


class ModeManager:
    def __init__(self, engine: SnakeEngine, duel_manager):
        self.mode = GameMode.MANUAL
        self.engine = engine
        self.duel_manager = duel_manager

    def start_duel(self):
        """Transition fluide : Capture l'état actuel pour le duel."""
        # 1. On récupère l'état EXACT du serpent manuel à cet instant
        current_state = self.engine.get_state()

        # 2. On injecte cet état dans les deux moteurs du duel
        # On utilise deepcopy pour que les deux serpents IA soient indépendants
        self.duel_manager.engine_astar.state = copy.deepcopy(current_state)
        self.duel_manager.engine_rl.state = copy.deepcopy(current_state)

        # 3. On synchronise aussi les références d'état dans le duel_manager
        self.duel_manager.state_astar = self.duel_manager.engine_astar.get_state()
        self.duel_manager.state_rl = self.duel_manager.engine_rl.get_state()

        self.mode = GameMode.DUEL
        print(f"🚀 Transition à l'étape {current_state.steps} : Duel activé !")
