# Utilisation d'une image légère
FROM python:3.12-slim

# Installation de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Installation des dépendances (optimisé pour le cache Docker)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copie du code
COPY . .

# Commande par défaut
CMD ["uv", "run", "app/main.py"]