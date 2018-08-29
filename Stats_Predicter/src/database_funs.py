
from sqlite3 import Error
from string import ascii_lowercase as letters
from sqlalchemy import create_engine
import pandas as pd
import sqlite3
import pickle
import os.path


def create_connection(db_file):

    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        conn.close()


def get_players(db_path):

    # initialize connection
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # pull players
    c.execute('SELECT Player FROM Players')
    out = c.fetchall()

    # close connections
    conn.close()

    # reformat names and store
    player_names = []
    [player_names.append(name[0]) for name in out]

    return player_names


def build_bio_table(db_path, table_name):

    # connect to sql database
    engine = create_engine(db_path)

    # print stuff out
    print('Building player biographical information table...')

    ## build full bio dataframe

    # initialize storage variables
    df_bio_all = pd.DataFrame()

    # load in data
    for letter in letters:

        # load file
        fn = '../BR_data/' + letter + '_stats.pickle'
        if os.path.isfile(fn):
            file = open(fn, 'rb')
            dat = pickle.load(file)

            # pull out dataframes
            # dict_stats = dat[0]
            df_bio = dat[1]

            # reformat as necessary
            for index, row in df_bio.iterrows():
                # get rid of *s
                index_no_star = index
                if '*' in index:
                    index_no_star = index.replace('*', '')
                    df_bio = df_bio.rename(index={index: index_no_star})
                # convert height to number
                hgt = row['Ht']
                if not (hgt is None or hgt == ''):
                    dash_ind = hgt.index('-')
                    df_bio.at[index_no_star, 'Ht'] = float(hgt[0:dash_ind])*12. + float(hgt[dash_ind+1:])

            # build full bio dataframe
            df_bio_all = df_bio_all.append(df_bio)

            # close file
            file.close()

    # add to sqlite db
    df_bio_all.to_sql(table_name, con=engine, if_exists='replace')

    print('         done.')


def build_average_stats_table(db_path, table_name):

    # connect to sql database
    engine = create_engine(db_path)

    # print stuff out
    print('Building player stats information table...')

    ## build full stats dataframe

    # initialize storage variables
    df_stats_all = pd.DataFrame()

    # load in data
    for letter in letters:

        # get file name
        fn = '../BR_data/' + letter + '_stats.pickle'

        if os.path.isfile(fn):

            file = open(fn, 'rb')
            dat = pickle.load(file)

            print('Processing stats for ' + letter + '.')

            # pull out dataframes
            dict_stats = dat[0]

            # reformat as necessary
            dict_temp = {}
            for key in dict_stats.keys():
                if '*' in key:
                    key_no_star = key.replace('*', '')
                    dict_temp[key_no_star] = dict_stats[key]
                else:
                    dict_temp[key] = dict_stats[key]
            dict_stats = dict_temp

            # build full stats dataframe
            for key, stats in dict_stats.items():

                # pull total (TM = TOT) if played for multiple teams in a single season
                season_store = []
                for index, row in stats.iterrows():
                    if row['Tm'] == 'TOT':
                        season_store.append(row['Season'])
                for index, row in stats.iterrows():
                    if row['Season'] in season_store and not (row['Tm'] == 'TOT'):
                        stats = stats.drop(index)

                # add in player column
                n_years = len(stats)
                name_dat = [key]*n_years
                stats['Player'] = pd.Series(name_dat, index=stats.index)

                # reformat season variable to only season start year and convert to float
                for index, row in stats.iterrows():
                    season_temp = stats.loc[index]['Season']
                    stats.at[index, 'Season'] = int(season_temp[0:4])

                # add to storage dataframe
                for index, row in stats.iterrows():
                    s = pd.Series(row)
                    s.name = (row['Player'].replace(' ', '') + '_' + str(row['Season']))
                    df_stats_all = df_stats_all.append(s)


            # close file
            file.close()

    # add to sqlite db
    df_stats_all.to_sql(table_name, con=engine, if_exists='replace')

    print('         done.')
