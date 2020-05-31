import enum


class LogLevel(enum.Enum):
    Dev = 0
    Info = 1
    Warning = 2
    Error = 3


class Log:
    def __init__(self, level: LogLevel, message: str, source: str = ''):
        self.level = level
        self.message = message
        self.source = source
