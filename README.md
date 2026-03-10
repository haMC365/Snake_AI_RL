# 🐍 Snake AI - Benchmarking Platform (RL vs A*)

Une plateforme de simulation de Snake haute performance conçue pour comparer l'intelligence humaine, les algorithmes de recherche de chemin classiques (**A***) et l'apprentissage par renforcement (**RL**).



## ✨ Fonctionnalités (Features)

Le projet **Snake AI** offre un environnement complet pour le développement et la comparaison d'algorithmes :

* **🕹️ Mode Manuel** : Jouez au serpent de manière classique avec les touches directionnelles ou ZQSD pour établir des scores de référence humains.
* **⚔️ Mode Duel Dynamique** : Basculez instantanément d'une partie humaine à une compétition d'IA en pressant une seule touche (`D`).
* **💾 Capture d'État (Snapshot)** : Système de clonage profond (`Deep Copy`) de l'état du jeu, garantissant que les deux IA démarrent avec une configuration identique (position, longueur, score).
* **🖥️ Affichage Split-Screen** : Visualisation en temps réel de deux moteurs de jeu côte à côte pour comparer visuellement les stratégies de l'A* et du RL.
* **🧠 Perception IA 11-bits** : Encodeur d'état optimisé permettant à l'agent de percevoir les dangers immédiats, sa direction actuelle et l'angle vers la nourriture.
* **🏗️ Architecture Découplée (MVC)** : Séparation stricte entre le **GameState** (données), le **SnakeEngine** (logique) et le **Renderer** (vue Pygame).
* **✅ Qualité Industrielle** : Intégration continue (CI) avec validation automatique des tests unitaires, formatage du code via `Ruff` et gestion des dépendances via `uv`.
---

## 🏗️ Structure du Projet

L'architecture est organisée selon le principe de **séparation des préoccupations** (SOC), garantissant que la logique de l'IA est totalement indépendante de l'affichage graphique.

```text
Snake_AI_RL/
├── .github/workflows/    # Pipelines CI/CD (Tests et Linting automatisés)
├── scripts/              # Outils de diagnostic (check_encoder, check_config)
├── tests/                # Suite de tests unitaires (pytest)
├── snake_ai/             # Code source principal
│   ├── core/             # Objets de données purs (GameState)
│   ├── engine/           # Moteur physique et règles du jeu (SnakeEngine)
│   ├── agents/           # Intelligence Artificielle
│   │   ├── rl/           # Agent Reinforcement Learning (Modèles, Encoders)
│   │   └── search/       # Agent A* (Pathfinding)
│   ├── simulation/       # Gestion des modes (Manual, Duel, ModeManager)
│   └── ui/               # Interface graphique et rendu (SnakeRenderer)
├── main.py               # Point d'entrée de l'application
├── pyproject.toml        # Configuration du projet et dépendances (uv)
└── uv.lock               # Verrouillage exact des versions Python
---
```

## 3. 🛠️ Prérequis Système (WSL / Linux)

Pour compiler et exécuter le projet avec le rendu graphique **Pygame**, vous devez installer les dépendances système liées à la gestion des médias, des polices et de la compilation Python.

### A. Mise à jour des dépôts
```test
sudo apt-get update
```
### B. Bibliothèques Multimédia (SDL2)
Ces bibliothèques permettent à Pygame d'ouvrir une fenêtre, de gérer le son et les entrées clavier/souris :

Bash
```
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev libportmidi-dev libjpeg-dev
```
                       
### C. Outils de Développement
Indispensables pour compiler certains modules Python et gérer le dépôt :

```
sudo apt-get install -y python3-dev build-essential curl git
```

> [!IMPORTANT]
> Note pour WSL : > 
> - Windows 11 (WSLg) : L'affichage est géré nativement. La fenêtre du jeu s'ouvrira directement sur votre bureau Windows.
> - Windows 10 : Si vous n'avez pas de serveur graphique configuré, vous devrez utiliser un serveur X (comme VcXsrv) ou exécuter les scripts en mode "headless" `(export SDL_VIDEODRIVER=dummy)`


## 4. 🚀 Installation Rapide

Nous utilisons **`uv`**, un gestionnaire de paquets Python ultra-rapide, pour garantir que tout le monde utilise exactement les mêmes versions de bibliothèques.

### A. Installer l'outil `uv`
Ouvrez votre terminal et exécutez la commande officielle d'installation :
```bash
# Téléchargement et installation
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Activation immédiate dans la session actuelle
source $HOME/.cargo/env
```
### B. Configurer le projet
Une fois uv installé, clonez le dépôt et laissez l'outil créer l'environnement virtuel et installer les dépendances (Pygame, Pytest, Ruff, etc.) automatiquement :

```bash
# 1. Cloner le projet
git clone https://github.com/haMC365/Snake_AI_RL
cd Snake_AI_RL

# 2. Créer l'environnement et installer les dépendances (lit le fichier uv.lock)
uv syn
```

### C. Vérifier l'installation
Pour être certain que tout est prêt, lancez une commande de test :
```bash
# Vérifie que uv reconnaît le projet et affiche la version
uv --version
```

> [!TIP]
> Pourquoi uv sync ? > Contrairement à pip install, cette commande supprime les paquets inutiles et s'assure que votre dossier .venv est une copie conforme de l'environnement de développement officiel.


