# hackerpet

python bindings for the [hackerpet](https://docs.particle.io/reference/device-os/libraries/h/hackerpet_plus/) HTTP API. Code is fully documented, so see `src/hackerpet/__init__.py` for more information.

## Overview

Start communication by initializing a `Hackerpet` class. Since this opens a client session, it is the responsibility of the caller to eventually call `hackerpet.close()`.

It is possible to interact with the hackerpet in the following ways:

* `.status()`: Get current status of the hackerpet
