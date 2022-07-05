"""
Communicate with a [hackerpet](https://docs.particle.io/reference/device-os/libraries/h/hackerpet_plus/)
via the Hackerpet class. See main() fn for example usage.

Functionality includes:
* retrieve current status from hackerpet
"""

from typing import Any
from urllib.parse import urlparse
from datetime import datetime
from enum import Enum, auto, unique
import aiohttp


@unique
class HubMode(Enum):
    """
    HubMode describes the rule governing whether hub should be enabled or disabled.

    STAY_OFF: hub is always off
    STAY_ON: hub is always on
    SCHEDULED: hub follows a schedule (set on device)
    """

    STAY_OFF = 0
    STAY_ON = 1
    SCHEDULED = 2
    UNKNOWN = 99

    @staticmethod
    def from_int_str(mode_str: str) -> "HubMode":
        """converts str of int value to HubMode, or `UNKNOWN` if invalid"""

        match int(mode_str) if mode_str.isdigit() else HubMode.UNKNOWN.value:
            case mode if 1 <= mode <= 3:
                return HubMode(mode)
            case _:
                return HubMode.UNKNOWN


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
    UNKNOWN = auto()

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
            print(f"unknown status: {status}")
            return HubStatus.UNKNOWN


@unique
class Game(Enum):
    """
    Game describes the game level that the hub is set to.

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
    GAME_UNKNOWN = 99

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
            case Game.GAME_UNKNOWN:
                return "Unknown"

    @staticmethod
    def from_int_str(game_str: str) -> "Game":
        """convert str of int value to Game, or `GAME_UNKNOWN` if invalid"""
        match int(game_str) if game_str.isdigit() else Game.GAME_UNKNOWN.value:
            case game if 0 <= game <= 11:
                return Game(game)
            case _:
                return Game.GAME_UNKNOWN


@unique
class HubState(Enum):
    """
    Describes state of hub, as determined by the hub mode.

    STANDBY: hub is not dispensing food
    ACTIVE: hub is dispensing food if any is present
    """

    STANDBY = "Standby"
    ACTIVE = "Active"


class Status:
    """Current status of the hub"""

    def __init__(self, body: Any) -> None:
        self.time = datetime.strptime(body["time"], "%a %b %d %H:%M:%S %Y")
        self.hub_mode = HubMode.from_int_str(body["hub_mode"])
        self.hub_status = HubStatus.from_status(body["status"])
        self.game = Game.from_int_str(body["game_id_playing"])
        self.hub_state = HubState(body["hub_state"])


class Hackerpet:
    """
    Interact with the hackerpet hub.
    Provides a mechanism to get the current status,
    as well as a variety of ways to interact with the hub.
    """

    def __init__(self, url: str = "http://cleverpet.local") -> None:
        """
        Initializes communication with a hackerpet. Since it starts a client session,
        but does not close it, it is the responsibility of the caller to eventually
        call `await hackerpet.close()`.

        # Args
        url: by default, the hackerpet starts with the url "http://cleverpet.local".
             This should not need an override except if a separate DNS entry is created,
             or if an IP is passed in directly
        """

        self.session = aiohttp.ClientSession()
        parsed = urlparse(url)
        self.url = parsed._replace(scheme="http").geturl()

    async def close(self) -> None:
        """closes the client session with the hackerpet"""
        await self.session.close()

    async def status(self) -> Status:
        """retrieves and returns a Status from the hackerpet"""
        async with self.session.get(f"{self.url}/local-api") as response:
            return Status(await response.json(content_type=None))


async def main() -> int:
    h = Hackerpet()
    status = await h.status()
    print(vars(status))
    await h.close()
    return 0
