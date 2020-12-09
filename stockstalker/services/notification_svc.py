from typing import List, Text, NoReturn

from stockstalker.common.logging import log
from stockstalker.notifyagents.notification_agent import NotificationAgent
from stockstalker.services.notification_history_base import NotificationHistoryBase


class NotificationSvc:

    def __init__(self, notification_history: NotificationHistoryBase):
        self.notification_history = notification_history
        self.notificaiton_agents: List[NotificationAgent] = []

    def send_notificaiton(self, msg: Text, identifier: Text) -> NoReturn:
        if self.notification_history.has_been_notified(identifier):
            log.info('Already sent notification for identifier %s', identifier)
            return
        for agent in self.notificaiton_agents:
            log.info('Sending notification to %s', agent.name)
            log.debug(msg)
            try:
                agent.send(msg)
                self.notification_history.add_history(identifier)
            except Exception as e:
                log.exception('Failed to send notification', exc_info=True)

    def register_agent(self, agent: NotificationAgent) -> NoReturn:
        self.notificaiton_agents.append(agent)