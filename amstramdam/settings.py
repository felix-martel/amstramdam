from pydantic import Field
from pydantic_settings import BaseSettings


class GameSettings(BaseSettings):
    score_multiplier: int = 1_000
    n_runs: int = 10
    run_duration: int = 10
    wait_duration: int = 5
    max_duration_for_time_bonus: int = 5
    max_distance_for_scoring: int = 500
    add_non_linear_bonus: bool = True
    max_distance_for_non_linear_bonus: int = 200
    allow_zoom: bool = False


class Settings(BaseSettings):
    game: GameSettings = Field(default_factory=GameSettings)


settings = Settings()
