# Mamba exceptions
from typing import Optional


class ComponentConfigException(Exception):
    def __init__(self, msg: Optional[str] = None) -> None:
        super(ComponentConfigException, self).__init__(msg or "Component configuration error")


class LaunchFileException(Exception):
    def __init__(self, msg: Optional[str] = None) -> None:
        super(LaunchFileException, self).__init__(msg or "Launch file configuration error")
