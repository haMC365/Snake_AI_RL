# --- CONFIGURATION DES VARIABLES ---
PYTHON	= uv run python
PYTEST	= uv run pytest
RUFF	= uv run ruff
TSB		= uv run tensorboard

# Valeurs par défaut pour l'entrainement
EPISODES  	= 20000
RENDER 		= true

.PHONY: help install run train monitor test lint benchmark clean

# --- COMMANDES ---
help: ## Affiche cette aide (liste toutes les commandes disponibles)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installe l'environnement et les dépendances (uv sync)
	uv sync

run: ## Lance le programme principal (Mode Manuel/Duel)
	$(PYTHON) main.py

train: ## Lance l'entraînement de l'IA (Usage: make train EPISODES=1000 RENDER=True)
	$(PYTHON) snake_ai/agents/rl/trainer.py --episodes $(EPISODES) --render $(RENDER)

monitor: ## Lance TensorBoard pour surveiller Epsilon, Reward et Loss
	@echo "Ouvrez votre navigateur sur http://localhost:6006"
	$(TSB) --logdir logs

test: ## Exécute la suite complète de tests unitaires (Pytest)
	$(PYTEST)

lint: ## Vérifie la qualité du code et applique le formatage (Ruff)
	$(RUFF) check . --fix
	$(RUFF) format .

benchmark: ## Génère le graphique comparatif A* vs RL (comparison_chart.png)
	$(PYTHON) benchmarks/run_duel_benchmark.py

check-vision: ## Script de diagnostic pour vérifier l'encodage 11-bits de l'IA
	$(PYTHON) scripts/check_encoder.py

clean: ## Nettoie les fichiers de cache Python et les fichiers temporaires
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "Nettoyage terminé."