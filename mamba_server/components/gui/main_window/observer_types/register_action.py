class RegisterAction:
    def __init__(self, menu_title, action_name, shortcut=None, status_tip=''):
        self.menu_title = menu_title
        self.action_name = action_name
        self.shortcut = shortcut
        self.status_tip = status_tip
