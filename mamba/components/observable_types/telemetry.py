from typing import Optional, Any


class Telemetry:
    def __init__(self, tm_id: str, value: Optional[Any] = None, tm_type: Optional[Any] = None):
        self.id = tm_id
        self.value = value
        self.type = tm_type
