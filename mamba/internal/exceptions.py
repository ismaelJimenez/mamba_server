# Mamba exceptions


class ComponentConfigException(Exception):
    def __init__(self, msg=None):
        super(ComponentConfigException, self).__init__(msg or "Component configuration error")


class LaunchFileException(Exception):
    def __init__(self, msg=None):
        super(LaunchFileException, self).__init__(msg or "Launch file configuration error")
