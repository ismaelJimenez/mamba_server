from typing import Optional, Any


class ServiceResponse:
    def __init__(self,
                 id: str,
                 provider: Optional[str] = None,
                 value: Optional[Any] = None,
                 type: Optional[Any] = None):
        self.id = id
        self.provider = provider
        self.value = value
        self.type = type
