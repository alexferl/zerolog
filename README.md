# zerolog
Python logging with zero setup JSON output.

## Getting started

### Simple Logging Example

```python
from zerolog import log

log.print("Hello, World!")

# {"level":"debug","time":"2023-12-14T23:23:57.922Z","message":"Hello, World!"}
```
> Note: By default log writes to `sys.stderr.buffer` and the default log level for `log.print` is `debug`.

### Leveled Logging
#### Simple Leveled Logging Example

```python
from zerolog import log

log.info().msg("Hello, World!")

# {"level":"info","time":"2023-12-14T23:36:47.768Z","message":"Hello, World!"}
```

### Contextual Logging

```python
from zerolog import log

log.debug().str("scale", "kg").float("weight", 42.69).msg("measuring in kilogram")

log.debug().str("Name", "Olivier").send()

# {"level":"debug","scale":"kg","weight":42.69,"time":"2023-12-14T23:32:26.368Z","message":"measuring in kilogram"}
# {"level":"debug","Name":"Olivier","time":"2023-12-14T23:32:26.368Z"}
```

### Exception Logging
You can log exceptions using the `exc` method.

```python
from zerolog import log

try:
    1/0
except Exception as e:
    log.exc(e).msg("uh oh")

# {"level":"error","exception":"division by zero","time":"2023-12-14T23:59:04.061Z","message":"uh oh"}
```
> Note: The default field name for exceptions is `exception`, you can change this by setting
> `zerolog.ExceptionFieldName` to meet your needs.

#### Exception Logging with Stack Trace

```python
import zerolog
from zerolog import log, stacktrace


def main():
    zerolog.ExceptionStackMarshaler = stacktrace.marshal_stack

    try:
        outer()
    except Exception as e:
        log.error().stack().exc(e).msg("uh oh")


def inner():
    1/0


def middle():
    inner()


def outer():
    middle()


# {"level":"error","stack":[{"source": "/app/test.py", "line": "9", "func": "main"}, {"source": "/app/test.py", "line": "23", "func": "outer"}, {"source": "/app/test.py", "line": "19", "func": "middle"}, {"source": "/app/test.py", "line": "15", "func": "inner"}],"exception":"division by zero","time":"2023-12-15T00:28:04.255Z","message":"uh oh"}
```
> Note: `zerolog.ExceptionStackMarshaler` must be set in order for `stack` to output anything.

#### Logging Fatal Messages
```python
from zerolog import log

log.fatal().msg("this is very bad")

# {"level":"fatal","time":"2023-12-15T00:22:03.664Z","message":"this is very bad"}
# exit status 1
```
## Credits
Based on the excellent [zerolog](https://github.com/rs/zerolog) in Go.
