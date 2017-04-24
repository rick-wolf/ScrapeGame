"""
populates the reviews and reviewers tables
"""

import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
import constants
import psycopg2
import sys

def retrieve_reviews(url, headers, suffix, title_link):
    """
    Retrieves all of the reviews for a given game
    
    :param url: the reviews url prefix (metacritic.com)
    :param headers: headers to include in the request
    :param suffix: url suffix to indicate user or press reviews
    :param title_link: the title of the game being queried, should match metacriticurl from games table
    
    :return: list of dicts containing data about each review
    """
    
    try:
    	request = urllib.request.Request(url+title_link+suffix, None, headers)
    	data = urllib.request.urlopen(request).read()
    except urllib.error.HTTPError:
    	return []
    
    soup = BeautifulSoup(data, 'lxml')
    
    reviews = soup.findAll('li', attrs={'class': 'review user_review'})
    
    review_dicts = []
    for review in reviews:
        review_dicts.append(parse_review(review))
    
    return review_dicts
    
    
def parse_review(review):
    """
    returns data associated with a review embedded in a list item tag
    
    :param review: raw html from the li tag
    :return: dict of data
    """
    rev_dict = {}
    
    # Reviewer's username
    rev_dict['reviewer'] = review.find('div', attrs={'class':'name'}).get_text().strip()

    # Date of Review
    date_text = review.find('div', attrs={'class':'date'}).get_text().strip()
    rev_dict['date'] = datetime.strptime(date_text, '%b %d, %Y').date()

    # Review Grade
    rev_dict['score'] = int(review.find('div', attrs={'class':'review_grade'}).get_text().strip())

    # Text body of the review, handling the 2 types of cases you can encounter
    rt = review.find('span', attrs={'class': 'blurb blurb_expanded'})
    if rt == None:
        rt = review.find('span')
    rev_dict['text'] = rt.get_text()
    
    return rev_dict
        

def main():
	conn=psycopg2.connect("dbname='scrapegame' user='rickwolf' password='mypass'")
	conn.autocommit = True
	cur = conn.cursor()

	#cur.execute("SELECT * FROM games OFFSET 4000 LIMIT 5000")
	cur.execute("SELECT * FROM games WHERE gameid>5024 ORDER BY gameid LIMIT 2000")
	titles = cur.fetchall()


	reviews_cmd = """INSERT INTO reviews 
	(game_id, reviewer, text, date, score)
	SELECT %(gameid)s, %(reviewer)s, %(text)s, %(date)s, %(score)s
	WHERE
	    NOT EXISTS (
	        SELECT game_id, reviewer FROM reviews WHERE game_id=%(gameid)s AND reviewer=%(reviewer)s
	    );

	"""

	reviewer_cmd = """INSERT INTO reviewers 
	(reviewer)
	SELECT %(reviewer)s
	WHERE
	    NOT EXISTS (
	        SELECT reviewer FROM reviewers WHERE reviewer=%(reviewer)s
	    );
	"""


	for gameid, gametitle, gamelink in titles:
	    revs = retrieve_reviews(constants.reviews_table_url, constants.headers, 
	                     constants.reviews_table_suffix, gamelink)
	    for rev in revs:
	        rev['gameid'] = gameid
	    print("entering " + gametitle + " into tables")
	    cur.executemany(reviewer_cmd, revs)
	    cur.executemany(reviews_cmd, revs)
	    sleep(constants.sleeptime)


if __name__ == '__main__':
	main()







