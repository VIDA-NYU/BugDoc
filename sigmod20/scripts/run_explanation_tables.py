import os
import sys
import subprocess
import time
import traceback
import ast
import psycopg2
from helpers import *
from formulas import *
import explain_LL

sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../vistrails'))

import json


def load_table(filename, input_keys, lims,max_iter):
    directories = filename.split('/')
    name = directories[-3]+"_"+directories[-2]+"_"+directories[-1][:-4]+"_"+str(max_iter)
    print(name)
    if os.path.isfile(filename):
        fileicareabout = open(filename, "r")
    else:
        fileicareabout = open(filename, "w+")
    alllines = fileicareabout.readlines()
    fileicareabout.close()
    feature_vector = "DROP TABLE IF EXISTS "+name+" CASCADE;CREATE TABLE "+name+" (id integer, p integer"
    attr_names = 'id,p'
    for key in input_keys:
        feature_vector += ',' + key + ' varchar(64)'
        attr_names += ',' + key
    feature_vector += ");"
    if lims is None:
        lims = [0, len(alllines)]
    count = 0
    for e in alllines[lims[0]:lims[1]]:
        try:
            exp_dict = json.loads(e.strip())
            result = 0 if eval(exp_dict['result']) else 1
            feature_vector += 'INSERT INTO %s (%s) VALUES(%d,%d' % (
                name, str(attr_names), count, result)
            count +=1
            for key in input_keys:
                v = exp_dict[key]
                feature_vector += ',' + "'{}'".format(str(v))
            feature_vector += ');'
        except:
            print("Error:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
    return feature_vector, count





def execute(experiements_path, max_iter=sys.maxsize, prev=0):
    experiments_list_path = experiements_path + '/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    dbconf = {}
    with open("db.conf") as conffile:
        for line in conffile:
            name, var = line.partition("=")[::2]
            dbconf[name.strip()] = var.strip()

    db = psycopg2.connect(dbname=dbconf['dbname'], user=dbconf['user'], password=dbconf['pass'])
    cur = db.cursor()

    for experiment in alllines:
        experiment_name = experiements_path + '/' + experiment[:-1]
        json_file = open(experiment_name + ".json", "r")
        json_str = json_file.read().strip()
        json_file.close()
        param_space = json.loads(json_str)
        filename = experiment_name + ".adb"
        keys = param_space.keys()

        lims = None if max_iter == sys.maxsize else [prev, prev + max_iter]
        sql, rows = load_table(filename, keys, lims,max_iter)
        exc(db, cur, sql)
        directories = experiment_name.split('/')
        name = directories[-3] + "_" + directories[-2] + "_" + directories[-1] + "_" + str(max_iter)
        try:
            explain_LL.run(name,rows,'4',db,cur)
        except:
            traceback.print_exc()
    cur.close()
    db.close()

