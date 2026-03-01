from torch.utils.tensorboard import SummaryWriter


class RLMonitor:
    def __init__(self, log_dir="logs/run_1"):
        # Le SummaryWriter est l'outil qui écrit les données
        self.writer = SummaryWriter(log_dir)

    def log_metrics(self, step, reward, epsilon, q_variance):
        """Enregistre les indicateurs clés à chaque étape."""
        self.writer.add_scalar("Reward/Total", reward, step)
        self.writer.add_scalar("Exploration/Epsilon", epsilon, step)
        self.scalar("Convergence/Q_Variance", q_variance, step)

    def close(self):
        self.writer.close()
