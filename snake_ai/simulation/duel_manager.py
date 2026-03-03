from snake_ai.engine.game import SnakeEngine
from snake_ai.core.game_state import GameState

class DuelManager:
    def __init__(self):
        self.state_astar = None
        self.state_rl = None
        self.engine_astar = None
        self.engine_rl = None
        self.running = False

    def start(self, initial_state: GameState):
        """Initialise deux moteurs indépendants à partir d'un seul état."""
        # Clonage critique pour éviter que RL ne mange la pomme d'A*
        self.state_astar = initial_state.clone()
        self.state_rl = initial_state.clone()

        self.engine_astar = SnakeEngine(self.state_astar)
        self.engine_rl = SnakeEngine(self.state_rl)
        
        self.running = True

    def step(self):
        """Fait avancer les deux IA d'un pas."""
        if not self.running:
            return
            
        # Ici on appellera les agents plus tard :
        # action_astar = agent_astar.get_action(self.state_astar)
        # self.engine_astar.step(action_astar)
        pass