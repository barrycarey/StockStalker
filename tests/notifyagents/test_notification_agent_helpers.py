from unittest import TestCase

from stockstalker.common.exceptions import InvalidNotificationAgentConfig
from stockstalker.notifyagents.discord_agent import DiscordAgent
from stockstalker.notifyagents.notification_agent_helpers import get_discord_agent, notification_agent_factory


class Test(TestCase):

    def test_notification_agent_factory_discord_config(self):
        agents = notification_agent_factory(
            [
                {'name': 'discord', 'webhook': 'www.webhook.com'}
            ]
        )
        self.assertTrue(len(agents) == 1)

    def test_notification_agent_factory_invalid_config(self):
        agents = notification_agent_factory(
            [
                {'name': 'dummy'}
            ]
        )
        self.assertTrue(len(agents) == 0)

    def test_get_discord_agent_valid(self):
        agent = get_discord_agent({'name': 'discord', 'webhook': 'www.webhook.com'})
        self.assertIsInstance(agent, DiscordAgent)

    def test_get_discord_agent_valid_confirm_name_and_webhook(self):
        agent = get_discord_agent({'name': 'discord', 'webhook': 'www.webhook.com'})
        self.assertEqual('discord', agent.name)
        self.assertEqual('www.webhook.com', agent.webhook_url)

    def test_get_discord_agent_no_webhook(self):
        self.assertRaises(InvalidNotificationAgentConfig, get_discord_agent, {'name': 'discord'})

    def test_get_discord_agent_empty_webhook(self):
        self.assertRaises(InvalidNotificationAgentConfig, get_discord_agent, {'name': 'discord', 'webhook': ''})
