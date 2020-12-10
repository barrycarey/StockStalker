import os
from typing import Text

from stockstalker.common.logging import log
from stockstalker.services.notification_history_base import NotificationHistoryBase


class NotificationHistoryFile(NotificationHistoryBase):

    def remove_history(self, identifier: Text):
        raise NotImplementedError

    def __init__(self, history_file_name: Text):
        self.history_file_name = history_file_name
        self.sent_notifications = []
        super().__init__()
        self._load_history()

    def _load_history(self):
        if not os.path.isfile(self.history_file_name):
            log.info('Unable to locate history file %s. Skipping Load', self.history_file_name)
            return
        with open(self.history_file_name, 'r') as f:
            for line in f:
                self.sent_notifications.append(line)
        log.info('Loaded %s notifications from history', len(self.sent_notifications))

    def add_history(self, identifier: Text):
        with open(self.history_file_name, 'a') as f:
            f.write(identifier)
            log.debug('Added 1 entry to notification history with identifer %s', identifier)

    def clear_history(self):
        with open(self.history_file_name, 'a') as f:
            f.truncate()

    def has_been_notified(self, identifier: Text):
        return identifier in self.sent_notifications
