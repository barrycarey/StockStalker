from typing import List, Text

from stockstalker.common.exceptions import NoNotificationAgents
from stockstalker.models.parser_config import ParserConfig
from stockstalker.notifyagents.notification_agent import NotificationAgent
from stockstalker.notifyagents.notification_agent_helpers import notification_agent_factory
from stockstalker.parsers.best_buy_parser import BestBuyParser
from stockstalker.parsers.newegg_parser import NeweggParser
from stockstalker.parsers.parser_base import ParserBase
from stockstalker.parsers.walmart_parser import WalmartParser
from stockstalker.services.notification_history_file import NotificationHistoryFile
from stockstalker.services.notification_svc import NotificationSvc

PARSER_NAME_MAP = {
    'newegg': NeweggParser,
    'walmart': WalmartParser,
    'bestbuy': BestBuyParser
}

def parser_factory(config: ParserConfig) -> ParserBase:

    if not config.notification_agents:
        raise NoNotificationAgents("You must provide at least one notification agent")
    notification_agents = notification_agent_factory(config.notification_agents)
    if len(notification_agents) < 1:
        raise NoNotificationAgents('No valid notification agents built from config')
    parser = get_parser_by_name(config.name)
    for agent in notification_agents:
        parser.notification_svc.register_agent(agent)

    return parser

def get_parser_by_name(name: Text) -> ParserBase:
    """
    Takes a string and attempts to map to parser object.  Returning a parser instance with a file notification service
    :rtype: ParserBase
    :param name: Name of parser
    :return: Parser instance
    """
    if name.lower() not in PARSER_NAME_MAP:
        raise ValueError(f'Cannot locate parser by name {name}')
    return PARSER_NAME_MAP[name.lower()](
        NotificationSvc(
            NotificationHistoryFile('history.log'),
        ),
        name
    )