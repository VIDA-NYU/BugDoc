import sys
import os
import time
import zmq
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))

# from selective_evaluation_conj import experiment_setup as selective_conj_setup
# from selective_evaluation_dis import experiment_setup as selective_dis_setup
# from selective_evaluation_ineq_dis import experiment_setup as selective_ineq_dis_setup
# from selective_evaluation_ineq_conj import experiment_setup as selective_ineq_conj_setup

from selective_evaluation_ineq_dis_parameters import experiment_setup as selective_setup

for _ in range(5):
    os.system("python ../../test/python_worker.py & disown")

selective_setup.prepare(20,5)
selective_setup.run()

# selective_conj_setup.run()
# selective_dis_setup.run()
# selective_ineq_conj_setup.run()
# selective_ineq_dis_setup.run()

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