import enum


class LogLevel(enum.Enum):
    Dev = 0
    Info = 1
    Warning = 2
    Error = 3


class Log:
    def __init__(self, level: LogLevel, msg: str, src: str = '') -> None:
        self.level = level
        self.msg = msg
        self.src = src
