from stockstalker.notifyagents.discord_agent import DiscordAgent
from stockstalker.parsers.newegg_parser import NeweggParser
from stockstalker.services.notification_history_file import NotificationHistoryFile
from stockstalker.services.notification_svc import NotificationSvc

search_pages = [
        'https://www.newegg.com/p/pl?d=rtx+3080&PageSize=96&N=8000']
product_pages = [
    'https://www.bestbuy.com/site/evga-geforce-rtx-3080-xc3-ultra-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6432400.p?skuId=6432400'
]
ignore_keywords = ['Gladiator']
notify_svc = NotificationSvc(NotificationHistoryFile('history.log'))
notify_svc.register_agent(DiscordAgent('https://discordapp.com/api/webhooks/786096935039139840/RnKGFPi0aMKqSMUie1CcXHNig3tRY33JBKQQWU_v-Q4c1PHrD-l0czd9mhH94PxR1SJk', 'Discord'))
parser = NeweggParser(notify_svc, search_pages=search_pages, web_driver=r"C:\chromedriver\chromedriver.exe", ignore_title_keywords=[])
parser.check_stock()
parser.web_driver.close()