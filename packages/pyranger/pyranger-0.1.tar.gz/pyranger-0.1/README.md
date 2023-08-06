# PyRanger

A simple integration library for integrating with ranger service discovery framework

## Dependencies
* kazoo

## Usage

```
from pyranger import RangerClient

test_service = RangerClient('localhost:2181', "namespace", "service-name")
test_service.start()

...
...

cur_host = test_service.get_host()

```
