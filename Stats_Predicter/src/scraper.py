
import urllib3 as ul3
from string import ascii_lowercase
import time
import pickle

from scraper_funs import pullBio_BR, pullStats_BR

# suppress unimportant warnings #
ul3.disable_warnings(ul3.exceptions.InsecureRequestWarning)

# populate URL lookup list #
root_url = r'https://www.basketball-reference.com/'
urls = []
for c in ascii_lowercase:
    url_temp = root_url + 'players/' + c + '/'
    urls.append(url_temp)

# start scraping players #
for url in urls:

    # pull player biographic information and all player rows for given letter
    df_bio, player_rows = pullBio_BR(url)

    ## initialize storage dictionaries
    stats_all = {}

    if player_rows is not None:

        for row in player_rows:

            # get player stats url tag
            url_tag = row.find('a').get('href')
            url_full = root_url + url_tag

            # grab player name
            player = row.find_all('th')[0].get_text()

            # print out some info to screen
            print('Grabbing stats for ' + player + '.')

            # grab stats
            df_stats = pullStats_BR(url_full)

            # build temporary storage dictionary until I figure out what to do next
            stats_all[player] = df_stats

            # pause for one second to limit time between queries
            time.sleep(1)

        # save out to pickle file for each letter
        with open('../BR_data/' + url[-2] + '_stats.pickle', 'wb') as handle:
            pickle.dump([stats_all, df_bio], handle, protocol=pickle.HIGHEST_PROTOCOL)

    # pause for one second to limit time between queries
    time.sleep(1)