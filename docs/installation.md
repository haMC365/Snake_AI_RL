# Guide d'Installation (WSL2/Ubuntu)

Ce guide détaille les étapes pour configurer l'environnement de développement de zéro, particulierement si vous utilisez Windows Subsystem for Linux (WSL2)

## 1. Prérequis Système (Ubuntu/Debian)
Avant d'installer les biblioteques de Python, vous devez installer les dépendances système necessaires pour le rendu graphique de Pygame et les outils de build.

Executer la commande suivante dans le terminal Ubuntu:
```bash
sudo apt update && sudo apt install -y \
    libgl1-mesa-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libavformat-dev \
    libswscale-dev \
    python3-dev \
    build-essential
```

**Note pour WSL2:** Assurez-vous que votre version de windows est à jour (Windows 10 21H2+ ou Windows 11) pour beneficier du support natif de WSLf (affichage des fenêtres Linux sur Windows)


## 2. Installation de Gestionnaire de Paquets `uv`
Nous utilisons `uv` pour garantir que tout le monde utilise exactement les mêmes versions de bibliotèques (via le fichier `uv.lock`)
- **Installer** `uv`:
  ```bash
  curl -LsSF https://astral.sh/uv/install.sh | sh
  ```

- **Redemarrer le terminal** ou lancer `source $HOME/.cargo/env`.


## 3. Configuration du Projet
Une fois le dépot cloné et les dépendances système installées:

1. **Navigueur dans le dossier**:
    ```bash
    cd snake_ai_rl
    ```

2. **Synchroniser l'evennement**:
    ```bash
    uv sync
    ```
    *Cette commande crée unvironement virtuel (`.venv`) et installe automatiquement toutes les dépendances (Pygame, Numpy, Msgpack, etc)* 

## 4. Vérification de l'installation
Pour vérifier que l'environnement est opérationnel, lancer la suite de tests:
```bash
uv run pytest
```