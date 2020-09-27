from __future__ import print_function
from builtins import str
from builtins import range
import argparse
import ast
import sys
import traceback
import zmq

from bugdoc.utils.utils import record_python_run


def workflow_function(kw_args, diagnosis):
    clauses = []
    for clause in diagnosis:
        clauses.append("".join([' kw_args[\'%s\'] %s %s and' % (p,
                                                                clause[p]['cp'],
                                                                "'{}'".format(clause[p]['v'])
                                                                if isinstance(clause[p]['v'], str)
                                                                else clause[p]['v']
                                                                )
                                for p in clause]
                               )
                       [:-4]
                       )
    booleans = [eval(clause) for clause in clauses]
    return not (bool(sum(booleans)))


parser = argparse.ArgumentParser()
parser.add_argument("--server", type=str, help="host responsible for execution requests")
parser.add_argument("--receive", type=str, help="port to receive messages on")
parser.add_argument("--send", type=str, help="port to send messages to")
args = parser.parse_args()

if args.server:
    HOST = args.server
else:
    HOST = 'localhost'

if args.receive:
    RECEIVE = args.receive
else:
    RECEIVE = '5557'

if args.send:
    SEND = args.send
else:
    SEND = '5558'

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://{0}:{1}".format(HOST, RECEIVE))

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://{0}:{1}".format(HOST, SEND))

# Process tasks forever
while True:
    data = receiver.recv().decode()
    if data == 'kill':
        break
    fields = data.split("|")
    filename = fields[0]
    parameter_list = ast.literal_eval(fields[1])
    inputs = ast.literal_eval(fields[2])
    outputs = ast.literal_eval(fields[3])

    f = open(filename, "r")
    diag = ast.literal_eval(f.read())
    f.close()

    kw_args = {}
    for i in range(len(parameter_list)):
        kw_args[inputs[i]] = parameter_list[i]
    try:
        result = workflow_function(kw_args, diag)
        parameter_list.append(result)

    except:
        print("Exception in user code:")
        print("-" * 60)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
        parameter_list.append(False)

    kw_args['result'] = str(parameter_list[-1])
    origin = None
    if len(fields) == 5:
        origin = fields[4]
    record_python_run(kw_args, filename, origin=origin)
    sender.send_string(str(parameter_list))
