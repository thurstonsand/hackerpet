"""
Communicate with a
[hackerpet](https://docs.particle.io/reference/device-os/libraries/h/hackerpet_plus/)
via the Hackerpet class. See main() fn for example usage.

Functionality includes:
* status(): retrieve current status from hackerpet
* set_game(game: Game)
* set_max_kibbles(max_kibbles: MaxKibbles)
* set_dst(dst_on: bool)
* set_timezone(tz_offset: int)
* set_hub_mode(hub_mode: HubMode)
* set_schedule(schedule: Schedule)
"""

import json
from datetime import datetime, time
from enum import Enum, IntEnum, auto, unique
from typing import Any, Optional
from urllib.parse import urlparse

import aiohttp


class IllegalValue(ValueError):
    """Exception raised when an unexpected status value is received"""

    message: str

    def __init__(self, cls: type, value_provided: Any):
        """provide the enum and the illegal value"""

        self.message = f"illegal value provided for {cls.__name__}: {value_provided}"
        super().__init__(self.message)


class OutOfRange(IndexError):
    """Exception raised if a value is out of range from expected"""

    message: str

    def __init__(self, name: str, lower: int, upper: int, found: int):
        self.message = f"expected value {name} to be in range [{lower}, {upper}], but found {found}"
        super().__init__(self.message)

    @staticmethod
    def test_range(name: str, lower: int, upper: int, found: int):
        """helper function for testing if a value is out of range"""
        if found < lower or found > upper:
            raise OutOfRange(name, lower, upper, found)


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
        if mode_str.isdigit():
            return cls(int(mode_str))
        else:
            return HubMode._missing_(mode_str)


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
        if game_str.isdigit():
            return cls(int(game_str))
        else:
            return Game._missing_(game_str)


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


class Status:
    """current status of the hub"""

    _raw_body: Any

    def __init__(self, body: Any):
        self._raw_body = body

    def as_dict(self) -> dict[str, Any]:
        """represent Status as a simple dict"""
        return {
            k: getattr(self, k)
            for k, v in self.__class__.__dict__.items()
            if isinstance(v, property)
        }

    @property
    def time(self) -> datetime:
        """time as returned from the hackerpet"""
        return datetime.strptime(self._raw_body["time"], "%a %b %d %H:%M:%S %Y")

    @property
    def hub_mode(self) -> HubMode:
        """one of STAY_ON, STAY_OFF, SCHEDULE"""
        return HubMode.from_int_str(self._raw_body["hub_mode"])

    @property
    def game(self) -> Game | GameTransitioning:
        """the current game level being played, or if it is transitioning between levels"""
        prev_game = Game.from_int_str(self._raw_body["game_id_playing"])
        next_game = Game.from_int_str(self._raw_body["game_id_queued"])
        if prev_game == next_game:
            return next_game
        else:
            return GameTransitioning(prev_game, next_game)

    @property
    def hub_state(self) -> HubState:
        """one of Standby, Active"""
        return HubState(self._raw_body["hub_state"])

    @property
    def max_kibbles(self) -> MaxKibbles:
        """max kibbles the hackerpet will dispense in a day"""
        return MaxKibbles(self._raw_body["max_kibbles"])

    @property
    def timezone_offset(self) -> int:
        """timezone set on the hackerpet"""
        timezone_offset_str = self._raw_body["timezone"]
        try:
            return int(float(timezone_offset_str))
        except ValueError as err:
            raise IllegalValue(float, timezone_offset_str) from err

    @property
    def schedule(self) -> Optional[Schedule]:
        """only valid if hub_mode is SCHEDULED; what the current shedule is"""
        if self.hub_mode == HubMode.SCHEDULED:
            return Schedule.from_json(self._raw_body)
        else:
            return None


class Hackerpet:
    """
    Interact with the hackerpet hub.
    Provides a mechanism to get the current status,
    as well as a variety of ways to interact with the hub.
    """

    session: aiohttp.ClientSession
    url: str

    def __init__(
        self, session: aiohttp.ClientSession, url: str = "http://cleverpet.local"
    ):
        """
        Initializes communication with a hackerpet. it is the responsibility of the caller to
        eventually close the provided session.

        # Args
        session: a client session to communicate with the hackerpet.

        url: by default, the hackerpet starts with the url "http://cleverpet.local".
             This should not need an override except if a separate DNS entry is created,
             or if an IP is passed in directly
        """

        self.session = session
        parsed = urlparse(url)
        self.url = parsed._replace(scheme="http").geturl()

    async def status(self) -> Status:
        """retrieves and returns a Status from the hackerpet"""
        async with self.session.get(f"{self.url}/local-api") as response:
            return Status(await response.json(content_type=None))

    async def set_game(self, game: Game):
        """sets the Game level of the hackerpet"""

        async with self.session.post(
            f"{self.url}/local-api/set_game", json={"game": game.value}
        ):
            # response is always 200 with empty body
            # nothing to do here
            pass

    async def set_max_kibbles(self, max_kibbles: MaxKibbles):
        """sets the max number of kibbles dispensed a day"""

        async with self.session.post(
            f"{self.url}/local-api/set_max_kibbles",
            json={"max_kibbles": max_kibbles.value},
        ):
            # response is always 200 with empty body
            # nothing to do here
            pass

    async def set_dst(self, dst_on: bool):
        """enables or disables DST"""

        async with self.session.post(
            f"{self.url}/local-api/set_dst", json={"dst_on", 1 if dst_on else 0}
        ):
            # response is always 200 with empty body
            # nothing to do here
            pass

    async def set_timezone(self, tz_offset: int):
        """sets timezone offset of the hackerpet; validates value is between -12 and +13"""

        OutOfRange.test_range("timezone_offset", -12, 13, tz_offset)
        async with self.session.post(
            f"{self.url}/local-api/set_timezone", json={"timezone_offset": tz_offset}
        ):
            # response is always 200 with empty body
            # nothing to do here
            pass

    async def set_hub_mode(self, hub_mode: HubMode):
        """sets the hub mode of the hackerpet"""

        async with self.session.post(
            f"{self.url}/local-api/set_hub_mode", json={"hub_mode": hub_mode.value}
        ):
            # response is always 200 with empty body
            # nothing to do here
            pass

    async def set_schedule(self, schedule: Schedule):
        """
        sets the weekday/weekend schedule for the hackerpet.

        only valid if hackerpet is in "Schedule" HubMode.
        """

        async with self.session.post(
            f"{self.url}/local-api/set_schedule", data=schedule.payload()
        ):
            # response is always 200 with empty body
            # nothing to do here
            pass


async def main() -> int:
    """example that prints out current status of the hackerpet"""
    async with aiohttp.ClientSession() as session:
        hackerpet = Hackerpet(session)
        status = await hackerpet.status()
        print(status.as_dict())
    return 0
