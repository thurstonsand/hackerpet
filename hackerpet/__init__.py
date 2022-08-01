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
__version__ = "0.0.1-alpha"

__all__ = ["data_types", "exceptions", "hackerpet"]

# pylint: disable=useless-import-alias
from .data_types import Game as Game
from .data_types import GameTransitioning as GameTransitioning
from .data_types import HubMode as HubMode
from .data_types import HubState as HubState
from .data_types import HubStatus as HubStatus
from .data_types import MaxKibbles as MaxKibbles
from .data_types import Schedule as Schedule
from .data_types import Status as Status
from .exceptions import IllegalValue as IllegalValue
from .exceptions import OutOfRange as OutOfRange
from .hackerpet import Hackerpet as Hackerpet


async def main() -> int:
    """example that prints out current status of the hackerpet"""
    # pylint: disable=import-outside-toplevel
    import aiohttp

    async with aiohttp.ClientSession() as session:
        hackerpet = Hackerpet(session, url="cleverpet.thurstons.house")
        status = await hackerpet.status()
        print(status)
    return 0
