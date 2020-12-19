import sys
import os
import time
import zmq
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../scripts'))


from count_instances import experiment_setup as count_setup
from find_all import experiment_setup as all_setup
from find_all_shortcut import experiment_setup as all_shortcut_setup
from find_all_stacked import experiment_setup as all_stacked_setup
from find_one import experiment_setup as one_setup
from find_one_shortcut import experiment_setup as one_shortcut_setup
from find_one_stacked import experiment_setup as one_stacked_setup
from parallel_evaluation import experiment_setup as parallel_setup

for _ in range(5):
    os.system("python ../../test/python_worker.py & disown")

count_setup.prepare(20,6)
count_setup.run()
count_setup.read()


all_setup.prepare(5,8)
all_setup.run()
all_setup.read()
all_setup.read_answers()



all_shortcut_setup.prepare(5,8)
all_shortcut_setup.run()
all_shortcut_setup.read()

all_stacked_setup.prepare(5,8)
all_stacked_setup.run()
all_stacked_setup.read()

one_setup.prepare(5,8)
one_setup.run()
one_setup.read()

one_shortcut_setup.prepare(5,8)
one_shortcut_setup.run()
one_shortcut_setup.read()

one_stacked_setup.prepare(5,8)
one_stacked_setup.run()
one_stacked_setup.read()


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


parallel_setup.prepare(4,22)
parallel_setup.run()

#real_setup.prepare()
#real_setup.run()
#real_setup.read()

#polygamy_setup.prepare()
#polygamy_setup.run()
#polygamy_setup.read()


#kaggle_setup.run()
#kaggle_setup.read()

#kaggle_all_setup.run()
#kaggle_all_setup.read()

#sherlock_setup.prepare()
#sherlock_setup.run()
#sherlock_setup.read()
#all_setup.prepare(6,20)
#all_setup.run()
#all_setup.read()
