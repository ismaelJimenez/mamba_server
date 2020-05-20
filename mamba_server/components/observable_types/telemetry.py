class Telemetry:
    def __init__(self, tm_id: str, value: any = None, tm_type: any = None):
        self.id = tm_id
        self.value = value
        self.type = tm_type
