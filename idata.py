import requests
import pandas as pd
import math
import datetime
import time

_main_addr = 'http://127.0.0.1:'
_ports = {'URL': '8090', 'URL_1': '8091', 'URL_2': '8092'}


def _send_test_get():
    endpoint = _main_addr + _ports['URL'] + '/user/2'
    auth_header = {'Authorization': 'Bearer qwer'}
    req = requests.get(endpoint, headers=auth_header).json()
    print(req)


def _login_reg_req(cred, end='login'):
    endpoint = _main_addr + _ports['URL_2'] + '/' + end
    data = {'username': cred[0], 'password': cred[1]}
    return requests.post(endpoint, data=data).json()


def _tp_to_time(tp):
    tp = tp.strip("()").split(", ")
    tp = [int(x) for x in tp]
    try:
        dt = datetime.datetime(tp[0], tp[1], tp[2], tp[3], tp[4], tp[5]).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        dt = datetime.datetime(tp[0], tp[1], 1, tp[3], tp[4], tp[5]).strftime('%Y-%m-%d %H:%M:%S')
    return dt


def _df_row_to_dict(row):
    return {'HR': row.values[0][0], 'VM': row.values[0][1]}


def _df_part_to_dict(df, start_idx):
    test_d = {}
    print(max(df.index))
    for row in df.index:
        test_d[_tp_to_time(df.at[row, 'time'])] = _df_row_to_dict(df.iloc[[start_idx - row]])
    return test_d


def _user_data_to_json(u_idx):
    pth = 'data/userData/' + str(u_idx) + '.csv'
    user_df = pd.read_csv(pth)
    len_df = len(user_df.index)
    num_split = math.floor(len_df / 1000.0)
    num_rest = int(len_df % 1000.0)
    data_jsons = []

    for idx in range(num_split):
        start_idx = idx * 1000
        df_part = user_df[start_idx:(start_idx + 1000)]
        data_jsons.append(_df_part_to_dict(df_part, start_idx))

    start_idx = 1000 * num_split
    df_part = user_df[start_idx:(start_idx + num_rest)]
    data_jsons.append(_df_part_to_dict(df_part, start_idx))

    return data_jsons


def upload_user_data():
    user_df = pd.read_csv('data/sleepUsers.csv')
    endpoint = _main_addr + _ports['URL_1'] + '/smartwatchdata'
    for idx in user_df.index:
        email = user_df.at[idx, 'email']
        password = user_df.at[idx, 'password']
        new_usr = _login_reg_req((email, password), 'register')
        if new_usr['message'] == 'success':
            print('success')
        login_data = _login_reg_req((email, password))
        user_data = _user_data_to_json(idx + 1)
        for patch in user_data:
            auth_data = 'Bearer ' + login_data['token']
            auth_header = {'Authorization': auth_data}
            req = requests.post(endpoint, json=patch, headers=auth_header).json()
            print(req)
            time.sleep(.1)


upload_user_data()