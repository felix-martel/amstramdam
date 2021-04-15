from typing import Optional, Union, Any, Iterator
import random
import string
from amstramdam._types.game import PlayerId, PlayerName


with open("data/player_names.txt", "r", encoding="utf8", errors="ignore") as file:
    PLAYER_NAMES: set[PlayerName] = {PlayerName(line.rstrip()) for line in file}


PlayerDict = dict[PlayerId, PlayerName]


class PlayerList:
    """
    Represent a list of players and their nicknames.
    Support:
    - adding/removing players
    - checking if player exists
    - changing or resetting nicknames

    Should I create a 'Player' class? or dataclass?
    """

    def __init__(self, game_name: str, players: Optional[PlayerDict] = None) -> None:
        self.game_name = game_name
        if players is None:
            players = {}
        self._players: PlayerDict = players
        self._available_names = self._get_available_names()

    def _get_available_names(self) -> set[PlayerName]:
        names = PLAYER_NAMES - self.names
        shuffled = random.sample(names, k=len(names))
        return set(shuffled)

    @property
    def ids(self) -> set[PlayerId]:
        """
        Return the set of player ids contained in `self`
        """
        return set(self._players.keys())

    @property
    def names(self) -> set[PlayerName]:
        """
        Return the set of player names contained in `self`
        """
        return set(self._players.values())

    def __repr__(self):
        return f"PlayerList(game={self.game_name})"

    def __contains__(self, item: Any) -> bool:
        return item in self._players

    def __getitem__(self, item: Any) -> PlayerName:
        if item not in self._players:
            raise KeyError(f"Unknown player <{item}> in {self}")
        return self._players[item]

    def _generate_id(self) -> PlayerId:
        uid = "".join(
            random.choices(
                string.ascii_lowercase + string.ascii_uppercase + string.digits, k=16
            )
        )
        return PlayerId(f"{self.game_name}_{uid}")

    @staticmethod
    def process_name(name: Union[str, PlayerName]) -> PlayerName:
        if len(name) > 20:
            name = name[:20]
        return PlayerName(name)

    def generate_id(self) -> PlayerId:
        pid = self._generate_id()
        while pid in self._players:
            pid = self._generate_id()
        return pid

    def generate_name(self) -> PlayerName:
        if self._available_names:
            name = self._available_names.pop()
        else:
            name = random.choice(list(PLAYER_NAMES))
        return PlayerName(name)

    def add(
        self, pid: Optional[PlayerId] = None, name: Optional[PlayerName] = None
    ) -> tuple[PlayerId, PlayerName]:
        if pid is not None:
            assert pid not in self, f"Player <{pid}> already exists in {self}"
        else:
            pid = self.generate_id()
        if name is None:
            name = self.generate_name()
        self._players[pid] = self.process_name(name)
        return pid, name

    def remove(self, pid: PlayerId) -> None:
        if pid not in self._players:
            return
        name = self._players[pid]
        if name in PLAYER_NAMES:
            self._available_names.add(name)
        del self._players[pid]

    def get_name(self, pid: PlayerId) -> PlayerName:
        return self[pid]

    def set_name(self, pid: PlayerId, name: Union[str, PlayerName]) -> None:
        if pid not in self:
            return
        self._set_name(pid, PlayerName(name))

    def _set_name(self, pid: PlayerId, name: PlayerName) -> None:
        new_name = self.process_name(name)
        if pid in self._players:
            former_name = self._players[pid]
            if former_name in PLAYER_NAMES:
                self._available_names.add(former_name)
        self._players[pid] = new_name

    def request_name(self, pid: PlayerId) -> PlayerName:
        name = self.generate_name()
        self.set_name(pid, name)
        return name

    def __iter__(self) -> Iterator[PlayerId]:
        return iter(self._players.keys())

    def __len__(self) -> int:
        return len(self._players)

    def __bool__(self) -> bool:
        return bool(len(self))

    def as_dict(self) -> dict[PlayerId, PlayerName]:
        return self._players
