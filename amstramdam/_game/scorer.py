"""
Given a distance and a time, return a score

The score is based on two variables:
- the distance `d` between the player's guess and the actual answer, expressed in
kilometers
- the time elapsed `t` from the start of the round and to the moment the guess was
received by the server, in seconds

Each `Scorer` has three main parameters: `M`, `D`, `T` (the actual attributes are
`multiplier`, `dist_param`, `time_param`, but we're trying to keep legible here).
The score is made of two parts: a distance-related score `s(d)`, and a time bonus
`b(d, t)`. Those two scores are multiplied by the multiplier `M`, so the final score is:
```
S(d, t) = M * (s(d) + b(d, t))
```
If the distance `d` is greater than `D`, then the player scores zero point. If the
elapsed time `t` is greater than `T`, then the player receives no time bonus.

# Computing the distance score

If the distance `d` is greater than `D`, then the player's score is zero, no matter how
much time elapsed. If non-linear bonuses are not activated, the score is linear from 0
to 1: `d = D` gives a score of zero, and `d = 0` gives a score of 1. For example, if
`D = 500 km` (the default), distances of 250 km and 100 km grants you scores of 0.5 and
0.8, respectively. If non-linear bonuses are activated, precise answers are granted
more than 1 point. The amount of points above 1 you can get is controlled by a parameter
`g` (attribute name is `non_linear_bonus_amount`). For a non-linear bonus of t=20%,
a distance of 0 grants 1.2 points. Finally, we have:
```
s(d) = s_linear(d) + s_bonus(d)
s_linear(d) = max(0, (d - D) / D)
s_bonus(d) = (g / (g * D) ** 2) * max(0., g - distance / D) ** 2
```

# Computing the time score

We first compute a linear score between 0 (for an elapsed time greater than `T`) to 1
(for instantaneous answers), then we multiply this score by the distance score
(otherwise, clicking randomly on the map could be a winning strategy!). The function is:
```
b(d, t) = s(d) * max(0, (t - T) / T)
```

# Precision mode

In precision mode, no time bonus are awarded.


# In practice

In practice, with the standard multiplier `M = 1_000`, 1000 is considered a good score
and 1500 a very good score. On the full 10-round game, scoring 10_000 points is very
good, and 15_000 is very, very challenging!
"""

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
            return 0.0
        return max(0.0, 1 - duration / self.time_param)

    def get_bonus(self, distance: float) -> float:
        if not self.non_linear_bonus:
            return 0.0
        # Max bonus as a fraction of the score multiplier (so +200 bonus for a 0km
        # distance with the standard 1000km)
        t = self.non_linear_bonus_amount
        # Last n kilometers for the non-linear bonus
        g = self.non_linear_bonus_amount * self.dist_param
        return (t / g ** 2) * max(0.0, g - distance) ** 2

    def get_distance_score(self, distance: float) -> float:
        linear_score = max(0.0, 1 - distance / self.dist_param)
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
