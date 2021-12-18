import pandas as pd
import datetime


def tp_to_time(tp):
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
    # _clean_df('data/DataPaper/user_1/Actigraph.csv')


_extract_data()