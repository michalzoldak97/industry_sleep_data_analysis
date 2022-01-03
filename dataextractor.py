import pandas as pd
import datetime


def _tp_to_time(tp, is_str=True):
    if is_str:
        tp = tp.strip("()").split(", ")
    tp = [abs(int(x)) for x in tp]
    if not 0 <= tp[3] <= 23:
        tp[3] = 0
    return datetime.datetime(tp[0], tp[1], tp[2], tp[3], tp[4], tp[5])


def _clean_df(pth, file_idx):
    df = pd.read_csv(pth)
    df.drop(columns=['idx', 'Axis1', 'Axis2', 'Axis3', 'Steps', 'Inclinometer Off', 'Inclinometer Standing',
                     'Inclinometer Sitting', 'Inclinometer Lying'], inplace=True)
    for idx, row in enumerate(df.index):
        time_part = df.at[idx, 'time'].split(':')
        df.at[idx, 'time'] = (2021, 12, df.at[idx, 'day'], int(time_part[0]), int(time_part[1]), int(time_part[2]))

    df.drop(columns=['day'], inplace=True)
    pth_to_save = 'data/userData/' + str(file_idx) + '.csv'
    df.to_csv(pth_to_save, index=False)


def _extract_data():
    user_idx = [x for x in range(1, 23)]
    for idx in user_idx:
        pth = 'data/DataPaper/user_' + str(idx) + '/Actigraph.csv'
        _clean_df(pth, idx)


def _add_state():
    df = pd.read_csv('data/userData/7.csv')
    activity = []
    for idx, row in enumerate(df.index):
        curr_time = _tp_to_time(df.at[idx, 'time'])
        if datetime.datetime(2021, 12, 1, 23, 35, 0) < curr_time < datetime.datetime(2021, 12, 2, 9, 0, 0):
            activity.append(0)
        # elif datetime.datetime(2021, 12, 1, 23, 56, 0) < curr_time < datetime.datetime(2021, 12, 2, 6, 40, 0):
        #     activity.append(0)
        else:
            activity.append(2)

    df['activity'] = activity
    df.to_csv('data/userData/7_1.csv', index=False)


def _time_split(tm):
    hm = tm.split(':')
    for idx, part in enumerate(hm):
        if part[0] == '0':
            hm[idx] = part[1:]
    return hm


def _add_state_auto():
    for idx in range(8, 23):
        act_pth = 'data/DataPaper/user_' + str(idx) + '/Activity.csv'
        activity_df = pd.read_csv(act_pth)
        for i in activity_df.index:
            st = _time_split(activity_df.at[i, 'Start'])
            et = _time_split(activity_df.at[i, 'End'])
            activity_df.at[i, 'Start'] = (2021, 12, activity_df.at[i, 'Day'], st[0], st[1], 0)
            activity_df.at[i, 'End'] = (2021, 12, activity_df.at[i, 'Day'], et[0], et[1], 0)
        data_pth = 'data/userData/' + str(idx) + '.csv'
        data_df = pd.read_csv(data_pth)
        for i, row in enumerate(data_df.index):
            data_df.at[i, 'time'] = data_df.at[i, 'time'].replace('-29', '2')
        activity = []
        for i, row in enumerate(data_df.index):
            curr_time = _tp_to_time(data_df.at[i, 'time'])
            has_match = False
            for j in activity_df.index:
                act_start = _tp_to_time(activity_df.at[j, 'Start'], False)
                act_end = _tp_to_time(activity_df.at[j, 'End'], False)
                if act_start < curr_time < act_end:
                    if activity_df.at[j, 'Activity'] == 0:
                        activity.append(0)
                        has_match = True
                        break
                    elif activity_df.at[j, 'Activity'] == 1:
                        activity.append(1)
                        has_match = True
                        break
                    else:
                        activity.append(2)
                        has_match = True
                        break
            if not has_match:
                activity.append(2)
        data_df['activity'] = activity
        new_d_pth = 'data/userData/' + str(idx) + '_1.csv'
        data_df.to_csv(new_d_pth, index=False)
