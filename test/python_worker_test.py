from builtins import str
from builtins import object
import os
import pytest
import time
import zmq


@pytest.mark.incremental
class TestPythonWorker(object):



    def test_diagnosis_false(self):

        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.bind("tcp://{0}:{1}".format("*", '5557'))
        receiver = context.socket(zmq.PULL)
        receiver.bind("tcp://{0}:{1}".format("*", '5558'))
        poller = zmq.Poller()
        poller.register(receiver, zmq.POLLIN)

        os.system("python test/python_worker & disown")

        conf = [0,1,2]
        inputs = ['p0','p1','p2']
        filename = 'test/test_diagnosis.vt'
        outputs = ['result']

        message = '|'.join([str(filename),str(conf),str(inputs),str(outputs)])
        sender.send_string(message)
        socks = dict(poller.poll(10000))
        if socks:
             if socks.get(receiver) == zmq.POLLIN:
                 msg = receiver.recv(zmq.NOBLOCK)
                 assert msg.decode() == "[0, 1, 2, 'False']"
        time.sleep(1)
        sender.send_string('kill')

        poller.unregister(receiver)
        receiver.close()
        sender.close()
        context.term()

    def test_diagnosis_true(self):

        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.bind("tcp://{0}:{1}".format("*", '5557'))
        receiver = context.socket(zmq.PULL)
        receiver.bind("tcp://{0}:{1}".format("*", '5558'))
        poller = zmq.Poller()
        poller.register(receiver, zmq.POLLIN)

        os.system("python test/python_worker & disown")

        conf = [0,0,2]
        inputs = ['p0','p1','p2']
        filename = 'test/test_diagnosis.vt'
        outputs = ['result']

        message = '|'.join([str(filename),str(conf),str(inputs),str(outputs)])
        sender.send_string(message)
        socks = dict(poller.poll(10000))
        if socks:
             if socks.get(receiver) == zmq.POLLIN:
                 msg = receiver.recv(zmq.NOBLOCK)
                 assert msg.decode() == "[0, 0, 2, 'True']"

        time.sleep(1)
        sender.send_string('kill')

        poller.unregister(receiver)
        receiver.close()
        sender.close()
        context.term()