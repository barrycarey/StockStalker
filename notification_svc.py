from typing import List

from NotificationAgent import NotificationAgent


class NotificationSvc:

    def __init__(self):
        self.notificaiton_agents: List[NotificationAgent] = []

    def send_notificaiton(self, data):
        for agent in self.notificaiton_agents:
            agent.send()