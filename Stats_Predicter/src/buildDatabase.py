
import database_funs as dfs
from string import ascii_lowercase as letters
from sqlalchemy import create_engine
import pandas as pd
import sqlite3
import pickle
import os.path

# set paths
db_path = '../database/test.db'
db_path_alc = 'sqlite:///../database/test.db'

# set build options
build_bio_table = 1
build_avg_stats_table = 0

if build_bio_table:

    table_name = 'Players'
    dfs.build_bio_table(db_path_alc, table_name)

if build_avg_stats_table:

    player_names = dfs.get_players(db_path)
    table_name = 'Average_Stats'
    dfs.build_average_stats_table(db_path_alc, table_name)