from urllib.parse import urlparse

from aiohttp_retry import ExponentialRetry, RetryClient
from aiohttp_retry.types import ClientType

from hackerpet.data_types import Game, HubMode, MaxKibbles, Schedule, Status
from hackerpet.exceptions import OutOfRange


class Hackerpet:
    """
    Interact with the hackerpet hub.
    Provides a mechanism to get the current status,
    as well as a variety of ways to interact with the hub.
    """

    session: RetryClient
    url: str

    def __init__(self, session: ClientType, url: str = "http://cleverpet.local"):
        """
        Initializes communication with a hackerpet. it is the responsibility of the
        caller to eventually close the provided `session`.

        # Args
        `session`: a client session to communicate with the hackerpet. If the caller
        wants to customize the retry logic, instantiate a `RetryClient` and pass
        that in for `session`

        `url`: by default, the hackerpet starts with the url "http://cleverpet.local".
             This should not need an override except if a separate DNS entry is created,
             or if an IP is passed in directly
        """
        if isinstance(session, RetryClient):
            self.session = session
        else:
            opts = ExponentialRetry(attempts=3, max_timeout=5)
            self.session = RetryClient(client_session=session, retry_options=opts)

        parsed = urlparse(url)
        self.url = f"http://{parsed.path if parsed.path else parsed.netloc}"

    async def status(self) -> Status:
        """retrieves and returns a Status from the hackerpet"""
        async with self.session.get(f"{self.url}/local-api") as response:
            return Status.from_json(await response.json(content_type=None))

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
        """
        sets timezone offset of the hackerpet;
        validates value is between -12 and +13
        """
        OutOfRange.check_range("timezone_offset", -12, 13, tz_offset)
        async with self.session.post(
            f"{self.url}/local-api/set_timezone",
            json={"timezone_offset": tz_offset},
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
