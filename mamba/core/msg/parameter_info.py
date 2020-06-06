from typing import Any
import enum


class ParameterType(enum.Enum):
    Get = 0
    Set = 1


class ParameterInfo:
    def __init__(self,
                 provider: str,
                 param_id: str,
                 param_type: ParameterType,
                 signature: Any,
                 description: str = '') -> None:
        self.provider = provider
        self.id = param_id
        self.type = param_type
        self.signature = signature
        self.description = description

    def __str__(self):
        return f'[id: {self.id}, type: {self.type}, ' \
               f'signature: {self.signature}]'
