from enum import IntEnum

import zerolog


class Level(IntEnum):
    # DebugLevel defines debug log level.
    DebugLevel = 0
    # InfoLevel defines info log level.
    InfoLevel = 1
    # WarnLevel defines warn log level.
    WarnLevel = 2
    # ErrorLevel defines error log level.
    ErrorLevel = 3
    # FatalLevel defines fatal log level.
    FatalLevel = 4
    # NoLevel defines an absent log level.
    NoLevel = 5
    # Disabled disables the logger.
    Disabled = 6

    # TraceLevel defines trace log level.
    TraceLevel = -1

    def string(self):
        match self:
            case self.TraceLevel:
                return zerolog.LevelTraceValue
            case self.DebugLevel:
                return zerolog.LevelDebugValue
            case self.InfoLevel:
                return zerolog.LevelInfoValue
            case self.WarnLevel:
                return zerolog.LevelWarnValue
            case self.ErrorLevel:
                return zerolog.LevelErrorValue
            case self.FatalLevel:
                return zerolog.LevelFatalValue
            case self.Disabled:
                return "disabled"
            case self.NoLevel:
                return ""

    def __str__(self):
        return self.string()


# parse_level converts a level string into a zerolog Level value.
# raises an exception if the input string does not match known values.
def parse_level(level_str: str) -> Level:
    match level_str:
        case zerolog.LevelTraceValue:
            return TraceLevel
        case zerolog.LevelDebugValue:
            return DebugLevel
        case zerolog.LevelInfoValue:
            return InfoLevel
        case zerolog.LevelWarnValue:
            return WarnLevel
        case zerolog.LevelErrorValue:
            return ErrorLevel
        case zerolog.LevelFatalValue:
            return FatalLevel
        case "disabled":
            return Disabled
        case "":
            return NoLevel
        case _:
            raise Exception(f"{level_str} is not valid")


TraceLevel = Level.TraceLevel
DebugLevel = Level.DebugLevel
InfoLevel = Level.InfoLevel
WarnLevel = Level.WarnLevel
ErrorLevel = Level.ErrorLevel
FatalLevel = Level.FatalLevel
NoLevel = Level.NoLevel
Disabled = Level.Disabled
