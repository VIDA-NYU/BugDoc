import sys
import os
import time
import zmq
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))


from parallel_evaluation import experiment_setup as parallel_setup

parallel_setup.prepare(4,15)
parallel_setup.run()
