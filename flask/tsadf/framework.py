import sys
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import f
import json
from time import sleep
from io import BytesIO
import base64
import asyncio

from timedataframe import TimeDataFrame
from anomalydetection import AD

import utility

class TAF:
    def __init__(self, ts, ts_freq, websocket, method='automatic', range_lower_limit=0, range_higher_limit=1000000):
        self.ts = ts
        self.ts_freq = ts_freq
        self.threshold_method = method
        self.range = int(range_higher_limit) - int(range_lower_limit)
        self.websocket = websocket

    def detect_stronger_seasonality(self, seasonality_list=['WEEKLY, DAILY']):
        self.preprocess_weekly_daily_data(seasonality_list)

    def calc_scores(self):
        self.ad = AD(self.ts, self.ts_freq, self.season, str(self.range), 'scores.csv')
        self.anomaly_df = self.ad.get_updated_df()

    async def threshold_selection(self):
        if self.threshold_method != 'automatic':
            self.point_distance_score_threshold, itermediate_thresholds1 = await self._determine_threshold(self.anomaly_df, 'PDS')
            self.difference_distance_score_threshold, itermediate_thresholds2 = await self._determine_threshold(self.anomaly_df, 'DDS')
            # print(itermediate_thresholds1)
            # print(itermediate_thresholds2)
        else:
            self._calculate_mz()


    def detect_anomalies(self):
        extreme_an_df = self.anomaly_df[self.anomaly_df['wvs'] == str(self.range)]['value']
        point_an_df = 0
        diff_an_df = 0
        only_point_an_df = 0
        only_diff_an_df = 0

        if self.threshold_method == 'interactive':
            point_an_df = self.anomaly_df[self.anomaly_df['qd'] > self.point_distance_score_threshold]
            diff_an_df = self.anomaly_df[self.anomaly_df['diff_qd'] > self.difference_distance_score_threshold]

            only_point_an_df = point_an_df[point_an_df['diff_qd'] <= self.difference_distance_score_threshold]
            only_diff_an_df = diff_an_df[diff_an_df['qd'] <= self.point_distance_score_threshold]


        elif self.threshold_method == 'automatic':
            point_an_df = self.anomaly_df[self.anomaly_df['qd_mz'] > 3.5]
            diff_an_df = self.anomaly_df[self.anomaly_df['dqd_mz'] > 3.5]

            only_point_an_df = point_an_df[point_an_df['dqd_mz'] <= 3.5]
            only_diff_an_df = diff_an_df[diff_an_df['qd_mz'] <= 3.5]

        results = {
          "pd_anomaly": len(only_point_an_df),
          "dd_anomaly": len(only_diff_an_df),
          "common_anomaly": len(point_an_df) - len(only_point_an_df),
          "extreme_anomalies": len(extreme_an_df)
        }

        if self.threshold_method == "automatic":
            return results
        else:
            print(results)
            print("finished")

    def _detailed_plot(self, raw_df, col, val_col, an_index, data_points=300, threshold=0, anomaly_count=0):

        f, splts = plt.subplots(len(an_index), 2, sharey=True)
        for j in range(len(an_index)):

            # show data points around the selected points
            index = list()
            range_high = list()
            range_low = list()
            threshold_high = list()
            threshold_low = list()
            wvs = list()
            qd = list()
            dqd = list()

            block_start = 0
            block_end = len(raw_df)
            if int(an_index[j] - data_points / 2) >= 0:
                block_start = int(an_index[j] - data_points / 2)

            if int(an_index[j] + data_points / 2) <= len(raw_df):
                block_end = int(an_index[j] + data_points / 2)

            # print('{}, {}, {}'.format(block_start, block_end, an_index[j]))

            try:

                temp_df = raw_df[block_start:block_end]
                temp_df = temp_df.reset_index(drop=True)

                for i in temp_df.index.values:
                    index.append(i)
                    if val_col == 'diff':
                        range_high.append(temp_df.loc[i]['diff_q3'])
                        range_low.append(temp_df.loc[i]['diff_q1'])
                        threshold_high.append(temp_df.loc[i]['diff_q3'] + threshold)
                        threshold_low.append(temp_df.loc[i]['diff_q1'] - threshold)
                    else:
                        range_high.append(temp_df.loc[i]['q3'])
                        range_low.append(temp_df.loc[i]['q1'])
                        threshold_high.append(temp_df.loc[i]['q3'] + threshold)
                        threshold_low.append(temp_df.loc[i]['q1'] - threshold)

                    wvs.append(temp_df.loc[i]['wvs'])
                    qd.append(temp_df.loc[i]['qd'])
                    dqd.append(temp_df.loc[i]['diff_qd'])

                splts[j][0].fill_between(index, range_high, range_low, color='lightblue', alpha=0.8, label='Normal Behavior (1st to 3rd quartile)')
                temp_df[val_col].plot(ax=splts[j][0], color='green')
                s = temp_df[temp_df['oi'] == an_index[j]][val_col]
                splts[j][0].scatter(y=s.values, x=s.index.values, color='red', label='Anomalies')
                splts[j][0].grid(True)

                temp_df['show_ticks'] = False
                temp_df['show_ticks'] = temp_df['oi'].apply(lambda x: (x % 6 == 0))
                ticks = temp_df[temp_df['show_ticks']]['time']
                splts[j][0].set_xticklabels(ticks.values.tolist(), rotation=10, fontsize=8)

            except:
                print('Error: out of boundary expception occurred in searching...')


            # show the cluster this data point belongs to
            day = raw_df[raw_df['oi'] == an_index[j]]['day'].values.tolist()[0]
            interval = raw_df[raw_df['oi'] == an_index[j]]['interval'].values.tolist()[0]
            cluster_df = raw_df[(raw_df['day'] == day) & (raw_df['interval'] == interval)]
            cluster_df = cluster_df.reset_index(drop=True)

            # show all data points in a time-series manner
            splts[j][1].scatter(y = cluster_df[val_col].values, x = cluster_df.index.values, color='mediumslateblue')
            q1, q3 = np.percentile(cluster_df[cluster_df['value'] > -1][val_col].dropna().values, [25, 75])
            splts[j][1].fill_between([v for v in range(len(cluster_df))], [q3 for v in range(len(cluster_df))], [q1 for v in range(len(cluster_df))], color="lightblue", alpha=0.8, label='Normal Behavior')

            # mark the data point
            anomaly_series = cluster_df[cluster_df['oi'] == an_index[j]][val_col]
            splts[j][1].scatter(y=anomaly_series.values, x = anomaly_series.index.values, color='red', label='Anomaly')
            splts[j][1].grid(True)


        # plt.subplots_adjust(top=0.94,bottom=0.075,left=0.04,right=0.97,hspace=0.285,wspace=0.095)
        plt.subplots_adjust(top=0.94,bottom=0.075,left=0.04,right=0.97,hspace=0.5,wspace=0.095)
        f.suptitle('Current threshold {}, # of anomalies detected {}'.format(threshold, anomaly_count))
        # plt.show()
        # plt.savefig('src/img/temp/detailed_plot.png', dpi=500)

        buf = BytesIO()
        fig1 = plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        fig_data = base64.b64encode(buf.getvalue())
        buf.close()
        return fig_data


    def preview_plot(self):
        print('plot')
        _, splts = plt.subplots(1, sharex=True, sharey=True)
        self.anomaly_df['value'][0:100].plot(x='time', color='mediumslateblue')
        plt.show()

        # df.plot(x='date_time', y='price_usd', figsize=(12,6))
        # plt.xlabel('Date time')
        # plt.ylabel('Price in USD')
        # plt.title('Time Series of room price by date time of search');


    def final_plot(temp_df, qd_t, dqd_t):
        _, splts = plt.subplots(1, sharex = True, sharey=True)
        index = list()
        range_high = list()
        range_low = list()
        threshold_high = list()
        threshold_low = list()
        diff_range_high = list()
        diff_range_low = list()
        diff_threshold_high = list()
        diff_threshold_low = list()
        qd = list()
        diff_qd = list()
        for i in temp_df.index.values:
            index.append(i)
            range_high.append(temp_df.loc[i]['q3'])
            range_low.append(temp_df.loc[i]['q1'])
            threshold_high.append(temp_df.loc[i]['q3'] + qd_t)
            threshold_low.append(temp_df.loc[i]['q1'] - qd_t)

            diff_range_high.append(temp_df.loc[i]['diff_q3'])
            diff_range_low.append(temp_df.loc[i]['diff_q1'])
            diff_threshold_high.append(temp_df.loc[i]['diff_q3'] + dqd_t)
            diff_threshold_low.append(temp_df.loc[i]['diff_q1'] - dqd_t)


            qd.append(temp_df.loc[i]['qd'])
            diff_qd.append(temp_df.loc[i]['diff_qd'])

        #splts.fill_between(index, threshold_high, range_high, color='lightblue', alpha=0.3, label='{} quartile distance'.format(qd_t))
        #splts.fill_between(index, range_high, range_low, color='lightblue', alpha=0.8, label='Normal Behavior (1st to 3rd quartile)')
        #splts.fill_between(index, range_low, threshold_low, color='lightblue', alpha=0.4)
        temp_df['value'].plot(ax=splts, color='mediumslateblue')
        s = temp_df[temp_df['qd'] > qd_t]['value']
        splts.scatter(y=s.values, x=s.index.values, color='red', marker='o', label='Anomalies based on point-distance')

        s2 = temp_df[temp_df['diff_qd'] > dqd_t]['value']
        splts.scatter(y=s2.values, x=s2.index.values, color='orange', marker='x', label='Anomalies based on difference-distance')

        s3 = temp_df[temp_df['wvs'] == 1000]['value']
        splts.scatter(y=s3.values, x=s3.index.values, color='black', marker='s', label='Non-contextual anomalies')

        splts.set_title('Anomalies against threshold pair ({}, {})'.format(qd_t, dqd_t))
        splts.legend(bbox_to_anchor=(1,0), loc="lower right", bbox_transform=_.transFigure, ncol=3)
        plt.show()

        _, splts = plt.subplots(1, sharex = True, sharey=True)
        splts.fill_between(index, threshold_high, range_high, color='lightblue', alpha=0.3, label='{} point distance border'.format(qd_t))
        splts.fill_between(index, range_high, range_low, color='lightblue', alpha=0.8, label='Normal Behavior')
        splts.fill_between(index, range_low, threshold_low, color='lightblue', alpha=0.4)
        temp_df['value'].plot(ax=splts, color='mediumslateblue')
        s_diff = temp_df['value'][(temp_df['qd'] > qd_t)]
        splts.scatter(y=s_diff.values, x=s_diff.index.values, color='orange', marker='x', label='Anomalies')
        splts.set_title('Anomalies against point distance threshold {}'.format(qd_t))
        splts.legend(bbox_to_anchor=(1,0), loc="lower right", bbox_transform=_.transFigure, ncol=3)

        _, splts = plt.subplots(1, sharex = True, sharey=True)
        splts.fill_between(index, diff_threshold_high, diff_range_high, color='lightblue', alpha=0.3, label='{} difference distance border'.format(dqd_t))
        splts.fill_between(index, diff_range_high, diff_range_low, color='lightblue', alpha=0.8, label='Normal Behavior')
        splts.fill_between(index, diff_range_low, diff_threshold_low, color='lightblue', alpha=0.4)
        temp_df['diff'].plot(ax=splts, color='mediumslateblue')
        s_diff = temp_df['diff'][(temp_df['diff_qd'] > dqd_t)]
        splts.scatter(y=s_diff.values, x=s_diff.index.values, color='orange', marker='x', label='Anomalies')
        splts.set_title('Anomalies against difference distance threshold {}'.format(dqd_t))
        splts.legend(bbox_to_anchor=(1,0), loc="lower right", bbox_transform=_.transFigure, ncol=3)

        #plt.xticks(index, time_ticks, rotation=90)
        plt.show()


    async def _determine_threshold(self, raw_df, score_type):
        value_col = 'value'
        if score_type == 'PDS':
            col = 'qd'
        elif score_type == 'DDS':
            col = 'diff_qd'
            value_col = 'diff'

        threshold_high = raw_df.describe()[col]['max']
        threshold_low = 0
        valid_threshold = 0

        intermediate_results = []
        while (threshold_high > (threshold_low+1)):
            # sleep(5)
            threshold_mean = math.ceil((threshold_high + threshold_low) / 2)

            an_list = raw_df[raw_df[col] > threshold_mean]
            an_list = an_list.sort_values(col)
            anomaly_count = len(an_list)
            # print('threshold_high {}, threshold_mean {}, threshold_low {}'.format(threshold_high, threshold_mean, threshold_low))
            closest_five = an_list['oi'][:5].values.tolist()
            # print(closest_five)

            data_points = 100

            detailed_plot = self._detailed_plot(raw_df, col, value_col, closest_five, data_points, threshold_mean, anomaly_count)
            print("Start sending...")
            await self.websocket.send({"type": "image", "message": detailed_plot})
            print("Send! Awaiting choice...")

            choice = await self.websocket.recv()
            print("Received choice")
            print(choice)

            if choice == 'yes':
                intermediate_results.append({'threshold': threshold_mean, 'anomalies': len(an_list)})
                threshold_high = threshold_mean
                valid_threshold = threshold_mean
            elif choice == 'q':
                break
            else:
                threshold_low = threshold_mean

        return valid_threshold, intermediate_results


    def _calculate_mz(self):
        self.anomaly_df['qd_mz'] = 0
        series = self.anomaly_df[self.anomaly_df['qd'] > 0]['qd'].dropna().values.tolist()
        med = np.median(series)
        mad = np.median([np.abs(y - med) for y in series])
        self.anomaly_df['qd_mz'] = self.anomaly_df[['qd']].apply(self._set_mz_qd, args=(med,mad,), axis=1)

        self.anomaly_df['dqd_mz'] = 0
        series = self.anomaly_df[self.anomaly_df['diff_qd'] > 0]['diff_qd'].dropna().values.tolist()
        med = np.median(series)
        mad = np.median([np.abs(y - med) for y in series])
        self.anomaly_df['dqd_mz'] = self.anomaly_df[['diff_qd']].apply(self._set_mz_dqd, args=(med,mad,), axis=1)

    def _set_mz_qd(self, r, med, mad):
        return 0.6745 * (r['qd'] - med) / mad

    def _set_mz_dqd(self, r, med, mad):
        return 0.6745 * (r['diff_qd'] - med) / mad


    def preprocess_weekly_daily_data(self, seasonality_list):
        # prepare X for daily vs weekly comparison
        df = self.ts.to_frame().reset_index()
        df.columns = ['time', 'value']
        df['day'] = df[['time']].apply(utility.add_day_column, axis=1)
        df['interval'] = df[['time']].apply(utility.add_interval_column, axis=1)
        df['hod'] = df[['interval']].apply(utility.add_hour_column, axis=1)
        df['moh'] = df[['interval']].apply(utility.add_minute_column, axis=1)
        df['date'] = df[['time']].apply(utility.add_date_column, axis=1)
        df['dom'] = df[['date']].apply(utility.add_day_of_month_column, axis=1)
        df['wom'] = df['dom'] / 7
        df['wom'] = np.ceil(df['wom'])
        df['wom'] = df['wom'] - 1

        day_counter = 0
        for date in df['date'].unique().tolist():
            #copy_df.loc[copy_df['date'] == date, 'add_group_index'] = day_counter
            df.loc[df['date'] == date, 'doy'] = day_counter
            day_counter = day_counter + 1


        df['month_index'] = df[['date']].apply(utility.add_month_index_column, axis=1)
        df['diff'] = df['value'].diff()
        intervals = df['interval'].unique().tolist()
        doms = df['dom'].unique().tolist()

        copy_df = df
        copy_df = copy_df.reset_index(drop=True).reset_index()
        X = []

        for i in copy_df['interval'].unique().tolist():
            s = copy_df[copy_df['interval'] == i]['value']
            X.append(s.dropna().values.tolist())

        #Y = weekly blocks
        copy_df = df
        copy_df = copy_df.reset_index(drop=True).reset_index()

        Y = []

        for ind in copy_df['day'].unique().tolist():
            temp = copy_df[copy_df['day'] == ind] # ind = 'monday', 'tuesday', 'wednesday', 'thursday'
            all_s = []
            for i in temp['interval'].unique().tolist(): # 0-> 00:00, 1 -> 00:15
                s = temp[temp['interval'] == i]['value']
                # print(s)
                all_s.append(s.dropna().values.tolist())

            Y.append(all_s)

        ticks = df['interval'].unique().tolist()
        for i in range(len(X)):
            if i % 16 != 0:
                ticks[i] = ''


        self.season, sizes, c_collector, Y_dim = self._compare(X, Y, seasonality_list[1], seasonality_list[0], ticks)


    def _compare(self, X, Y, name_x, name_y, ticks=False, alpha = 0.05, plt_title='Comparison of seasonality'):
        c_collector = []
        unexpected = 0
        insignificant = 0
        C = 0
        for d in range(len(X)):
            D = X[d]
            var_D = np.var(D, ddof=1)

            # 3. create blocks and collect all D_i
            c = 0
            for i in range(len(Y)): # 672
                D_i = Y[i][d]
                # determine variance
                var_D_i = np.var(D_i, ddof=1)
                # check variance
                if var_D_i < var_D:
                    # check significance of the difference
                    deg_D = len(D) - 1
                    deg_D_i = len(D_i) - 1
                    critical_val_low = f.ppf(q=alpha/2, dfn=deg_D, dfd=deg_D_i)
                    critical_val_high = f.ppf(q=1 - alpha/2, dfn=deg_D, dfd=deg_D_i)

                    fstat_sample = var_D / var_D_i

                    if (fstat_sample < critical_val_low) | (fstat_sample > critical_val_high):
                        c = c + 1
                    else:
                        unexpected = unexpected + 1
                        insignificant = insignificant + 1
                else:
                    unexpected = unexpected + 1

            #print(c)
            c_collector.append(c)
            if c > int(len(Y)/2):
                C = C + 1

        #print(C)
        winner = ''
        if C > int(len(X)/2):
            # print('Go with {}'.format(name_y))
            winner = name_y
        else:
            # print('Go with {}'.format(name_x))
            winner = name_x

        # print('unexpected variance {}'.format(unexpected))


        # plt.bar(range(len(c_collector)), c_collector)
        # plt.title('Votes for {} seasonality'.format(name_y))
        # if ticks:
        #     plt.xticks([i for i in range(len(X))], ticks, rotation=90)
        #
        # plt.xlabel('{} data-points'.format(name_x))
        # plt.ylabel('Votes')
        # plt.tight_layout()
        # plt.show()
        #
        # labels = ['{} var not smaller than {} \n'.format(name_y, name_x), 'insignificant difference', '{} var is significantly \nsmaller than {}'.format(name_y, name_x)]
        insignificant_var_perc = insignificant / (len(Y) * len(Y[0])) * 100
        unexpected_var_perc = unexpected / (len(Y) * len(Y[0])) * 100
        expected_var_perc = 100 - unexpected_var_perc
        sizes = [unexpected_var_perc - insignificant_var_perc, insignificant_var_perc, expected_var_perc]
        #
        explode = (0, 0.1, 0.1)
        #
        # patches, _, _ = plt.pie(sizes, explode=explode, autopct='%1.1f%%',
        #         shadow=True, startangle=90)
        # plt.axis('equal')
        # plt.legend(patches, labels, loc="best")
        # plt.title(plt_title)
        # plt.show()
        return winner, sizes, c_collector, [len(Y), len(Y[0])]
