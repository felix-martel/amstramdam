import random
from typing import Generator

from amstramdam.game.types import Player, Pseudo
from amstramdam import utils


NICKNAME_FILE = "data/player_names.txt"
with open("data/player_names.txt", "r", encoding="utf8", errors="ignore") as f:
    NICKNAMES: set[Pseudo] = {Pseudo(line.rstrip()) for line in f}
_global_player_list: set[Player] = set()


class PlayerList:
    """Store the list of players and their nicknames

    `PlayerList` contains methods to add/rename/remove players from the player list
    """

    def __init__(
        self,
        game_name: str,
        players: set[Player] | None = None,
        nicknames: dict[Player, Pseudo] | None = None,
    ) -> None:
        self.game_name = game_name
        self.ids: set[Player] = players if players is not None else set()
        if nicknames is not None:
            nicknames = {
                player: name for player, name in nicknames.items() if player in self.ids
            }
        self.nicknames: dict[Player, Pseudo] = (
            nicknames if nicknames is not None else dict()
        )
        self._available_names = list(NICKNAMES - set(self.nicknames.values()))

    def __len__(self) -> int:
        return len(self.ids)

    def __contains__(self, item: Player) -> bool:
        return item in self.ids

    def __iter__(self) -> Generator[Player, None, None]:
        yield from self.ids

    def generate_player_name(self) -> Player:
        return Player(f"{self.game_name}_{utils.random.generate_random_identifier(16)}")

    def pick_nickname(self) -> Pseudo:
        if self._available_names:
            nickname = random.choice(self._available_names)
            self._available_names.remove(nickname)
            return Pseudo(nickname)
        else:
            return random.choice(list(NICKNAMES))

    def format(self) -> str:
        nicknames = []
        for player in self.ids:
            nickname = self.get_nickname(player)
            if nickname and str(nickname) != str(player):
                nicknames.append(f"{player} ({nickname})")
            else:
                nicknames.append(player)
        return ",".join(nicknames)

    def add_nickname(self, player: Player, nickname: Pseudo) -> None:
        if player not in self.ids:
            pass
        if (
            player in self.nicknames
            and (old_nickname := self.nicknames[player]) in NICKNAMES
            and nickname != old_nickname
        ):
            # `old_nickname` is now available again
            self._available_names.append(old_nickname)
        self.nicknames[player] = nickname

    def request_nickname(self, player: Player) -> Pseudo:
        nickname = self.pick_nickname()
        self.add_nickname(player, nickname)
        return nickname

    def remove_nickname(self, player: Player) -> None:
        if player in self.nicknames:
            old_nickname = self.nicknames[player]
            del self.nicknames[player]
            if old_nickname in NICKNAMES:
                self._available_names.append(old_nickname)

    def get_nickname(self, player: Player) -> Pseudo:
        return self.nicknames.get(player, Pseudo(player))

    def add_player(
        self, player: Player | None = None, nickname: Pseudo | None = None
    ) -> tuple[Player, Pseudo]:
        if player is not None:
            assert (
                player not in _global_player_list and player not in self.ids
            ), f"Player {player!r} already exists"
        else:
            player = self.generate_player_name()
            # Do I need to check for collisions?
        self.ids.add(player)
        _global_player_list.add(player)
        if nickname is None:
            nickname = self.pick_nickname()
        self.add_nickname(player, nickname)
        return player, nickname

    def remove_player(self, name: Player) -> None:
        if name in _global_player_list:
            _global_player_list.remove(name)
        if name not in self.ids:
            return
        self.remove_nickname(name)
        self.ids.remove(name)
