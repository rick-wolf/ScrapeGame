"""
Populates the games table of the database
"""

import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
import constants
import psycopg2

def parse_game_titles(text_data):
    """
    Retrieves all the info associated with each game from input text
    
    :param text_data: text from a single <li> tag with class 'product game_product'
    :return: a dict of the form {url:game_url_tail, title:official_title}
    """
    atag = text_data.find('a', href=True)
    url_tail = atag['href']
    title = atag.get_text().strip()
    
    return {'url':url_tail, 'title':title}



def paginate_games(url, headers, pagelim = float('inf')):
    """
    Loops through pages and returns a list of games on each page
    
    :param url: url with all text except the page number
    :param headers: headers to include in the request
    :param pagelim: how many pages to paginate through
    
    :return: a list of game names and their data
    """
    
    gamelist = []
    i = 0
    while i <= pagelim:
        i += 1
        request = urllib.request.Request(url + str(i), None, headers)
        pagedata = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(pagedata, "lxml")
        
        games_in_page = soup.findAll('li', attrs={'class': 'product game_product'})
        if not games_in_page:
            print('Explored ' + str(i) + ' pages before stopping')
            break
        
        for game in games_in_page:
            gamelist.append(parse_game_titles(game))
        
        sleep(constants.sleeptime)
    
    return gamelist


def main():
	# establish connection to database
	conn=psycopg2.connect("dbname='scrapegame' user='rickwolf' password='mypass'")
	conn.autocommit = True
	cur = conn.cursor()
	insert_cmd = """INSERT INTO games 
    	(gametitle, metacriticurl)
	SELECT %(title)s, %(url)s
	WHERE
    	NOT EXISTS (
        	SELECT metacriticurl FROM games WHERE metacriticurl=%(url)s
    	);
	"""

	# retrieve xbox game titles and enter into tables
	game_titles = paginate_games(constants.games_table_url_xbox, constants.headers)
	cur.executemany(insert_cmd, game_titles)

    # retrieve ps4 game titles and enter into tables
    game_titles = paginate_games(constants.games_table_url_ps4, constants.headers)
    cur.executemany(insert_cmd, game_titles)


if __name__ == "__main__":
	main()
