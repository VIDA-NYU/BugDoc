import sys
import os
import shutil
from generate_experiments import generate
import run_trees, run_stacked_shortcut, run_shortcut, read_results


def prepare(num_params, num_values):

    data_folder = os.getcwd() +'/count_instances/data_shortcut'
    data_folder_trees = os.getcwd() + '/count_instances/data_trees'
    generate(num_params,num_values,data_folder)

    if os.path.exists(data_folder_trees):
        shutil.rmtree(data_folder_trees)
    os.makedirs(data_folder_trees)

    experiments_list = os.path.join(data_folder,'list.txt')
    experiments_list_file = open(experiments_list, 'r')
    data_list = experiments_list_file.readlines()

    experiments_list_trees = os.path.join(data_folder_trees,'list.txt')
    experiments_list_trees_file = open(experiments_list_trees, "a")


    for experiment_name in data_list:
        shutil.copy(os.path.join(data_folder,experiment_name[:-1]+'.json'), data_folder_trees)
        shutil.copy(os.path.join(data_folder,experiment_name[:-1]+'.vt'), data_folder_trees)
        experiments_list_trees_file.write(experiment_name)


def run():
    max_iter = sys.maxsize
    k=sys.maxsize
    experiments_path = os.getcwd() + '/count_instances/data_shortcut'

    run_shortcut.execute(experiments_path, max_iter=max_iter)
    run_stacked_shortcut.execute(experiments_path, max_iter=max_iter)

    experiments_path = os.getcwd() + '/count_instances/data_trees'
    run_trees.execute(experiments_path, max_iter=max_iter,k=k)




def read():
    iterations = [sys.maxsize]
    algos = ['shortcut','stacked']
    experiements_path = os.getcwd() + '/count_instances/data_shortcut'
    read_results.execute(experiements_path, algos, iterations)

    algos = ['bugdoc']
    experiements_path = os.getcwd() + '/count_instances/data_trees'
    read_results.execute(experiements_path, algos, iterations)

