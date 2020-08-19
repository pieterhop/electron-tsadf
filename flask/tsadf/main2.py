import os
import sys
import argparse
import websockets
import asyncio
import json

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

def auto(tsfile, tsfreq, method, lowboundary, highboundary):
    print("Start auto detection...")
    try:
        TDF = TimeDataFrame(tsfile)
        ts = TDF.fetch_series(TDF.fetch_keys()[1])
    except Exception as e:
        print('Error: {}'.format(e))
        exit(0)

    taf = TAF(ts, tsfreq, None, method, lowboundary, highboundary)

    taf.detect_stronger_seasonality(['DAILY', 'WEEKLY'])
    taf.calc_scores()
    taf.threshold_selection()
    return taf.detect_anomalies()

async def interactive(tsfile, tsfreq, method, lowboundary, highboundary, plot, websocket):
    print("Start interactive detection...")
    try:
        TDF = TimeDataFrame(tsfile)
        ts = TDF.fetch_series(TDF.fetch_keys()[1])
    except Exception as e:
        print('Error: {}'.format(e))
        exit(0)

    taf = TAF(ts, tsfreq, websocket, method, lowboundary, highboundary)

    if plot:
        print("Start preview plot...")
        taf.preview_plot()
    else:
        taf.detect_stronger_seasonality(['DAILY', 'WEEKLY'])
        taf.calc_scores()
        await taf.threshold_selection()
        return await taf.detect_anomalies()

async def handler(websocket, path):
    print("New client")
    args = await websocket.recv()
    print("Arguments received")
    args = json.loads(args)
    await interactive(args['file'], args['tsf_amount'], args['tsm'], args['lowerbound'], args['upperbound'], websocket)

def start_socket():
    start_server = websockets.serve(handler, "localhost", 4567, compression=None)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Started server")
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    start_socket()