## 5. 🧪 Compiler et Valider (Qualité du Code)

Avant de soumettre vos modifications ou de lancer la simulation, assurez-vous que votre environnement respecte les standards de qualité du projet.

### A. Exécuter les Tests Unitaires
Nous utilisons `pytest` pour valider la logique du moteur de jeu (`SnakeEngine`), les transitions de mode et l'intégrité du `GameState`.

```bash
# Lancer les tests unitaires (actuellement 8 tests validés)
uv run pytest
```
### B. Analyse Statique (Linting)
Nous utilisons Ruff, un linter ultra-rapide, pour garantir que le code suit les conventions Python (PEP 8) et éviter les erreurs courantes.

```bash
# Vérifier la conformité du code
uv run ruff check .
```

### C. Formatage Automatique
Si Ruff signale des erreurs de style (espaces, lignes vides, imports inutilisés), vous pouvez les corriger instantanément :

```bash
# Corriger automatiquement les erreurs de formatage
uv run ruff format .
uv run ruff check . --fix
```

> [!NOTE]
> Pipeline CI/CD : Chaque push sur GitHub déclenche automatiquement ces vérifications. Si pytest ou ruff échouent en local, votre Pull Request sera bloquée sur GitHub.

## 6. 🎮 Exécution et Commandes

Une fois l'installation validée, vous pouvez lancer les différents modules du projet via le point d'entrée principal.

### A. Lancer la Simulation (Mode Manuel)
Par défaut, le jeu démarre en mode manuel. C'est l'étape idéale pour tester la réactivité du moteur de jeu.

```bash
uv run python main.py
```

Commandes Clavier :
- Flèches Directionnelles : Diriger le serpent.
- Touche D : Déclencher le Mode Duel (Transition vers l'IA).
- Touche R : Redémarrer la partie.
- Échap : Quitter le jeu.

### B. Le Mode Duel (IA vs IA)
Lorsque vous pressez la touche D, le ModeManager capture l'état exact de votre partie et lance deux simulations en parallèle :

1. À gauche (A)* : Un algorithme de recherche de chemin qui calcule la route la plus courte vers la nourriture.

2. À droite (RL) : Un agent entraîné par Apprentissage par Renforcement qui prend des décisions basées sur son expérience.

### C. Outils de Diagnostic
Si vous développez de nouvelles fonctionnalités pour l'IA, utilisez ce script pour vérifier la perception de l'agent sans lancer l'interface graphique :

```bash
# Vérifie l'encodage binaire de l'état (11 bits)
uv run scripts/check_encoder.py
```

> [!TIP]
> Performance : Si vous trouvez que le serpent est trop lent ou trop rapide en mode manuel, vous pouvez ajuster les FPS dans la configuration du moteur de jeu.

## 8. 🧠 Architecture de l'IA (Encodeur)

Pour permettre à l'agent de **Reinforcement Learning (RL)** d'apprendre efficacement, nous utilisons un espace d'observation réduit à **11 dimensions**. Plutôt que de lui donner les pixels de l'écran, nous lui transmettons un vecteur binaire.

### L'Espace d'Observation (11 bits)

L'état du jeu est encodé selon trois catégories d'informations :

1. **Dangers Immédiats (3 bits)** :
   - Danger à 1 case devant.
   - Danger à 1 case à droite.
   - Danger à 1 case à gauche.

2. **Direction Actuelle (4 bits)** :
   - Le serpent va-t-il vers le Haut, le Bas, la Gauche ou la Droite ?

3. **Position de la Nourriture (4 bits)** :
   - La nourriture est-elle plus haut, plus bas, plus à gauche ou plus à droite que la tête ?



### Fonctionnement de l'Encodage

L'encodeur transforme les coordonnées du `GameState` en une série de `0` et de `1`. Par exemple, si le serpent se dirige vers un mur à droite et que la nourriture est en haut, le vecteur indiquera :
- `Danger Droite = 1`
- `Food Up = 1`

Cette abstraction permet à l'IA de généraliser son apprentissage : elle ne mémorise pas la grille, elle apprend des **concepts de survie** (ex: "Si danger devant, tourner à gauche ou à droite").

---

### Vérification Technique
Vous pouvez visualiser cet encodage en temps réel avec le script dédié :
```bash
uv run scripts/check_encoder.py
```

## 9. 🤝 Contribution

Les contributions sont les bienvenues ! Pour maintenir la qualité du projet, merci de suivre cette procédure :

1. **Créer une branche** : Utilisez un nom explicite (`feature/nom-de-la-feature` ou `fix/nom-du-bug`).
2. **Respecter le style** : Avant de commit, lancez `uv run ruff format .`.
3. **Valider les tests** : Aucun code ne sera accepté si `uv run pytest` ne retourne pas **8/8 PASS**.
4. **Pull Request** : Décrivez clairement vos changements et liez l'Issue correspondante le cas échéant.

---

## 10. 📄 Licence

Ce projet est sous licence **MIT**. Cela signifie que vous pouvez librement copier, modifier et distribuer le code, à condition de conserver la mention du copyright original.

---


> [!TIP]
> **Une question ?** N'hésitez pas à ouvrir une *Issue* sur le dépôt GitHub pour discuter d'une nouvelle idée ou signaler un bug rencontré sur WSL.
