from builtins import str
from builtins import range
from builtins import object
import os
import pytest
import zmq
import bugdoc.utils.tree as _tree

from bugdoc.utils.utils import record_python_run, load_runs


@pytest.mark.incremental
class TestRuns(object):



    def test_runs(self):
        run = {'p1':'v1','p2':2, 'p3':0.3, 'result':'False'}
        record_python_run(run, 'test.vt')
        _, runs, _ = load_runs('test.adb',['p1','p2','p3'])
        os.remove('test.adb')
        assert [b'v1',2,0.3,False] == runs[0]


