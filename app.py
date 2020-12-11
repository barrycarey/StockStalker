from stockstalker.notifyagents.discord_agent import DiscordAgent
from stockstalker.parsers.newegg_parser import NeweggParser
from stockstalker.services.notification_history_file import NotificationHistoryFile
from stockstalker.services.notification_svc import NotificationSvc

search_pages = [
        'https://www.newegg.com/p/pl?d=rtx+3080&PageSize=96&N=8000']
product_pages = [
    'https://www.newegg.com/Product/ComboDealDetails?ItemList=Combo.4208292',
    'https://www.newegg.com/evga-geforce-rtx-2080-ti-11g-p4-2383-rx/p/N82E16814487510?Item=N82E16814487510&Description=rtx%202080&cm_re=rtx_2080-_-14-487-510-_-Product',
    'https://www.newegg.com/asus-geforce-rtx-3080-tuf-rtx3080-o10g-gaming/p/N82E16814126452?Item=N82E16814126452&Description=rtx%203080&cm_re=rtx_3080-_-14-126-452-_-Product'
]
ignore_keywords = ['Gladiator']
notify_svc = NotificationSvc(NotificationHistoryFile('history.log'))
notify_svc.register_agent(DiscordAgent('https://discordapp.com/api/webhooks/786096935039139840/RnKGFPi0aMKqSMUie1CcXHNig3tRY33JBKQQWU_v-Q4c1PHrD-l0czd9mhH94PxR1SJk', 'Discord'))
parser = NeweggParser(notify_svc, search_pages=search_pages, product_pages=product_pages, ignore_title_keywords=[])
parser.check_product_pages()
