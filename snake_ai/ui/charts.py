import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class LivePerformanceCharts:
    def __init__(self):
        # Configuration de la figure Matplotlib avec 3 sous-graphiques
        self.fig, (self.ax_score, self.ax_steps, self.ax_time) = plt.subplots(
            3, 1, figsize=(6, 10)
        )
        plt.subplots_adjust(hspace=0.4)

        # Données pour A*
        self.astar_episodes = []
        self.astar_scores = []
        self.astar_steps = []
        self.astar_times = []

        # Données pour RL
        self.rl_episodes = []
        self.rl_scores = []
        self.rl_steps = []
        self.rl_times = []

        self._setup_axes()
        plt.ion()  # Mode interactif ON
        plt.show()

    def _setup_axes(self):
        self.ax_score.set_title("Score vs Épisodes")
        self.ax_steps.set_title("Pas vs Épisodes")
        self.ax_time.set_title("Temps (ms) vs Épisodes")

    def update_data(self, episode, astar_metrics, rl_metrics):
        """Reçoit les métriques et met à jour les listes de données."""
        # A*
        self.astar_episodes.append(episode)
        self.astar_scores.append(astar_metrics["score"])
        self.astar_steps.append(astar_metrics["steps"])
        self.astar_times.append(astar_metrics["avg_latency"] * 1000)

        # RL
        self.rl_episodes.append(episode)
        self.rl_scores.append(rl_metrics["score"])
        self.rl_steps.append(rl_metrics["steps"])
        self.rl_times.append(rl_metrics["avg_latency"] * 1000)

        self._render_charts()

    def _render_charts(self):
        # Nettoyage et rafraîchissement des courbes
        for ax in [self.ax_score, self.ax_steps, self.ax_time]:
            ax.clear()

        self._setup_axes()

        # Courbes Score
        self.ax_score.plot(
            self.astar_episodes, self.astar_scores, label="A*", color="cyan"
        )
        self.ax_score.plot(self.rl_episodes, self.rl_scores, label="RL", color="orange")
        self.ax_score.legend()

        # Courbes Steps
        self.ax_steps.plot(self.astar_episodes, self.astar_steps, color="cyan")
        self.ax_steps.plot(self.rl_episodes, self.rl_steps, color="orange")

        # Courbes Latence
        self.ax_time.plot(self.astar_episodes, self.astar_times, color="cyan")
        self.ax_time.plot(self.rl_episodes, self.rl_times, color="orange")

        plt.pause(0.001)  # Nécessaire pour mettre à jour la fenêtre Matplotlib
