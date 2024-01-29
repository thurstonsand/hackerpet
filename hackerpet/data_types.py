import json
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum, IntEnum, auto, unique
from typing import Any, Optional

from .exceptions import IllegalValue


@unique
class HubMode(IntEnum):
    """
    HubMode describes the rule governing whether hub should be enabled or disabled.

    STAY_OFF: hub is always off
    STAY_ON: hub is always on
    SCHEDULED: hub follows a schedule (set on device)
    """

    STAY_OFF = 0
    STAY_ON = 1
    SCHEDULED = 2

    @classmethod
    def _missing_(cls: type, value: Any) -> "HubMode":
        raise IllegalValue(cls, value)

    @classmethod
    def from_int_str(cls: type, mode_str: str) -> "HubMode":
        """converts str of int value to HubMode, or raise an IllegalStatus exception"""
        if not mode_str.isdigit():
            return HubMode._missing_(mode_str)
        return cls(int(mode_str))


@unique
class HubStatus(Enum):
    """
    HubStatus describes the current state of the hub.

    PLAYING: food is in the hub, and player can play
    EMPTY: no food in hub, player cannot play
    PLATTER_JAMMED: platter is jammed
    POD_JAMMED: pod is jammed
    DOME_REMOVED: dome has been removed
    """

    PLAYING = auto()
    EMPTY = auto()
    PLATTER_JAMMED = auto()
    POD_JAMMED = auto()
    DOME_REMOVED = auto()

    @classmethod
    def _missing_(cls: type, value: Any) -> "HubStatus":
        raise IllegalValue(cls, value)

    @staticmethod
    def from_status(status: str) -> "HubStatus":
        """converts message from hub to Status, or UNKNOWN if invalid"""

        if "Your hub is working" in status:
            return HubStatus.PLAYING
        elif "Out of food" in status:
            return HubStatus.EMPTY
        elif "Platter is jammed" in status:
            return HubStatus.PLATTER_JAMMED
        elif "Singulator is jammed" in status:
            return HubStatus.POD_JAMMED
        elif "Dome is removed" in status:
            return HubStatus.DOME_REMOVED
        else:
            return HubStatus._missing_(status)


@unique
class Game(IntEnum):
    """
    Game describes the specific game levels available to hackerpet.

    See the __str__ def for a brief description of each game level
    """

    GAME0 = 0
    GAME1 = 1
    GAME2 = 2
    GAME3 = 3
    GAME4 = 4
    GAME5 = 5
    GAME6 = 6
    GAME7 = 7
    GAME8 = 8
    GAME9 = 9
    GAME10 = 10
    GAME11 = 11

    def __str__(self) -> str:
        match self:
            case Game.GAME0:
                return "Eating the food"
            case Game.GAME1:
                return "Exploring the Touchpads"
            case Game.GAME2:
                return "Engaging Consistently"
            case Game.GAME3:
                return "Avoiding Unlit Touchpads"
            case Game.GAME4:
                return "Learning the Lights"
            case Game.GAME5:
                return "Mastering the Lights"
            case Game.GAME6:
                return "Responding Quickly"
            case Game.GAME7:
                return "Learning Brightness"
            case Game.GAME8:
                return "Learning Double Sequences"
            case Game.GAME9:
                return "Learning Longer Sequences"
            case Game.GAME10:
                return "Matching Two Colors"
            case Game.GAME11:
                return "Matching More Colors"

    @classmethod
    def _missing_(cls: type, value: Any) -> "Game":
        raise IllegalValue(Game, value)

    @classmethod
    def from_int_str(cls: type, game_str: str) -> "Game":
        """convert str of int value to Game, or `GAME_UNKNOWN` if invalid"""
        if not game_str.isdigit():
            return Game._missing_(game_str)
        return cls(int(game_str))


class GameTransitioning:
    """
    GameTransitioning describes a special state of Game where it is transitioning
    between two different games. It will remain in this state after a new game
    level has been chosen, and before the next round is played.
    """

    prev: Game
    next: Game
    value: int

    def __init__(self, prev_game: Game, next_game: Game):
        self.prev = prev_game
        self.next = next_game
        self.value = next_game.value

    def __str__(self) -> str:
        return f"game transitioning: {self.prev} -> {self.next}"

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__}: {self.prev.__repr__()} -> {self.next.__repr__()}>"
        )


