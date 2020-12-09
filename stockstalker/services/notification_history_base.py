from typing import Text


class NotificationHistoryBase:

    def __init__(self):
        pass

    def add_history(self, identifier: Text):
        raise NotImplementedError

    def remove_history(self, identifier: Text):
        raise NotImplementedError

    def clear_history(self):
        raise NotImplementedError

    def has_been_notified(self, identifier: Text):
        raise NotImplementedError

