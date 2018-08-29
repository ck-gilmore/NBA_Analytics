
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import stats_funs as sfs
import numpy as np
import pandas as pd
import matplotlib.pyplot

# suppress unimportant warnings #
import warnings
warnings.filterwarnings(action="ignore", module="sklearn", message="^internal gelsd")

# set filepaths #
dbn = '../database/test.db'

# set filter options #
tbn_stats = 'Average_Stats'
tbn_bios = 'Players'
min_seasons = 3

# set analysis options #
model_type = 'nn'

# pull data for SQLite DB #

# set data filtering options (operator, value), stats
filter_opts_stats = {}
season_min = 2012
filter_opts_stats['Season'] = ['>=', str(season_min)]

# set data filtering options (operator, value), bios
filter_opts_bios = {}

# pull raverage stats data
stats_dat = sfs.pullSQLData(dbn, tbn_stats, 'index', filter_opts_stats)

# pull biographic data
bio_dat = sfs.pullSQLData(dbn, tbn_bios, 'Player', filter_opts_bios)

# do some additional filtering #
df_temp = stats_dat.groupby('Player').filter(lambda x: len(x) >= min_seasons)
player_grouped = df_temp.groupby('Player')

# start off with basic OLS on just points #

# initialize storage arrays
fvec_store = []
dep_store = []

# define output metric
out_metric = ['PTS']

# extract features and dependent variables
# feature vector: [Weight; Height; Age in upcoming season; Yrs of pro experience; Pts, Yr-2; Pts, Yr-1; Pts, Avg Career So Far]
ids = ['Constant', 'Weight', 'Height', 'Age', 'Years of Exp', 'Pts -2', 'Pts -1', 'Pts Career Avg']
for key, stats in player_grouped:

    # pull stuff from bio database
    player = stats.iloc[0]['Player']
    hgt = float(bio_dat.loc[player]['Ht'])
    wgt = float(bio_dat.loc[player]['Wt'])
    first_yr = bio_dat.loc[player]['From'] - 1
    last_yr = bio_dat.loc[player]['To'] - 1

    # initialize feature vector
    fvec_bio = [wgt, hgt]

    # set other variables
    season_start = max(season_min, first_yr) + min_seasons - 1

    # pull stuff from stats database
    for season_ind in range(int(season_start), int(last_yr + 1)):

        # grab stats
        stats_row = stats.loc[stats['Season'] == season_ind]
        stats_row_m2 = stats.loc[stats['Season'] == season_ind - 2]
        stats_row_m1 = stats.loc[stats['Season'] == season_ind - 1]

        if len(stats_row) > 0 and len(stats_row_m1) and len(stats_row_m2):

            # grab other bio stuff
            age_next = float(stats_row.iloc[0]['Age'])
            yrs_pro = season_ind - first_yr

            # grab pts stuff
            pts_m2 = stats_row_m2.iloc[0]['PTS']
            pts_m1 = stats_row_m1.iloc[0]['PTS']
            efg_m2 = stats_row_m2.iloc[0]['eFG%']
            efg_m1 = stats_row_m1.iloc[0]['eFG%']

            if efg_m2 == '' or efg_m1 == '':
                continue
            else:
                efg_m2 = float(efg_m2)
                efg_m1 = float(efg_m1)
                efg_diff = efg_m1 - efg_m2

            # grab pts average
            temp = stats.loc[stats['Season'] < season_ind]
            temp['eFG%'] = pd.to_numeric(temp['eFG%'])
            pts_avg = temp['PTS'].mean()
            efg_avg = temp['eFG%'].mean()

            # store feature vectors
            fvec = fvec_bio + [age_next, yrs_pro, pts_m2, pts_m1, pts_avg, efg_m2, efg_diff]
            fvec_store.append(fvec)

            # grab dependent variable
            pts_dep = stats_row.iloc[0]['PTS']
            dep_store.append(pts_dep)

# convert to numpy arrays
X = np.array(fvec_store)
y = np.array(dep_store)

# preprocess features
X_scaled = preprocessing.scale(X)

# split into training/test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# fit to training data
pts_model = sfs.fitData(X_train, y_train, model_type)

# assess error
sfs.calcErr(X_train, y_train, X_test, y_test, pts_model, model_type)

# visualize stuff


