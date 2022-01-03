from app import app
import json
from flask import request, jsonify
from db import conn
import pymysql


@app.route('/')
def check():
    return 'Hello from Flask server'


@app.route('/sleepdata', methods=['GET'])
def select_data():
    if request.method != 'GET':
        return 'Invalid method'

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query_text = 'SELECT u.username from tbl_user u WHERE u.user_id = 51'
    cursor.execute(query_text)
    rows = cursor.fetchall()
    res = jsonify(rows)
    res.status_code = 200
    return res


def get_data(usr_id: int, d_range=0):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query_text = 'SELECT ' \
                 'sleep_data ' \
                 'FROM tbl_user_sleep_data ' \
                 'WHERE user_id =' + str(usr_id)

    cursor.execute(query_text)
    rows = cursor.fetchall()

    print(rows[0]['sleep_data'])


get_data(56)

if __name__ == "__main__":
    app.run(debug=True)



