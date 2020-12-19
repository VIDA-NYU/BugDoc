import sys
import os
import shutil
import subprocess
from generate_experiments import generate
import run_trees, run_qm, run_data_xray, run_explanation_tables,run_shortcut, \
    run_smac, run_stacked_shortcut, read_results


def prepare(num_params, num_values):
    data_folder = os.getcwd() + '/find_one_shortcut/data'
    data_folder_smac = os.getcwd() + '/find_one_shortcut/data_smac'
    generate(num_params, num_values, data_folder)

    if os.path.exists(data_folder_smac):
        shutil.rmtree(data_folder_smac)
    os.makedirs(data_folder_smac)

    experiments_list = os.path.join(data_folder, 'list.txt')
    experiments_list_file = open(experiments_list, 'r')
    data_list = experiments_list_file.readlines()

    experiments_list_smac = os.path.join(data_folder_smac, 'list.txt')
    experiments_list_smac_file = open(experiments_list_smac, "a")

    for experiment_name in data_list:
        shutil.copy(os.path.join(data_folder, experiment_name[:-1] + '.json'), data_folder_smac)
        shutil.copy(os.path.join(data_folder, experiment_name[:-1] + '.vt'), data_folder_smac)
        experiments_list_smac_file.write(experiment_name)


def run():
    max_iter = sys.maxsize
    prev = 0

    experiements_path = os.getcwd() + '/find_one_shortcut/data'
    run_shortcut.execute(experiements_path, max_iter=max_iter)
    run_stacked_shortcut.execute(experiements_path, k=1, max_iter=max_iter)
    run_data_xray.execute(experiements_path, max_iter=max_iter, prev=prev)
    run_explanation_tables.execute(experiements_path, max_iter=max_iter, prev=prev)

    experiements_path = os.getcwd() + '/find_one_shortcut/data_smac'

    run_smac.execute(experiements_path, 0)
    run_data_xray.execute(experiements_path, max_iter=max_iter, prev=prev)
    run_explanation_tables.execute(experiements_path, max_iter=max_iter, prev=prev)

    experiements_path = os.getcwd() + '/find_one_shortcut/data'
    run_trees.execute(experiements_path, max_iter=max_iter, mode='shortcut')
    run_qm.execute(experiements_path, max_iter=max_iter)


def read():
    iterations = [sys.maxsize]
    algos = ['shortcut', 'stacked', 'bugdoc', 'dataxray', 'explanation']
    experiements_path = os.getcwd() + '/find_one_shortcut/data'
    read_results.execute(experiements_path, algos, iterations)

    algos = ['dataxray', 'explanation']
    experiements_path = os.getcwd() + '/find_one_shortcut/data_smac'

    read_results.execute(experiements_path, algos, iterations)

