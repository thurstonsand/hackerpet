# hackerpet

[![GitHub Release](https://img.shields.io/github/release/thurstonsand/hackerpet?style=flat-square)](https://github.com/thurstonsand/hackerpet/releases)
[![GitHub license](https://img.shields.io/github/license/thurstonsand/hackerpet?style=flat-square)](https://github.com/thurstonsand/hackerpet/blob/main/LICENSE)


python bindings for the [hackerpet](https://docs.particle.io/reference/device-os/libraries/h/hackerpet_plus/) HTTP API. Code is fully documented, so see `src/hackerpet/__init__.py` for more information.

This is strictly a library, with no executable or CLI.

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

# Development

Here are a couple notes to help myself when trying to continue development, since I am a new Python dev.

## Local Development

To run, simply use:

```sh
poetry run python -m hackerpet
```

## Releasing

To tag a version for release, use `bumpver`:

```sh
bumpver update -t final --major/--minor/--patch
```

where 

* `-t final` describes which tag to use (between `alpha`, `beta`, `rc`, `post`, and `final`)
* `--major/--minor/--patch` describes which part of the version to bump
* Optionally use `-d` for dry-run
