import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import multiprocessing as mlpt
import joblib


def _transform_data(df):
    data_list = []
    for idx in df.index:
        time_tp = eval(df.at[idx, 'time'])[3:]
        time_vm = time_tp[0] + (time_tp[1] * .1) + (time_tp[2] * .01)
        data_row = [df.at[idx, 'HR'], df.at[idx, 'Vector Magnitude'], time_vm, df.at[idx, 'activity']]
        data_list.append(data_row)

    return data_list


def _mlpt_append_list(idx: int, lst):
    for i in range(2):
        df_pth = 'data/userData/' + str(idx + i) + '_1.csv'
        lst.append(_transform_data(pd.read_csv(df_pth)))


def _load_data(n_threads=11):
    manager = mlpt.Manager()
    mlpt_lists = [manager.list() for _ in range(n_threads)]
    all_data = []
    processes = []
    p_cnt = 0
    for i in range(1, 23, 2):
        processes.append(mlpt.Process(target=_mlpt_append_list, args=(i, mlpt_lists[p_cnt])))
        p_cnt += 1

    for i in range(n_threads):
        processes[i].start()
    for i in range(n_threads):
        processes[i].join()

    for i in range(n_threads):
        all_data += list(mlpt_lists[i])

    all_data = [item for sublist in all_data for item in sublist]
    return all_data


def _calc_acc(y_pred, y_true):
    good = 0
    good_cls = [0, 0, 0]
    all_cls = [0, 0, 0]

    all_y = 0
    for i, pred in enumerate(y_pred):
        if pred == y_true[i]:
            good += 1
            if pred == 0:
                good_cls[0] += 1
            elif pred == 1:
                good_cls[1] += 1
            elif pred == 2:
                good_cls[2] += 1
        if y_true[i] == 0:
            all_cls[0] += 1
        elif y_true[i] == 1:
            all_cls[1] += 1
        elif y_true[i] == 2:
            all_cls[2] += 1
        all_y += 1

    print("Good {} for All {} = {}%  \n all good{}  all cls {} \n 0 res = {}, 1 res = {}, 2 res = {}".format(good, all_y, ((good / all_y) * 100), all_cls, good_cls, ((good_cls[0] / all_cls[0]) * 100), ((good_cls[1] / all_cls[1]) * 100), ((good_cls[2] / all_cls[2]) * 100)))


def classify():
    sleep_data = _load_data()
    x_set = [el[:3] for el in sleep_data]
    y_set = [el[3] for el in sleep_data]
    x_train, x_test, y_train, y_test = train_test_split(x_set, y_set, test_size=.2, random_state=21)
    classifier = RandomForestClassifier(n_estimators=100, n_jobs=-1, max_depth=25, criterion='gini', random_state=21)
    classifier.fit(x_train, y_train)
    y_pred = classifier.predict(x_test)
    _calc_acc(y_pred, y_test)
    joblib.dump(classifier, 'classifiers/rf_one.joblib', compress=3)


classify()
