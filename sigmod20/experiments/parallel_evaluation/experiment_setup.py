import sys
import os
import re
import shutil
import json
import numpy as np
import time
import zmq
from bugdoc.algos.debugging_decision_trees import AutoDebug


def prepare(num_params, min_values):

    data_folder = os.getcwd() +'/find_all/data'
    data_folder_parallel = os.getcwd() + '/parallel_evaluation/data'

    if os.path.exists(data_folder_parallel):
        shutil.rmtree(data_folder_parallel)
    os.makedirs(data_folder_parallel)

    experiments_list = os.path.join(data_folder, 'list.txt')
    experiments_list_file = open(experiments_list, 'r')
    data_list = experiments_list_file.readlines()

    experiments_list_parallel = os.path.join(data_folder_parallel,'list.txt')
    experiments_list_parallel_file = open(experiments_list_parallel, "a")
    data_list = [experiment for experiment in data_list if
                      int(experiment.split('_')[3]) == num_params and int(experiment.split('_')[4]) > min_values]
    for experiment_name in data_list:

        shutil.copy(os.path.join(data_folder,experiment_name[:-1]+'.json'), data_folder_parallel)
        shutil.copy(os.path.join(data_folder,experiment_name[:-1]+'.vt'), data_folder_parallel)
        experiments_list_parallel_file.write(experiment_name)

def run():
    experiements_path = os.getcwd() + '/parallel_evaluation/data'
    experiments_list_path = experiements_path + '/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()
    prev = 0
    evaluation = {}
    for core in [1,2,5,10,20,30,40,50]:
        for i in range(core-prev):
            os.system("python ../../test/python_worker.py & disown")
        prev = core
        max_instances = []
        totals = []

        for experiment in alllines:
            f = open(os.path.join(experiements_path,experiment[:-1])+".json", "r")
            param_space = json.loads(f.read())
            f.close()            
            debug = AutoDebug(max_iter=sys.maxsize, return_max_instances = True)
            believedecisive, t, total, max_instances_trees = debug.run(
                os.path.join(experiements_path,experiment[:-1]) + ".vt", param_space, ['result'])
            max_instances.append(max_instances_trees)
            totals.append(total)
            os.remove(os.path.join(experiements_path,experiment[:-1]) + ".adb")
        evaluation[core] = {'total':np.mean(totals), 'max_instances':np.mean(max_instances)}

    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    sender.bind("tcp://{0}:{1}".format("*", '5557'))
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://{0}:{1}".format("*", '5558'))
    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)
    for _ in range(50):
        time.sleep(1)
        sender.send_string('kill')
    poller.unregister(receiver)
    receiver.close()
    sender.close()
    context.term()

    f = open(experiements_path + "/evaluation.json", "w")
    f.write(json.dumps(evaluation))
    f.close()