@unique
class HubState(Enum):
    """
    Describes state of hub, as determined by the hub mode.

    STANDBY: hub is not dispensing food
    ACTIVE: hub is dispensing food if any is present
    """

    STANDBY = "Standby"
    ACTIVE = "Active"

    @classmethod
    def _missing_(cls: type, value: Any) -> str:
        raise IllegalValue(cls, value)


class MaxKibbles:
    """
    a limit on the number of kibbles dispensed in a day.

    If limit == 0 or None, disables limit
    """

    _limit: Optional[int]
    value: int

    def __init__(self, limit: Optional[int]):
        self._limit = limit
        self.value = limit if limit else 0

    def __str__(self) -> str:
        if self._limit == 0 or self._limit is None:
            return "no limit"
        else:
            return f"limit: {self._limit}"

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self.value}>"


class Schedule:
    """
    defines the schedule that the hackerpet will follow in "Scheduled" HubMode.

    Sets the schedule for weekdays and weekends separately
    """

    weekday_from: time
    weekday_to: time
    weekend_from: time
    weekend_to: time

    def __init__(
        self, weekday_from: time, weekday_to: time, weekend_from: time, weekend_to: time
    ):
        self.weekday_from = weekday_from
        self.weekday_to = weekday_to
        self.weekend_from = weekend_from
        self.weekend_to = weekend_to

    @staticmethod
    def _hm_format(tme: time) -> str:
        return tme.strftime("%H:%S")

    def __str__(self) -> str:
        return (
            "schedule: weekdays "
            f"{Schedule._hm_format(self.weekday_from)} - "
            f"{Schedule._hm_format(self.weekday_to)}; "
            f"weekends {Schedule._hm_format(self.weekend_from)} - "
            f"{Schedule._hm_format(self.weekend_to)}"
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}: "
            f"<weekday_from: {self.weekday_from.__repr__()}, "
            f"weekday_to: {self.weekday_to.__repr__()}, "
            f"weekend_from: {self.weekend_from.__repr__()}, "
            f"weekend_to: {self.weekday_to.__repr__()}>"
        )

    @classmethod
    def from_json(cls: type, payload: Any) -> "Schedule":
        """parse json response to instantiate Schedule"""
        weekday_from = payload["weekday_from"]
        weekday_to = payload["weekday_to"]
        weekend_from = payload["weekend_from"]
        weekend_to = payload["weekend_to"]
        return cls(weekday_from, weekday_to, weekend_from, weekend_to)

    def payload(self) -> str:
        """hackerpet expects this exact layout in json payload"""

        return json.dumps(
            {
                "weekday_from": Schedule._hm_format(self.weekday_from),
                "weekday_to": Schedule._hm_format(self.weekday_to),
                "weekend_from": Schedule._hm_format(self.weekend_from),
                "weekend_to": Schedule._hm_format(self.weekend_to),
            },
            separators=(",", ":"),
        )


@dataclass(frozen=True, slots=True)
class Status:
    """current status of the hub"""

    time: datetime
    hub_mode: HubMode
    game: Game | GameTransitioning
    hub_state: HubState
    max_kibbles: MaxKibbles
    timezone_offset: int
    schedule: Optional[Schedule]

    @classmethod
    def from_json(cls: type, raw_body: Any) -> "Status":
        """
        extract values from raw_body to populate the dataclass.
        must use object.__setattr__ due to dataclass being frozen.
        see https://docs.python.org/3/library/dataclasses.html#dataclasses.FrozenInstanceError # noqa: E501 # pylint: disable=line-too-long
        """
        # set time
        tme = datetime.strptime(raw_body["time"], "%a %b %d %H:%M:%S %Y")

        # set hub_mode
        hub_mode = HubMode.from_int_str(raw_body["hub_mode"])

        # set game
        prev_game = Game.from_int_str(raw_body["game_id_playing"])
        next_game = Game.from_int_str(raw_body["game_id_queued"])
        game = (
            (
                next_game
                if prev_game == next_game
                else GameTransitioning(prev_game, next_game)
            ),
        )

        # set hub_state
        hub_state = HubState(raw_body["hub_state"])

        # set max_kibbles
        max_kibbles = MaxKibbles(raw_body["max_kibbles"])

        # set timezone_offset
        timezone_offset_str = raw_body["timezone"]
        try:
            timezone_offset = int(float(timezone_offset_str))
        except ValueError as err:
            raise IllegalValue(float, timezone_offset_str) from err

        # set schedule
        schedule = (
            Schedule.from_json(raw_body) if hub_mode == HubMode.SCHEDULED else None
        )
        return cls(
            tme, hub_mode, game, hub_state, max_kibbles, timezone_offset, schedule
        )
