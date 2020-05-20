class Telecommand:
    def __init__(self, tc_id: str, args: list = [], tc_type: str = ''):
        self.id = tc_id
        self.args = args
        self.type = tc_type
