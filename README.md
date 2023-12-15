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
# {"level":"debug","Name":"Olivier","time":"2023-12-14T23:32:26.368Z"}a
```

# Credit
Based on the excellent [zerolog](https://github.com/rs/zerolog) in Go.
