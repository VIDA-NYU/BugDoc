"""
Worker script
===========================

This script responsible for receiving pipeline configurations from BugDoc's algorithms.
It runs and evaluates the pipeline instances, and returns the result to BugDoc.
"""

# %%
# Importing necessary packages.
# ------------------------
# We load utility packages to open communication and store pipeline instances.

import ast
import sys
import traceback
import zmq
from bugdoc.utils.utils import record_pipeline_run

# %%
# Importing pipeline engine API.
# ------------------------
# Here we load the functions that execute and evaluate a pipeline instance.
from my_api_example import execute_pipeline, evaluate_pipeline_output


host = 'localhost'
receive = '5557'
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
    data = receiver.recv_string()
    fields = data.split("|")
    filename = fields[0]
    values = ast.literal_eval(fields[1])
    parameters = ast.literal_eval(fields[2])
    try:
        configuration = {
            parameters[i]: values[i]
            for i in range(len(parameters))
        }
        output = execute_pipeline(filename, configuration)
        result = evaluate_pipeline_output(output)
    except:
        traceback.print_exc(file=sys.stdout)
        result = False
  
    record_pipeline_run(filename, values, parameters, result)
    values.append(result)
    sender.send_string(str(values))
