from builtins import str
from builtins import range
from builtins import object
import os
import pytest
import zmq
import bugdoc.utils.tree as _tree

from bugdoc.algos.debugging_decision_trees import AutoDebug
from bugdoc.utils.quine_mccluskey import prune_tree


@pytest.mark.incremental
class TestBudget(object):

    def kill(self):
        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.bind("tcp://{0}:{1}".format("*", '5557'))
        receiver = context.socket(zmq.PULL)
        receiver.bind("tcp://{0}:{1}".format("*", '5558'))
        poller = zmq.Poller()
        poller.register(receiver, zmq.POLLIN)

        sender.send_string('kill')

        poller.unregister(receiver)
        receiver.close()
        sender.close()
        context.term()

    def test_diagnosis_false(self):
        os.system("python test/python_worker.py & disown")
        space = {'p0':['a','b','c','d','e','f'],'p1':[0,1,2],'p2':['a','b','c','d','e','f']}
        filename = 'test/test_diagnosis.vt'
        outputs = ['result']

        believedecisive, t, total = AutoDebug().run(filename, space, outputs)
        if _tree.get_depth(t) > 0:
            keys = list(space.keys())
            result = prune_tree(t, keys)
            assert 'p1=1' in result[0]
        else:
            assert False

        self.kill()

        assert True



