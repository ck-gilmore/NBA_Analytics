
import pickle

file = open('../BR_data/a_stats.pickle','rb')
dat = pickle.load(file)
file.close()

print(dat)