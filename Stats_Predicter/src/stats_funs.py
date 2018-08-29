import sqlite3
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score

def pullSQLData(dbn, tbn, indn, filter_opts):

    # conect to sqlite db
    conn = sqlite3.connect(dbn)
    c = conn.cursor()

    # build SQLite query
    query = 'SELECT * FROM ' + tbn
    count = 0 # not pythonic, find a better way to accomplish this
    for key, item in filter_opts.items():
        if count == 0:
            query += ' WHERE '
        count += 1
        query += key + item[0] + item[1]
        if count < len(filter_opts):
            query += ' AND '

    # execute query
    qout = c.execute(query)

    # put queried data into dataframe
    cols = [column[0] for column in qout.description]
    output = pd.DataFrame.from_records(data=qout.fetchall(), columns=cols, index=indn)

    # close db connection
    conn.close()

    return output

def calcLinRegStats(X, y):

    X2 = sm.add_constant(X)
    est = sm.OLS(y, X2)
    lm = est.fit()
    stats_sum = lm.summary()

    return stats_sum

def fitData(X, y, model_type):

    mod = None

    if model_type == 'linreg':

        mod = LinearRegression()
        mod.fit(X, y)

    elif model_type == 'nn':

        mod = MLPRegressor(max_iter=5000)
        mod.fit(X, y)

    return mod

def calcErr(X_train, y_train, X_test, y_test, mod, model_type):

    y_pred_test = mod.predict(X_test)
    y_pred_train = mod.predict(X_train)
    y_err_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    y_err_test = np.sqrt(mean_squared_error(y_test, y_pred_test))

    # print summary statistics
    print('RMSE, Training = ', y_err_train)
    print('RMSE, Test = ', y_err_test)

    if model_type == 'linreg':

        r2 = r2_score(y_train, y_pred_train)
        print('Model R2 = ', r2)

        linreg_stats = calcLinRegStats(X_train, y_train)
        print(linreg_stats)










