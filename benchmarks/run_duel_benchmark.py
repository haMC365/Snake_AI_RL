"""
Ce module sert pour comparer visuellement le fonctionnement d'A* et RL
"""

import random
import numpy as np
import csv
import time
import copy
import os
import matplotlib.pyplot as plt
from snake_ai.core.game_state import GameState
from snake_ai.engine.game import SnakeEngine
from snake_ai.simulation.duel_manager import DuelManager
from snake_ai.agents.astar.astar_agent import AStarAgent
from snake_ai.agents.rl.rl_agent import RLAgent


# Étape 2 — Fixer Seed pour la reproductibilité
def set_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)


# Étape 3 — Fonction create_initial_state (Sans UI)
def create_initial_state(grid_size: int) -> GameState:
    center_y = grid_size // 2
    # On place le serpent au centre gauche pour laisser de l'espace
    snake = [(5, center_y), (4, center_y), (3, center_y)]

    # Position de la nourriture fixe pour le premier pas (sera randomisée par le moteur ensuite)
    food = (grid_size - 5, center_y)

    return GameState(
        snake=snake,
        direction="RIGHT",
        food=food,
        score=0,
        steps=0,
        alive=True,
        grid_width=grid_size,
        grid_height=grid_size,
    )


# Étape 4 — Fonction run_single_duel
# Dans run_single_duel
def run_single_duel(astar_agent, rl_agent, grid_size: int) -> dict:
    initial_state = create_initial_state(grid_size)
    engine_astar = SnakeEngine(copy.deepcopy(initial_state))
    engine_rl = SnakeEngine(copy.deepcopy(initial_state))

    duel = DuelManager(engine_astar, engine_rl, astar_agent, rl_agent)

    start_time = time.time()

    # On suit le dernier pas où une pomme a été mangée
    last_score_step_astar = 0
    last_score_step_rl = 0

    # Limite : si le serpent fait plus de cases qu'il n'y en a sur la grille
    # sans manger, on considère qu'il tourne en rond.
    limit = grid_size * grid_size

    while engine_astar.state.alive or engine_rl.state.alive:
        # Sauvegarde des scores AVANT le mouvement
        old_score_astar = engine_astar.state.score
        old_score_rl = engine_rl.state.score

        duel.step()

        # Mise à jour du marqueur de temps si une pomme est mangée
        if engine_astar.state.score > old_score_astar:
            last_score_step_astar = engine_astar.state.steps
        if engine_rl.state.score > old_score_rl:
            last_score_step_rl = engine_rl.state.steps

        # SÉCURITÉ ANTI-BOUCLE
        # On vérifie : "Pas actuel - Pas au moment de la dernière pomme > Limite"
        if engine_astar.state.alive:
            if (engine_astar.state.steps - last_score_step_astar) > limit:
                engine_astar.state.alive = False

        if engine_rl.state.alive:
            if (engine_rl.state.steps - last_score_step_rl) > limit:
                engine_rl.state.alive = False

    # --- CRUCIAL : Le dictionnaire de retour ---
    metrics = {
        "astar_score": engine_astar.state.score,
        "astar_steps": engine_astar.state.steps,
        "rl_score": engine_rl.state.score,
        "rl_steps": engine_rl.state.steps,
        "runtime": time.time() - start_time,
    }

    duel.shutdown()
    return metrics  # Indenté au même niveau que le début du 'while'


# Étape 6 — Statistiques
def compute_summary(results: list) -> dict:
    # On filtre les éventuels None pour ne garder que les dict valides
    valid_results = [r for r in results if r is not None]

    if not valid_results:
        print("❌ Erreur : Aucun résultat valide pour le résumé.")
        return {}

    summary = {}
    for key in valid_results[0].keys():
        values = [r[key] for r in valid_results]
        summary[f"{key}_mean"] = np.mean(values)
        summary[f"{key}_std"] = np.std(values)
    return summary


