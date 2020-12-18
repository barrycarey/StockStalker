from dataclasses import dataclass
from typing import Text, List


@dataclass
class ParserConfig:
    name: str
    links: dict[Text, List[Text]]
    ignore_title_keywords: List[Text]
    ignore_urls: List[Text]
    notification_agents: List[dict[Text, Text]]