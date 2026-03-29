import json
import msgpack
import os


def migrate():
    json_path = "data/q_table.json"
    msgpack_path = "data/q_table.msgpack"

    if os.path.exists(json_path):
        # 1. Lire le JSON
        with open(json_path, "r") as f:
            data = json.load(f)

        # 2. Convertir et sauvegarder en Msgpack
        with open(msgpack_path, "wb") as f:
            f.write(msgpack.packb(data))

        print(f"Migration réussie : {json_path} -> {msgpack_path}")
    else:
        print("Erreur : Le fichier data/q_table.json est introuvable.")


if __name__ == "__main__":
    migrate()
