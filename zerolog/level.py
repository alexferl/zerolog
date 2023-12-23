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


DebugLevel = Level.DebugLevel
InfoLevel = Level.InfoLevel
WarnLevel = Level.WarnLevel
ErrorLevel = Level.ErrorLevel
FatalLevel = Level.FatalLevel
NoLevel = Level.NoLevel
Disabled = Level.Disabled
TraceLevel = Level.TraceLevel
