import sys,os
parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

from flowlauncher import FlowLauncher
import requests
from bs4 import BeautifulSoup
import webbrowser
import dbm
import logging

url = 'https://anicloud.io'

class Anicloud(FlowLauncher):

    def query(self, query):
        query = query.strip().lower()

        try:
            data = requests.get(url + '/animes-alphabet').text
            soup = BeautifulSoup(data, 'html.parser')

            animes = soup.find('div', id = 'seriesContainer').find('ul').find_all('a')
        except:
            logging.exception('Error scraping animes')

        output=[]

        with dbm.open('cover.db', 'c') as db:
            for anime in animes:
                title_lower = anime.text.strip().lower()
                titles_lower = anime.get('data-alternative-title').strip().lower()
                if query in title_lower or query in titles_lower:

                    anime_url = url + anime.get('href')
                    cover_url = ''

                    try:
                        cover_url = db[title_lower].decode()
                    except:
                        try:
                            anime_data = requests.get(anime_url).text
                            anime_soup = BeautifulSoup(anime_data, 'html.parser')
                            cover_url = url + anime_soup.find('div', class_ = 'seriesCoverBox').find('img').get('data-src')
                            db[title_lower] = cover_url
                        except:
                            logging.exception('Error scraping cover')

                    output.append({
                        'Title': anime.text.strip(),
                        **({'SubTitle': '(' + anime.get('data-alternative-title').strip() + ')'} if titles_lower != '' else {'SubTitle': ' '}),
                        'IcoPath': cover_url,
                        'JsonRPCAction': { 'method': 'open_url', 'parameters': [anime_url, title_lower] }
                    })
        return output

    def open_url(self, anime_url, title_lower):
        webbrowser.open(anime_url)
        with dbm.open('cover.db', 'w') as db:
            try:
                anime_data = requests.get(anime_url).text
                anime_soup = BeautifulSoup(anime_data, 'html.parser')
                cover_url = url + anime_soup.find('div', class_ = 'seriesCoverBox').find('img').get('data-src')
                db[title_lower] = cover_url
            except:
                logging.exception('Error updating cover')

if __name__ == '__main__':
    Anicloud()