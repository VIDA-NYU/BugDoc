import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))
import time
import zmq
from ogt_outliers import experiment_setup


for _ in range(5):
   os.system("python ../../test/python_worker_ogt.py & disown")

experiment_setup.prepare(20)
experiment_setup.run()
experiment_setup.read()

context = zmq.Context()
sender = context.socket(zmq.PUSH)
sender.bind("tcp://{0}:{1}".format("*", '5557'))
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://{0}:{1}".format("*", '5558'))
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
for _ in range(5):
    time.sleep(1)
    sender.send_string('kill')
poller.unregister(receiver)
receiver.close()
sender.close()
context.term()