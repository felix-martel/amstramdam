from amstramdam._types.game import RoundScore
from dataclasses import dataclass
from typing import TypedDict


class ScoringParams(TypedDict, total=False):
    time_param: int
    dist_param: int
    precision_mode: bool
    non_linear_bonus: bool
    non_linear_bonus_amount: float
    multiplier: int


@dataclass
class Scorer:
    time_param: int = 5
    dist_param: int = 500
    precision_mode: bool = False
    non_linear_bonus: bool = True
    non_linear_bonus_amount: float = 0.2
    multiplier: int = 1_000

    def get_time_score(self, duration: float) -> float:
        if self.precision_mode:
            return 0.
        return max(0., 1 - duration / self.time_param)

    def get_bonus(self, distance: float) -> float:
        if not self.non_linear_bonus:
            return 0.
        # Max bonus as a fraction of the score multiplier (so +200 bonus for a 0km
        # distance with the standard 1000km)
        t = self.non_linear_bonus_amount
        # Last n kilometers for the non-linear bonus
        g = self.non_linear_bonus_amount * self.dist_param
        return (t / g ** 2) * max(0., g - distance) ** 2

    def get_distance_score(self, distance: float) -> float:
        linear_score = max(0., 1 - distance / self.dist_param)
        score = linear_score + self.get_bonus(distance)
        return self.multiplier * score

    def score(self, distance: float, duration: float) -> RoundScore:
        distance_score = self.get_distance_score(distance)
        time_score = self.get_time_score(duration) * distance_score
        score = round(distance_score + time_score)
        return {
            "distance": distance,
            "duration": duration,
            "distance_score": distance_score,
            "time_score": time_score,
            "score": score,
        }