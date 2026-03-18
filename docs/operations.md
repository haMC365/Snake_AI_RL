# Structure de Guide de Commandes

## A. Gestion de l'Environnement (Installation)

```bash
# Installer les dependances (créé le venv et installe les libs de pyprojet.toml)
uv sync

# Mettre à jour les bibliotèques vers la dernière version compatible
uv lock -- upgrade

# Ajouter un nouvelle biblioteque (ex. numpy)
uv add numpy
```

## B. Execution du Programme
```bash
# Lancer le programme principal (Mode Manuel par defaut)
uv run main.py

# Note: Dans le programme, appuyez sur 'D' pour basculer en mode DUEL.
```

## C. Entrainement de l'IA (Training)
```bash
# Lancer un nouvel entrainement de l'agent RL
uv run python snake_ai/agents/rl/trainer.py

# Visualizer la progression de l'entrainement avec TensorBoard
uv run tensorboard --logdir=logs/
```

## D. Tests et Qualite du Code
```bash
# Lancer la suite complete de tests (pytest)
uv run pytest

# Lancer un test spécifique (ex: moteur de jeu)
uv run pytest tests/test_engine.py

# Vérifier la conformité du code (Linting avec Ruff)
uv run ruff check .
```

## E. Benchmarking et Compilation
```bash
# Lancer le benchmark de duel et generer la graphique de comparaison
uv run benchmarks/run_duel_benchmark.py

# (Optionnel) Contruire l'image Docker pour le déploiment
docker build -t snake-ai-rl
```