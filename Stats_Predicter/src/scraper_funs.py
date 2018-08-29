import urllib3 as ul3
from bs4 import BeautifulSoup as Bsp
import pandas as pd
import numpy as np

__all__ = ['pullStats_BR', 'pullBio_BR']

def pullStats_BR(page_url):

    # BR: Basketball Reference; see https://www.basketball-reference.com/

    # setup scrape manager
    scrape_manager = ul3.PoolManager()

    # pull page
    response = scrape_manager.request('GET', page_url)
    soup = Bsp(response.data, features='lxml')

    # find stats table
    stats_table_all = soup.find('table', attrs={'id': 'per_game'})
    stats_table = stats_table_all.find('tbody')

    # pull out header
    rowh = stats_table_all.find_all('tr')[0]
    header = rowh.get_text().split('\n')[1:-1]

    # pull stats from table
    df_stats = scrapeBRTable_noIndex(stats_table, header)

    return df_stats

def pullBio_BR(page_url):

    # setup scrape manager
    scrape_manager = ul3.PoolManager()

    # pull page
    response = scrape_manager.request('GET', page_url)
    soup = Bsp(response.data, features='lxml')

    # pull player table
    player_table_all = soup.find('table', attrs={'id': 'players'})

    if player_table_all is not None:

        player_table = player_table_all.find('tbody')

        # pull out header
        rowh = player_table_all.find_all('tr')[0]
        header = rowh.get_text().split('\n')[1:-1]

        # pull stats from table
        df_bio = scrapeBRTable(player_table, header)

        # grab stats url
        player_rows = player_table.find_all('tr')

    else:

        df_bio = None
        player_rows = None

    return df_bio, player_rows

def scrapeBRTable(table, header):

    # intitialize storage dataframe
    df_dat = pd.DataFrame(columns=header[1:])
    df_dat.index.name = header[0]

    # extract data
    rows_dat = table.find_all('tr')
    for row in rows_dat:
        season = row.find_all('th')
        if len(season) > 0:
            dat_pull = [season[0].get_text()]
        else:
            # skip empty rows
            continue
        cols = row.find_all('td')
        for col in cols:
            dat = col.get_text()
            dat_pull.append(dat)

        # convert things to a float if it's possible
        dat_pull = convert_to_float(dat_pull)

        # put data in dataframe (for now)
        df_dat.loc[dat_pull[0]] = dat_pull[1:]

    return df_dat

def scrapeBRTable_noIndex(table, header):

    # intitialize storage dataframe
    df_dat = pd.DataFrame(columns=header)

    # extract data
    rows_dat = table.find_all('tr')
    for ind, row in enumerate(rows_dat):
        season = row.find_all('th')
        if len(season) > 0:
            dat_pull = [season[0].get_text()]
        else:
            # skip empty rows
            continue
        cols = row.find_all('td')
        for col in cols:
            dat = col.get_text()
            dat_pull.append(dat)

        # convert things to a float if it's possible
        dat_pull = convert_to_float(dat_pull)

        # put data in dataframe (for now)
        df_dat.loc[ind] = dat_pull

    return df_dat

def convert_to_float(dat):
    dat_new = []
    for x in dat:
        try:
            dat_new.append(float(x))
        except ValueError:
            dat_new.append(x)
    return dat_new






