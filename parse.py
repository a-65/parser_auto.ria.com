import requests
from bs4 import BeautifulSoup
import csv

# Парсинг данных о новых автомобилях марки "Шкода" с сайта https://auto.ria.com

URL = 'https://auto.ria.com/newauto/marka-skoda/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15', 'accept': '*/*'}
HOST = 'https://auto.ria.com'
FILE = 'cars.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='mhide') # end button of pages
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='proposition')
    cars = []
    for item in items:
        uah_price = None
        if item.find('span', class_='size16').get_text(strip=True):
            uah_price = item.find('span', class_='size16').get_text(strip=True)
        cars.append({
            'title': item.find('div', class_='proposition_title').get_text(strip=True),
            'link': HOST + item.find('a', class_='proposition_link').get('href'),
            'usd_price': item.find('span', class_='green').get_text(strip=True),
            'uah_price': uah_price,
            'city': item.find('span', class_='item region').get_text(strip=True)
        })
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['title', 'link', 'usd_price', 'uah_price', 'city'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)} авто.')
    else:
        print('Error')


parse()