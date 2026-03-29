"""
Ce module contient la logique pour les charts
"""

from typing import Any

import matplotlib.pyplot as plt


class LivePerformanceCharts:
    """
    Classe utilise pour montrer les performances
    """

    def __init__(self):
        plt.style.use("dark_background")
        self.fig, (self.ax_score, self.ax_eff, self.ax_time) = plt.subplots(
            3, 1, figsize=(6, 10)
        )
        plt.subplots_adjust(hspace=0.4)

        # On prépare les listes de données
        self.episodes = []
        self.astar_data: dict[str, list[Any]] = {
            "score": [],
            "efficiency": [],
            "time": [],
        }
        self.rl_data: dict[str, list[Any]] = {"score": [], "efficiency": [], "time": []}

        # --- CRÉATION DES OBJETS LIGNES ---
        # On crée les lignes une seule fois, on ne fera que mettre à jour leurs données
        (self.line_score_astar,) = self.ax_score.plot([], [], label="A*", color="cyan")
        (self.line_score_rl,) = self.ax_score.plot([], [], label="RL", color="orange")

        (self.line_eff_astar,) = self.ax_eff.plot([], [], color="cyan")
        (self.line_eff_rl,) = self.ax_eff.plot([], [], color="orange")

        (self.line_time_astar,) = self.ax_time.plot([], [], color="cyan")
        (self.line_time_rl,) = self.ax_time.plot([], [], color="orange")

        self._setup_axes()
        plt.ion()
        plt.show(block=False)

    def _setup_axes(self):
        self.ax_score.set_title("Score vs Épisodes")
        self.ax_eff.set_title("Efficacité du Chemin (Manhattan / Pas)")
        self.ax_time.set_title("Latence (ms) vs Épisodes")

        # On fixe l'axe Y de l'efficacité entre 0 et 1.1 pour plus de clarté
        self.ax_eff.set_ylim(0, 1.1)
        self.ax_score.legend(loc="upper left")

    def update_data(self, episode, astar_metrics, rl_metrics):
        # Enregistrement l'épisode actuel
        self.episodes.append(episode)

        # --- TRAITEMENT DUEL A* (Cyan) ---
        self.astar_data["score"].append(astar_metrics["score"])

        # Condition critique pour la survie
        if astar_metrics["alive"]:
            self.astar_data["efficiency"].append(astar_metrics.get("efficiency", 1.0))
            self.astar_data["time"].append(astar_metrics["avg_latency"] * 1000)
        else:
            # Utilisation du None pour que Matplotlib ARRETE de tracer la ligne
            self.astar_data["efficiency"].append(None)
            self.astar_data["time"].append(None)

        # --- TRAITEMENT DUEL RL (Orange) ---
        self.rl_data["score"].append(rl_metrics["score"])

        # Contition critique pour la survie
        if rl_metrics["alive"]:
            self.rl_data["efficiency"].append(rl_metrics.get("efficiency", 1.0))
            self.rl_data["time"].append(rl_metrics["avg_latency"] * 1000)
        else:
            # Utilisation du None pour "casser" la ligne orange ici
            self.rl_data["efficiency"].append(None)
            self.rl_data["time"].append(None)

        # --- MISE À JOUR ULTRA-RAPIDE (Inchangée) ---
        # Matplotlib gère les None automatiquement pour interrompre la ligne
        self.line_score_astar.set_data(self.episodes, self.astar_data["score"])
        self.line_score_rl.set_data(self.episodes, self.rl_data["score"])

        self.line_eff_astar.set_data(self.episodes, self.astar_data["efficiency"])
        self.line_eff_rl.set_data(self.episodes, self.rl_data["efficiency"])

        self.line_time_astar.set_data(self.episodes, self.astar_data["time"])
        self.line_time_rl.set_data(self.episodes, self.rl_data["time"])

        # Ajustement des axes
        for ax in [self.ax_score, self.ax_eff, self.ax_time]:
            ax.relim()
            ax.autoscale_view()

        self.fig.canvas.flush_events()
        plt.pause(0.001)
