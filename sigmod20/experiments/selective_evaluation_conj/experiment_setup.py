import sys
import os
import shutil
import subprocess
import run_trees, run_qm, run_selective, read_results
from generate_experiments import generate


def prepare(num_params, num_values):
    data_folder = os.getcwd() + '/selective_evaluation_conj/data_trees'
    data_folder_selective = os.getcwd() + '/selective_evaluation_conj/data_selective'
    generate(num_params, num_values, data_folder, min_params=num_params-1)

    if os.path.exists(data_folder_selective):
        shutil.rmtree(data_folder_selective)
    os.makedirs(data_folder_selective)

    experiments_list = os.path.join(data_folder, 'list.txt')
    experiments_list_file = open(experiments_list, 'r')
    data_list = experiments_list_file.readlines()

    experiments_list_selective = os.path.join(data_folder_selective, 'list.txt')
    experiments_list_selective_file = open(experiments_list_selective, "a")

    for experiment_name in data_list:
        shutil.copy(os.path.join(data_folder, experiment_name[:-1] + '.json'), data_folder_selective)
        shutil.copy(os.path.join(data_folder, experiment_name[:-1] + '.vt'), data_folder_selective)
        experiments_list_selective_file.write(experiment_name)


def run():
    max_iter = sys.maxsize

    experiements_path = os.getcwd() + '/selective_evaluation_conj/data_trees'
    run_trees.execute(experiements_path, max_iter=max_iter)
    run_qm.execute(experiements_path, max_iter=max_iter)

    experiements_path = os.getcwd() + '/selective_evaluation_conj/data_selective'
    run_selective.execute(experiements_path, max_iter=max_iter)
    run_qm.execute(experiements_path, max_iter=max_iter)


def read():
    iterations = [sys.maxsize]
    algos = ['bugdoc']
    experiements_path = os.getcwd() + '/selective_evaluation_conj/data_trees'
    read_results.execute(experiements_path, algos, iterations)

    experiements_path = os.getcwd() + '/selective_evaluation_conj/data_selective'
    read_results.execute(experiements_path, algos, iterations)
