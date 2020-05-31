from typing import List, Any


class ServiceRequest:
    def __init__(self, id: str, type: str = '', args: List[Any] = []) -> None:
        self.id = id
        self.type = type
        self.args = args
