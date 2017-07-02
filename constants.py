## Super Global
# metacritic/beautifulsoup stuff
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent':user_agent,}

sleeptime = 2 # the duration of sleep between requests, in seconds


## Games Table
games_table_url = "http://www.metacritic.com/browse/games/release-date/available/pc/date?view=condensed&page=" # iterate through page numbers
games_table_url_xbox = "http://www.metacritic.com/browse/games/release-date/available/xboxone/date?view=condensed&page="
games_table_url_ps4 = "http://www.metacritic.com/browse/games/release-date/available/ps4/date?view=condensed&page="

## Reviews Table
reviews_table_url = "http://www.metacritic.com"
reviews_table_suffix = "/user-reviews"
reviews_attr = 'review user_review'
