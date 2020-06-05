from typing import List, Any, Optional


class ServiceRequest:
    def __init__(self,
                 id: str,
                 provider: Optional[str] = None,
                 type: str = '',
                 args: List[Any] = []) -> None:
        self.id = id
        self.provider = provider
        self.type = type
        self.args = args
