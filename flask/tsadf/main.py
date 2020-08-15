import os
import sys
import argparse

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
    ap.add_argument("-p", "--plot", help="plot boolean", default=False)
    args = vars(ap.parse_args())
    return args

def detect(tsfile, tsfreq, method, lowboundary, highboundary, plot):
    try:
        TDF = TimeDataFrame(tsfile)
        ts = TDF.fetch_series(TDF.fetch_keys()[1])
    except Exception as e:
        print('Error: {}'.format(e))
        exit(0)

    taf = TAF(ts, tsfreq, method, lowboundary, highboundary)
    
    if plot:
        taf.preview_plot()
    else:
        taf.detect_stronger_seasonality(['DAILY', 'WEEKLY'])
        taf.calc_scores()
        taf.threshold_selection()
        return taf.detect_anomalies()

if __name__ == '__main__':
    args = input()
    detect(args['tsfile'], args['tsfreq'], args['method'], args['lowboundary'], args['highboundary'], args['plot'])
