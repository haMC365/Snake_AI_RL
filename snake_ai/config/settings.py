from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class RLSettings(BaseSettings):
    # --- Hyperparamètres de Reinforcement Learning ---
    alpha: float = Field(
        default=0.1, description="Taux d'apprentissage (Learning Rate)"
    )
    gamma: float = Field(
        default=0.9, description="Facteur de réduction (Discount Factor)"
    )
    epsilon: float = Field(default=1.0, description="Taux d'exploration initial")
    epsilon_min: float = Field(default=0.01, description="Taux d'exploration minimum")
    epsilon_decay: float = Field(
        default=0.995, description="Vitesse de réduction de l'exploration"
    )

    # --- Configuration du Jeu ---
    block_size: int = 20
    speed: int = 40

    # Gestion des variables d'environnement (optionnel)
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SNAKE_")


# Instance globale pour accès facile
settings = RLSettings()
