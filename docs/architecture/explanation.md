# Architecture
## Approche
- *Version Initiale*: Heritage Classique
  - Base Agent (Classe Abstraite): définit la méthode `get_action()`
  - AStarAgent: Herite de Base_Agent
  - ATableAgent (RLAgent): Herite de Base_Agent

- *Version Actuelle*: Approche Composition et Decouplage
  - RLAgent poosède son propre `StateEncoder` et la logique de chargement `msgpack`, tandis qu'`AStarAgent` utilise une logique algorithmique pure. 