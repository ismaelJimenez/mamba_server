from typing import Optional, Any


class ServiceResponse:
    def __init__(self,
                 id: str,
                 value: Optional[Any] = None,
                 type: Optional[Any] = None):
        self.id = id
        self.value = value
        self.type = type
