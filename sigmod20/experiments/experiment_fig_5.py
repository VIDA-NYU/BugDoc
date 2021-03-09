import sys
import os
import time
import zmq
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))


from count_instances import experiment_setup as count_setup

for _ in range(5):
    os.system("python ../../test/python_worker.py & disown")

count_setup.prepare(20,6)
count_setup.run()
count_setup.read()


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
