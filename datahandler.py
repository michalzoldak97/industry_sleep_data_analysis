from app import app
from datetime import datetime
import joblib
import json
from flask import request, jsonify
from db import conn
import pymysql


state_dict = {0: 'sleep', 1: 'lay', 2: 'active'}


def _fetch_user_sleep_data(usr_id: int):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query_text = 'SELECT ' \
                 'sleep_data ' \
                 'FROM tbl_user_sleep_data ' \
                 'WHERE user_id =' + str(usr_id)

    cursor.execute(query_text)
    return cursor.fetchall()


def _get_all_data(usr_id: int, d_range: tuple):
    rows = _fetch_user_sleep_data(usr_id)

    rows = [eval(rows[i]['sleep_data']) for i, row in enumerate(rows)]
    data_list = []
    for row in rows:
        for k in row.keys():
            data_row = [k, datetime.strptime(k, '%Y-%m-%d %H:%M:%S'), row[k]['HR'], row[k]['VM']]
            if d_range[0] < data_row[1] < d_range[1]:
                data_list.append(data_row)

    return data_list


def _transform_data(usr_id: int, d_range: tuple):
    all_data = _get_all_data(usr_id, d_range)
    for i, row in enumerate(all_data):
        time_vm = row[1].hour + (row[1].minute * .1) + (row[1].second * .01)
        all_data[i] = [row[0], float(row[2]), float(row[3]), time_vm]

    return all_data


def _calc_general_stats(sleep_data: list):
    state_cnt = [0, 0, 0]
    for row in sleep_data:
        state_cnt[row[4]] += 1

    data_len = len(sleep_data)
    stats = {}
    for i, cnt in enumerate(state_cnt):
        stats[state_dict[i]] = '{:.2f}'.format((cnt / data_len) * 100)

    return stats


def _transform_classify_data(sleep_data: list):
    data_dict = {'stats': _calc_general_stats(sleep_data)}
    for row in sleep_data:
        data_dict[row[0]] = {'HR': row[1], 'VM': row[2], 'STATE': state_dict[row[4]]}

    return data_dict


def _classify(usr_id: int, d_range: tuple):
    all_data = _transform_data(usr_id, d_range)
    x_set = [x[1:] for x in all_data]
    classifier = joblib.load('classifiers/rf_one.joblib')
    y_pred = classifier.predict(x_set)
    for i, _ in enumerate(all_data):
        all_data[i].append(y_pred[i])

    return _transform_classify_data(all_data)


@app.route('/')
def check():
    return 'Hello from Flask server'


@app.route('/sleepdata', methods=['GET'])
def select_data():
    if request.method != 'GET':
        return 'Invalid method'

    usr_id = request.args.get('userid')
    from_date = request.args.get('fromdate')
    to_date = request.args.get('todate')

    try:
        usr_id = int(usr_id)
        from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        err_msg = {'Error': 'Query params have invalid format'}
        err_msg = jsonify(err_msg)
        err_msg.status_code = 500
        return err_msg
    try:
        sleep_data = _classify(usr_id, (from_date, to_date))
        res = jsonify(sleep_data)
        res.status_code = 200
        return res
    except:
        err_msg = {'Error': 'Failed to process data'}
        err_msg = jsonify(err_msg)
        err_msg.status_code = 500
        return err_msg


if __name__ == "__main__":
    app.run(debug=True)



