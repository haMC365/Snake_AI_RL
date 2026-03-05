import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import numpy as np


class DuelManager:
    """
    Gère la confrontation en temps réel entre l'IA A* et l'IA RL.
    Exécute les décisions en parallèle pour optimiser les performances.
    """

    def __init__(self, engine_astar, engine_rl, astar_agent, rl_agent):
        self.engine_astar = engine_astar
        self.engine_rl = engine_rl
        self.astar_agent = astar_agent
        self.rl_agent = rl_agent

        # On garde une référence aux états actuels
        self.state_astar = engine_astar.get_state()
        self.state_rl = engine_rl.get_state()

        # Initialisation des stats
        self.start_time = time.time()
        self.astar_latencies = []
        self.rl_latencies = []
        self.astar_max_latency = 0.0
        self.rl_max_latency = 0.0

        # Pool de threads pour le vrai parallélisme
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _agent_step(self, agent, engine, latencies_list):
        """Méthode générique pour exécuter un pas d'agent avec mesure de temps."""
        state = engine.get_state()
        if not state.alive:
            return 0.0

        t0 = time.perf_counter()
        action = agent.get_action(state)
        dt = time.perf_counter() - t0

        engine.step(action)
        latencies_list.append(dt)
        return dt

    def _safe_agent_step(self, agent, engine, latencies_list):
        """
        Exécute un pas de jeu de manière sécurisée.
        Retourne la latence si l'agent est vivant, sinon 0.0.
        """
        state = engine.get_state()
        if not state or not state.alive:
            return 0.0

        try:
            t0 = time.perf_counter()
            action = agent.get_action(state)
            dt = time.perf_counter() - t0

            engine.step(action)
            latencies_list.append(dt)
            return dt
        except Exception as e:
            print(f"⚠️ Erreur lors du step d'un agent: {e}")
            return 0.0

    # --- Étape 2 : Sous-méthodes privées (Workers) ---

    def _step_astar(self):
        """Exécute un cycle de décision pour l'agent A*."""
        if not self.state_astar.alive:
            return

        start = time.perf_counter()
        # Calcul de l'action via l'algorithme A*
        action = self.astar_agent.get_action(self.state_astar)
        duration = time.perf_counter() - start

        # Mise à jour de la logique
        self.engine_astar.step(action)

        # Mise à jour des stats si présentes
        if self.stats_astar:
            self.stats_astar.record_decision_time(duration)
            self.stats_astar.increment_step()
            self.stats_astar.update_score(self.state_astar.score)
            if not self.state_astar.alive:
                self.stats_astar.finish()

    def _step_rl(self):
        """Exécute un cycle de décision pour l'agent RL."""
        if not self.state_rl.alive:
            return

        start = time.perf_counter()
        # Inférence via le modèle Reinforcement Learning
        action = self.rl_agent.get_action(self.state_rl)
        duration = time.perf_counter() - start

        # Mise à jour de la logique
        self.engine_rl.step(action)

        # Mise à jour des stats si présentes
        if self.stats_rl:
            self.stats_rl.record_decision_time(duration)
            self.stats_rl.increment_step()
            self.stats_rl.update_score(self.state_rl.score)
            if not self.state_rl.alive:
                self.stats_rl.finish()

    # --- Étape 3 : Synchronisation (Step Principal) ---

    def step(self):
        """Lance les calculs des deux agents en parallèle."""
        # Soumission des tâches au pool de threads
        future_astar = self.executor.submit(
            self._safe_agent_step,
            self.astar_agent,
            self.engine_astar,
            self.astar_latencies,
        )
        future_rl = self.executor.submit(
            self._safe_agent_step, self.rl_agent, self.engine_rl, self.rl_latencies
        )

        # Récupération des résultats (bloquant jusqu'à la fin des calculs)
        dt_astar = future_astar.result()
        dt_rl = future_rl.result()

        # Mise à jour des latences maximales
        if dt_astar > self.astar_max_latency:
            self.astar_max_latency = dt_astar
        if dt_rl > self.rl_max_latency:
            self.rl_max_latency = dt_rl

        # Rafraîchissement des états pour le renderer
        self.state_astar = self.engine_astar.get_state()
        self.state_rl = self.engine_rl.get_state()

    # --- Étape 4 : Shutdown ---

    def shutdown(self):
        """Arrête proprement l'executor à la fin du programme."""
        print("🛑 Arrêt du DuelManager (Threads)...")
        self.executor.shutdown(wait=True)

    def get_metrics(self):
        """Prépare le dictionnaire de métriques pour l'interface UI."""
        runtime = time.time() - self.start_time

        # Calcul des moyennes (évite division par zéro)
        avg_astar = np.mean(self.astar_latencies) if self.astar_latencies else 0.0
        avg_rl = np.mean(self.rl_latencies) if self.rl_latencies else 0.0

        return {
            "astar": {
                "score": getattr(self.state_astar, "score", 0),
                "steps": getattr(self.state_astar, "steps", 0),
                "avg_latency": float(avg_astar),
                "max_latency": float(self.astar_max_latency),
                "runtime": float(runtime),
            },
            "rl": {
                "score": getattr(self.state_rl, "score", 0),
                "steps": getattr(self.state_rl, "steps", 0),
                "avg_latency": float(avg_rl),
                "max_latency": float(self.rl_max_latency),
                "runtime": float(runtime),
            },
        }
