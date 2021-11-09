import os
import json
import ast
import copy
import pandas as pd
import sys
import traceback


def record_algo_result(experiment_name, algo):

    agg = open(os.path.join(experiment_name, "results.agg"), "a")
    with open(os.path.join(experiment_name, "config.json"), "r") as infile:
        config = json.load(infile)
    buggy_cols = {x for l in config["bugs"] for x in l}
    fps = []
    fns = []
    tps = []
    if algo == 'ogt':
        fp = 0
        fn = 0
        tp = 0
        f = open(os.path.join(experiment_name, "ogt.res"), 'r')
        result = ast.literal_eval(f.read().strip())
        f.close()

        fail_dataframe = pd.read_csv(os.path.join(experiment_name, "fail.csv"))
        for c in buggy_cols:
            for i in range(100):
                if fail_dataframe[c].iloc[i] > 10:
                    if len(result) == 2:
                        if i in result[1]:
                            tp += 1
                        else:
                            fn += 1
                    else:
                        fn += 1
                else:
                    if len(result) == 2:
                        if i in result[1]:
                            fp += 1
        for _ in range(6):
            fps.append(fp)
            fns.append(fn)
            tps.append(tp)
    else:
        f = open(os.path.join(experiment_name, algo+".res"), 'r')
        lines = f.readlines()
        f.close()
        for l in lines:

            result = ast.literal_eval(l.strip())
            fp = 0
            fn = 0
            tp = 0

            fail_dataframe = pd.read_csv(os.path.join(experiment_name, "fail.csv"))
            for c in buggy_cols:
                for i in range(100):
                    if fail_dataframe[c].iloc[i] > 10:
                        if i in result:
                            tp += 1
                        else:
                            fn += 1
                    else:
                        if i in result:
                            fp += 1
            fps.append(fp)
            fns.append(fn)
            tps.append(tp)
    agg_result = {'algo': algo, 'fp': fps, 'tp': tps, 'fn': fns}
    agg.write(json.dumps(agg_result) + '\n')
    agg.close()


def execute(experiments_path, algos):
    experiments_list_path = experiments_path + '/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    for experiment in alllines:
        experiment_name = os.path.join(experiments_path, experiment[:-1])
        if os.path.exists(os.path.join(experiment_name, "results.agg")):
            os.remove(os.path.join(experiment_name, "results.agg"))
        for algo in algos:
            try:
                print("record_algo_result", algo)
                record_algo_result(experiment_name,algo)
            except:
                print("Error")
                print("-" * 60)
                traceback.print_exc(file=sys.stdout)
                print("-" * 60)
