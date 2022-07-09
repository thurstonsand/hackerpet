# hackerpet

python bindings for the [hackerpet](https://docs.particle.io/reference/device-os/libraries/h/hackerpet_plus/) HTTP API. Code is fully documented, so see `src/hackerpet/__init__.py` for more information.

## Overview

Start communication by initializing a `Hackerpet` class. Since this opens a client session, it is the responsibility of the caller to eventually call `hackerpet.close()`.

It is possible to interact with the hackerpet in the following ways:

* `.status()`: Get current status of the hackerpet
* `.set_game(game: Game)`: set the currently playing game
* `set_max_kibbles(max_kibbles: MaxKibbles)`: set the max kibbles distributed in a day
* `set_dst(dst_on: bool)`: enable or disable DST
* `set_timezone(tz_offset: int)`: set timezone (-12, 13)
* `set_hub_mode(hub_mode: HubMode)`: set hub mode between `STAY_OFF`, `STAY_ON`, and `SCHEDULED`
* `set_schedule(schedule: Schedule)`: set weekday/weekend schedule when `HubMode == SCHEDULED`

# Dependencies

The only dependency for the project is [`aiohttp`](https://docs.aiohttp.org/en/stable/).