from typing import List

from stockstalker.common.logging import log
from stockstalker.notifyagents.discord_agent import DiscordAgent
from stockstalker.notifyagents.notification_agent import NotificationAgent

def notification_agent_factory(configs: List[dict]) -> List[NotificationAgent]:
    agents = []
    for config in configs:
        if config['name'].lower() not in AGENT_NAME_MAP:
            log.error('Unable to locate notification agent with name %s', config['name'])
            continue
        agents.append(AGENT_NAME_MAP[config['name']](config))

    return agents

def get_discord_agent(config: dict) -> DiscordAgent:
    if 'webhook' not in config or not config['webhook']:
        raise ValueError('Discord config is missing webhook URL')
    log.info('Creating discord agent')
    return DiscordAgent(config['webhook'], config['name'])

AGENT_NAME_MAP = {
    'discord': get_discord_agent,
}