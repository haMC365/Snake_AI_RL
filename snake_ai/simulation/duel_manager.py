import time
from concurrent.futures import ThreadPoolExecutor

# import numpy as np


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

        # Dictionnaire consolidé pour faciliter le transfert vers les charts
        self.metrics = {
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

        self.start_time = time.time()  # Pour le calcul du runtime
        self.astar_max_latency = 0.0  # Pour enregistrer le pire pic de l'A*
        self.rl_max_latency = 0.0  # Pour enregistrer le pire pic du RL

        # Pool de threads pour exécuter les deux cerveaux en même temps
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _agent_step(self, agent, engine, agent_key):
        """
        Exécute un pas pour un agent, mesure la performance et met à jour les états.
        agent_key doit être "astar" ou "rl".
        """
        state = engine.get_state()

        # Si le serpent est déjà mort, on ne fait rien
        if not state.alive:
            self.metrics[agent_key]["alive"] = False
            return 0.0

        # --- MESURE DE LA RÉFLEXION ---
        t0 = time.perf_counter()
        action = agent.get_action(state)
        dt = time.perf_counter() - t0

        # --- MISE À JOUR DU MOTEUR ---
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
        print("🛑 Arrêt du DuelManager (Threads)...")
        self.executor.shutdown(wait=True)

    def get_metrics(self):
        """Prépare le dictionnaire de métriques pour l'interface UI."""
        runtime = time.time() - self.start_time

        # On injecte le runtime et les pics de latence dans le dictionnaire déjà prêt
        self.metrics["astar"]["max_latency"] = float(self.astar_max_latency)
        self.metrics["astar"]["runtime"] = float(runtime)

        self.metrics["rl"]["max_latency"] = float(self.rl_max_latency)
        self.metrics["rl"]["runtime"] = float(runtime)

        # On retourne une copie pour éviter les problèmes de threads avec l'UI
        return {"astar": self.metrics["astar"].copy(), "rl": self.metrics["rl"].copy()}
