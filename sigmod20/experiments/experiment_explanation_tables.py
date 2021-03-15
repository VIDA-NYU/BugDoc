import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))

from find_all import experiment_setup as all_setup
from find_all_shortcut import experiment_setup as all_shortcut_setup
from find_all_stacked import experiment_setup as all_stacked_setup
from find_one import experiment_setup as one_setup
from find_one_shortcut import experiment_setup as one_shortcut_setup
from find_one_stacked import experiment_setup as one_stacked_setup

import run_explanation_tables

max_iter = sys.maxsize
prev = 0

directories = [
    '/find_all/data',
    '/find_all/data_smac',
    '/find_all_shortcut/data',
    '/find_all_shortcut/data_smac',
    '/find_all_stacked/data',
    '/find_all_stacked/data_smac',
    '/find_one/data',
    '/find_one/data_smac',
    '/find_one_shortcut/data',
    '/find_one_shortcut/data_smac',
    '/find_one_stacked/data',
    '/find_one_stacked/data_smac'
    ]

for d in directories:
    experiements_path = os.getcwd() + d
    run_explanation_tables.execute(experiements_path, max_iter=max_iter, prev=prev)


all_setup.read()
all_setup.read_answers()

all_shortcut_setup.read()

all_stacked_setup.read()

one_setup.read()

one_shortcut_setup.read()

one_stacked_setup.read()

