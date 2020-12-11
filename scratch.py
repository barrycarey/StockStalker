import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.newegg.com/evga-geforce-rtx-2080-ti-11g-p4-2383-rx/p/N82E16814487510?Item=N82E16814487510&Description=rtx%202080&cm_re=rtx_2080-_-14-487-510-_-Product')
soup = BeautifulSoup(r.text)
print('')