"""
Gestion des duels en temps réel entre A* et RL

Ce module fournit le 'Duel Manager', qui executé les décisions des deux agents
en parallèle via du multithreading, collecte les métriques de performance
(latence, score, étapes, etc.) et synchronise les états pour l'affichage.
"""

import time
from concurrent.futures import ThreadPoolExecutor

from typing import Any, Tuple

from snake_ai.engine.game import SnakeEngine
from snake_ai.agents.astar.astar_agent import AStarAgent
from snake_ai.agents.rl.rl_agent import RLAgent
from snake_ai.core.game_state import GameState


class DuelManager:
    """
    Gère la confrontation en temps réel entre l'IA A* et l'IA RL.
    Exécute les décisions en parallèle pour optimiser les performances.
    """

    def __init__(
        self,
        engine_astar: SnakeEngine,
        engine_rl: SnakeEngine,
        astar_agent: AStarAgent,
        rl_agent: RLAgent,
    ):
        self.engine_astar = engine_astar
        self.engine_rl = engine_rl
        self.astar_agent = astar_agent
        self.rl_agent = rl_agent

        self.last_food_pos: dict[str, Any] = {"astar": None, "rl": None}
        self.steps_at_food_spawn: dict[str, int] = {"astar": 0, "rl": 0}
        self.initial_dist: dict[str, int] = {"astar": 0, "rl": 0}

        # On garde une référence aux états actuels
        self.state_astar = engine_astar.get_state()
        self.state_rl = engine_rl.get_state()

        # Dictionnaire consolidé pour faciliter le transfert vers les charts
        self.metrics: dict[str, dict[str, Any]] = {
            "astar": {
                "score": 0,
                "steps": 0,
                "avg_latency": 0.0,
                "total_time": 0.0,
                "alive": True,
            },
            "rl": {
                "score": 0,
                "steps": 0,
                "avg_latency": 0.0,
                "total_time": 0.0,
                "alive": True,
            },
        }

        # Initilisation des métriques avec "efficiency"
        for key in ["astar", "rl"]:
            self.metrics[key]["efficiency"] = 1.0  # 100% au debut
            self.metrics[key]["eff_list"] = []  # Pour la moyenne glissante

        self.start_time = time.time()  # Pour le calcul du runtime
        self.astar_max_latency = 0.0  # Pour enregistrer le pire pic de l'A*
        self.rl_max_latency = 0.0  # Pour enregistrer le pire pic du RL

        # Pool de threads pour exécuter les deux cerveaux en même temps
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _get_manhattan(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
        """Retourne la distance de Manhattan"""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def _agent_step(
        self, agent: AStarAgent | RLAgent, engine: SnakeEngine, agent_key: str
    ):
        """
        Exécute un pas pour un agent, mesure la performance et met à jour les états.
        agent_key doit être "astar" ou "rl".
        """
        state: GameState = engine.get_state()

        # Si le serpent est déjà mort, on ne fait rien
        if not state.alive:
            self.metrics[agent_key]["alive"] = False
            return 0.0

        # ----- LOGIQUE D'EFFICATITE -----
        # Si la pomme a change de place, on enregistre la nouvelle distance de départ
        current_food = state.food
        if current_food != self.last_food_pos[agent_key]:
            self.last_food_pos[agent_key] = current_food
            self.steps_at_food_spawn[agent_key] = engine.state.steps
            self.initial_dist[agent_key] = self._get_manhattan(
                state.head(), current_food
            )

        # --- MESURE DE LA RÉFLEXION ---
        t0 = time.perf_counter()
        action = agent.get_action(state)
        dt = time.perf_counter() - t0

        # SAUVEGARDE du score AVANT le mouvement
        old_score: int = engine.state.score

        # Mise a jour du moter
        alive = engine.step(action)

        # --- MISE À JOUR DES MÉTRIQUES ---
        m = self.metrics[agent_key]
        m["steps"] += 1
        m["total_time"] += dt
        m["avg_latency"] = m["total_time"] / m["steps"]
        m["score"] = engine.state.score
        m["alive"] = alive

        # Mise à jour des références d'état pour le Renderer
        if agent_key == "astar":
            self.state_astar = engine.get_state()
        else:
            self.state_rl = engine.get_state()

        # Si une pomme est mangée, on calcule l'efficacité sur ce trajet
        if engine.state.score > old_score:
            steps_taken = engine.state.steps - self.steps_at_food_spawn[agent_key]
            if steps_taken > 0:
                # Ratio = Distance la plus courte / Pas réels
                eff = self.initial_dist[agent_key] / steps_taken
                m["eff_list"].append(min(1.0, eff))
                # Moyenne glissante sur les 10 dernières pommes
                m["efficiency"] = sum(m["eff_list"][-10:]) / len(m["eff_list"][-10:])

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
        """Lance les calculs des deux agents en parallèle et synchronise les résultats."""
        # 1. Soumission des tâches au pool de threads
        # On utilise "astar" et "rl" comme clés pour mettre à jour le dictionnaire metrics
        future_astar = self.executor.submit(
            self._agent_step, self.astar_agent, self.engine_astar, "astar"
        )
        future_rl = self.executor.submit(
            self._agent_step, self.rl_agent, self.engine_rl, "rl"
        )

        # 2. Récupération des résultats (attend que les deux agents aient fini de réfléchir)
        dt_astar = future_astar.result()
        dt_rl = future_rl.result()

        # 3. Mise à jour des latences maximales (Peak latency)
        # Optionnel : Utile pour diagnostiquer les ralentissements soudains de l'A*
        if dt_astar > self.astar_max_latency:
            self.astar_max_latency = dt_astar
        if dt_rl > self.rl_max_latency:
            self.rl_max_latency = dt_rl

        # 4. Vérification de fin de partie
        # Retourne False si les deux serpents sont morts
        return self.metrics["astar"]["alive"] or self.metrics["rl"]["alive"]

    # --- Étape 4 : Shutdown ---

    def shutdown(self):
        """Arrête proprement l'executor à la fin du programme."""
        print("Arrêt du DuelManager (Threads)...")
        self.executor.shutdown(wait=True)

    def get_metrics(self):
        """Prépare le dictionnaire de métriques pour l'interface UI."""
        runtime = time.time() - self.start_time

        # Mise à jour des métriques temporelles
        for key in ["astar", "rl"]:
            self.metrics[key]["max_latency"] = float(
                self.astar_max_latency if key == "astar" else self.rl_max_latency
            )
            self.metrics[key]["runtime"] = float(runtime)

        # On retourne une copie profonde pour éviter les conflits de lecture/écriture entre threads
        return {"astar": {**self.metrics["astar"]}, "rl": {**self.metrics["rl"]}}
