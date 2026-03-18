## 🗄️ Schéma des Données (Q-Table)

Le projet utilise un stockage binaire via **MessagePack** pour optimiser la rapidité de lecture de l'IA.

### Structure du fichier `q_table.msgpack`
| Composant | Type | Description |
| :--- | :--- | :--- |
| **Clé** | `String` | Représentation textuelle du tuple d'état (11 bits). |
| **Valeur** | `List[float]` | vecteur de 3 valeurs Q : `[Continuer, Droite, Gauche]`. |

### Encodage de l'état (11-bits)
L'agent ne voit pas les pixels, il reçoit un vecteur binaire calculé par `StateEncoder` :
1. **Danger** (3 bits) : Devant, Droite, Gauche.
2. **Direction** (4 bits) : Nord, Sud, Est, Ouest.
3. **Nourriture** (4 bits) : Proximité relative (Haut, Bas, Gauche, Droite).