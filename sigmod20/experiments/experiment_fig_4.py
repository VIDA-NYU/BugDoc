import sys
import os
import time
import zmq
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))
from find_all import experiment_setup as all_setup

all_setup.read_answers()
