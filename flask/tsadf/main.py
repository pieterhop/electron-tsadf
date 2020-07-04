import os
import sys
# import argparse

path = './'
exclude = [".git", "__pycache__", "node_modules", "ui", "js", "css", "data"]
DIRS = [x[0] for x in os.walk(path)]
for d in DIRS:
    split_d = d.split('/')
    common = list(set(split_d).intersection(exclude))
    if len(common) < 1:
        sys.path.append(d+'/')

from timedataframe import TimeDataFrame
from framework import TAF

def input():
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--tsfile", help="path to timeseries file ( in CSV format-> ['Time', 'Value'] )", required=True)
    ap.add_argument("-f", "--tsfreq", help="timeseries frequency", required=True)
    ap.add_argument("-m", "--method", help="threshold selection method", default='automatic')
    ap.add_argument("-s", "--seasonality", help="list of seasonality", default='automatic')
    ap.add_argument("-l", "--lowboundary", help="lower limit of accepted value", default=0)
    ap.add_argument("-b", "--highboundary", help="higher limit of accepted value", default=100000)
    ap.add_argument("-p", "--plot", help="plot boolean", default=True)

    args = vars(ap.parse_args())
    return args

def preprocess_seasonality():
    pass

def detect(tsfile, tsfreq, method, lowboundary, highboundary):
    # method = kwargs.get('method', 'automatic')
    # lowboundary = kwargs.get('lower', 0)
    # highboundary = kwargs.get('higher', 100000)

    try:
        TDF = TimeDataFrame(tsfile)
        ts = TDF.fetch_series(TDF.fetch_keys()[1]) # assumed CSV format ['Time', 'Value']
    except Exception as e:
        print('Error: {}'.format(e))
        exit(0)

    taf = TAF(ts, tsfreq, method, lowboundary, highboundary)
    taf.detect_stronger_seasonality(['DAILY', 'WEEKLY'])
    taf.calc_scores()

    # taf.preview_plot()

    taf.threshold_selection()
    return taf.detect_anomalies()

if __name__ == '__main__':
    detect('sample_data.csv', 96, 'automatic', 0, 100000)
