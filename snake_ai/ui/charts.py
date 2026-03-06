import matplotlib.pyplot as plt


class LivePerformanceCharts:
    def __init__(self):
        # Configuration avec style sombre pour aller avec le jeu
        plt.style.use("dark_background")
        self.fig, (self.ax_score, self.ax_steps, self.ax_time) = plt.subplots(
            3, 1, figsize=(6, 10)
        )
        plt.subplots_adjust(hspace=0.4)

        # On prépare les listes de données
        self.episodes = []
        self.astar_data = {"score": [], "steps": [], "time": []}
        self.rl_data = {"score": [], "steps": [], "time": []}

        # --- CRÉATION DES OBJETS LIGNES ---
        # On crée les lignes une seule fois, on ne fera que mettre à jour leurs données
        (self.line_score_astar,) = self.ax_score.plot([], [], label="A*", color="cyan")
        (self.line_score_rl,) = self.ax_score.plot([], [], label="RL", color="orange")

        (self.line_steps_astar,) = self.ax_steps.plot([], [], color="cyan")
        (self.line_steps_rl,) = self.ax_steps.plot([], [], color="orange")

        (self.line_time_astar,) = self.ax_time.plot([], [], color="cyan")
        (self.line_time_rl,) = self.ax_time.plot([], [], color="orange")

        self._setup_axes()
        plt.ion()
        plt.show(block=False)

    def _setup_axes(self):
        self.ax_score.set_title("Score vs Épisodes")
        self.ax_steps.set_title("Pas vs Épisodes")
        self.ax_time.set_title("Latence (ms) vs Épisodes")
        self.ax_score.legend(loc="upper left")

    def update_data(self, episode, astar_metrics, rl_metrics):
        self.episodes.append(episode)

        # Mise à jour des listes internes
        self.astar_data["score"].append(astar_metrics["score"])
        self.astar_data["steps"].append(astar_metrics["steps"])
        self.astar_data["time"].append(astar_metrics["avg_latency"] * 1000)

        self.rl_data["score"].append(rl_metrics["score"])
        self.rl_data["steps"].append(rl_metrics["steps"])
        self.rl_data["time"].append(rl_metrics["avg_latency"] * 1000)

        # --- MISE À JOUR ULTRA-RAPIDE ---
        # On injecte les nouvelles données dans les lignes sans effacer l'axe
        self.line_score_astar.set_data(self.episodes, self.astar_data["score"])
        self.line_score_rl.set_data(self.episodes, self.rl_data["score"])

        self.line_steps_astar.set_data(self.episodes, self.astar_data["steps"])
        self.line_steps_rl.set_data(self.episodes, self.rl_data["steps"])

        self.line_time_astar.set_data(self.episodes, self.astar_data["time"])
        self.line_time_rl.set_data(self.episodes, self.rl_data["time"])

        # Ajustement automatique des limites des axes pour voir les courbes
        for ax in [self.ax_score, self.ax_steps, self.ax_time]:
            ax.relim()
            ax.autoscale_view()

        self.fig.canvas.flush_events()  # Plus rapide que plt.draw()
        plt.pause(0.001)
