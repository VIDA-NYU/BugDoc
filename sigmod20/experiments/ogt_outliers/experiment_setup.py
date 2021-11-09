import sys
import os
import shutil
import subprocess
import run_ogt, run_outlier, read_ogt_results
from generate_experiments import generate_ogt_experiments


def prepare(num_params):
    data_folder = os.getcwd() + '/ogt_outliers/data'
    generate_ogt_experiments(num_params, data_folder)


def run():
    experiments_path = os.getcwd() + '/ogt_outliers/data'
    run_ogt.execute(experiments_path)
    run_outlier.execute(experiments_path)


def read():
    experiments_path = os.getcwd() + '/ogt_outliers/data'
    algos = ['ogt', 'if', 'ee']
    read_ogt_results.execute(experiments_path, algos)

