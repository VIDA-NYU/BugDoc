import argparse
import ast
import logging
import importlib
import json
import os
import sys, traceback
import zmq
from bugdoc.utils.utils import record_pipeline_run
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="path to a configuration file describing the pipeline")
    parser.add_argument("--receive", type=str, help="port to receive messages on")
    parser.add_argument("--send", type=str, help="port to send messages to")
    args = parser.parse_args()

    host = 'localhost'

    if args.receive:
        receive = args.receive
    else:
        receive = '5557'

    if args.send:
        send = args.send
    else:
        send = '5558'

    filename = args.file

    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://{0}:{1}".format(host, receive))

    # Socket to send messages to
    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://{0}:{1}".format(host, send))


    # Process tasks forever
    while True:
        data = receiver.recv_string()
        logging.debug("data: " + data)
        if data == 'kill':
            break
        fields = data.split("#")
        entry_point = fields[0]
        values = ast.literal_eval(fields[1])
        parameters = ast.literal_eval(fields[2])
        kwargs = {
            parameters[i]: values[i]
            for i in range(len(parameters))
        }
        try:
            with open(filename) as f:
                config = json.load(f)
            module = importlib.import_module(config['python_module'])
            run = getattr(module, config['run'])
            result = run(kwargs)
            logging.debug("result: " + str(result))
        except:
            logging.error("Exception in user code:")
            logging.error("-" * 60)
            traceback.print_exc(file=sys.stdout)
            result = False
            logging.error("-" * 60)

        record_pipeline_run(entry_point + ".adb", values, parameters, result)
        values.append(result)
        sender.send_string(str(values))