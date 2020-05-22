class IoServiceRequest:
    def __init__(self, id: str, type: str = '', args: list = []):
        self.id = id
        self.type = type
        self.args = args
