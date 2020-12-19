class StockStalkerException(Exception):
    pass

class NoNotificationAgents(StockStalkerException):
    def __init__(self, message):
        super(NoNotificationAgents, self).__init__(message)

class InvalidConfigDirectory(StockStalkerException):
    def __init__(self, message):
        super(InvalidConfigDirectory, self).__init__(message)

class InvalidNotificationAgentConfig(StockStalkerException):
    def __init__(self, message):
        super(InvalidNotificationAgentConfig, self).__init__(message)

