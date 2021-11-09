import argparse
import ast
import copy
import logging
import importlib
import json
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '../scripts'))
import traceback
import zmq
from bugdoc.utils.utils import record_python_run

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def workflow_function(kw_args, filename):
    dataset = kw_args["dataset"]
    with open(os.path.join(filename,'config.json'), 'r') as infile:
        config = json.load(infile)

    module = importlib.import_module(config["python_module"])
    run = getattr(module,'run')
    return run(dataset, config["threshold"], config["bugs"])


parser = argparse.ArgumentParser()
parser.add_argument("--server", type=str, help="host responsible for execution requests")
parser.add_argument("--receive", type=str, help="port to receive messages on")
parser.add_argument("--send", type=str, help="port to send messages to")
args = parser.parse_args()

if args.server:
    host = args.server
else:
    host = 'localhost'

if args.receive:
    receive = args.receive
else:
    receive = '5557'

if args.send:
    send = args.send
else:
    send = '5558'


context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://{0}:{1}".format(host, receive))

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://{0}:{1}".format(host, send))

# Process tasks forever
while True:
    data = receiver.recv().decode()
    logging.debug("data: " + data)
    if data == 'kill':
        break

    filename, parameter_list, inputs, outputs = data.split("|")
    parameter_list = ast.literal_eval(parameter_list)
    inputs = ast.literal_eval(inputs)
    outputs = ast.literal_eval(outputs)
    kwargs = {}

    for i in range(len(parameter_list)):
        kwargs[inputs[i]] = parameter_list[i]
    try:
        result = workflow_function(kwargs, filename)
        logging.debug("result: " + str(result))
        parameter_list.append(str(result))
    except:
        logging.error("Exception in user code:")
        logging.error("-" * 60)
        traceback.print_exc(file=sys.stdout)
        logging.error("-" * 60)
        parameter_list.append(str(False))

    kwargs['result'] = parameter_list[-1]
    record_python_run(kwargs, os.path.join(filename,'pipeline.vt'))
    sender.send_string(str(parameter_list))

