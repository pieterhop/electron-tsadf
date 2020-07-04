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



# final_plot(raw_df[0:2000], 204, 182)