# Étape 7 — Export CSV
def export_csv(results: list, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    keys = ["game_id"] + list(results[0].keys())
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        for i, res in enumerate(results):
            row = {"game_id": i}
            row.update(res)
            writer.writerow(row)


# Étape de Visualisation
def plot_benchmark_results(results: list):
    astar_scores = [r["astar_score"] for r in results]
    rl_scores = [r["rl_score"] for r in results]

    plt.figure(figsize=(14, 6))

    # Graphique 1 : Histogramme de distribution
    plt.subplot(1, 2, 1)
    plt.hist(
        astar_scores,
        alpha=0.6,
        label=f"A* (Moy: {np.mean(astar_scores):.1f})",
        color="royalblue",
        bins=15,
    )
    plt.hist(
        rl_scores,
        alpha=0.6,
        label=f"RL (Moy: {np.mean(rl_scores):.1f})",
        color="seagreen",
        bins=15,
    )
    plt.title("Distribution des Scores")
    plt.xlabel("Score final")
    plt.ylabel("Nombre de parties")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend()

    # Graphique 2 : Évolution temporelle (Moyenne mobile)
    plt.subplot(1, 2, 2)
    plt.plot(astar_scores, color="royalblue", alpha=0.2, label="A* Brut")
    plt.plot(rl_scores, color="seagreen", alpha=0.2, label="RL Brut")

    # Lissage (moyenne mobile sur 5 parties)
    window = 5
    if len(results) >= window:
        astar_smooth = np.convolve(astar_scores, np.ones(window) / window, mode="valid")
        rl_smooth = np.convolve(rl_scores, np.ones(window) / window, mode="valid")
        plt.plot(
            range(window - 1, len(astar_scores)),
            astar_smooth,
            color="blue",
            linewidth=2,
            label="A* Tendance",
        )
        plt.plot(
            range(window - 1, len(rl_scores)),
            rl_smooth,
            color="green",
            linewidth=2,
            label="RL Tendance",
        )

    plt.title("Évolution des performances")
    plt.xlabel("Numéro de la partie")
    plt.ylabel("Score")
    plt.legend()

    plt.tight_layout()
    chart_path = "benchmarks/comparison_chart.png"
    plt.savefig(chart_path)
    print(f"📈 Graphique sauvegardé : {chart_path}")
    plt.show()


# Étape 5 & 8 — Point d’entrée
def run_benchmark(n_games: int, grid_size: int):
    print(
        f"🧪 Lancement du Benchmark : {n_games} duels | Grille {grid_size}x{grid_size}"
    )
    set_seeds(42)

    astar_agent = AStarAgent()
    rl_agent = RLAgent()

    model_path = "data/q_table.msgpack"
    if os.path.exists(model_path):
        rl_agent.load(model_path)  # Assure-toi que cette méthode existe dans RLAgent
        print(f"📖 Modèle RL chargé avec succès ({model_path})")
    else:
        print(
            "⚠️ ATTENTION : Aucun modèle trouvé à data/q_table.msgpack. Le RL joue au hasard !"
        )

    results = []
    start_bench = time.time()

    for i in range(n_games):
        metrics = run_single_duel(astar_agent, rl_agent, grid_size)
        results.append(metrics)
        if (i + 1) % 5 == 0:
            print(f"  🏁 Duel {i + 1}/{n_games} terminé...")

    total_time = time.time() - start_bench
    summary = compute_summary(results)

    # Export et Visualisation
    export_csv(results, "benchmarks/results.csv")

    print("\n" + "=" * 40)
    print(f"📊 RÉSULTATS GLOBAUX ({total_time:.1f}s)")
    print("=" * 40)
    print(
        f"A* Score Moyen : {summary['astar_score_mean']:.2f} (±{summary['astar_score_std']:.2f})"
    )
    print(f"A* Steps Moyens : {summary['astar_steps_mean']:.1f}")
    print("-" * 40)
    print(
        f"RL Score Moyen : {summary['rl_score_mean']:.2f} (±{summary['rl_score_std']:.2f})"
    )
    print(f"RL Steps Moyens : {summary['rl_steps_mean']:.1f}")
    print("=" * 40)

    plot_benchmark_results(results)


if __name__ == "__main__":
    # On commence par 50 parties pour avoir des stats fiables sans attendre trop longtemps
    run_benchmark(n_games=50, grid_size=20)
