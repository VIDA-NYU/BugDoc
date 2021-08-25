import argparse
import os
import logging
import json
import time
import zmq
from bugdoc.algos.debugging_decision_trees import DebuggingDecisionTrees
from bugdoc.algos.stacked_shortcut import StackedShortcut
from bugdoc.utils.quine_mccluskey import prune_tree
from bugdoc.utils.tree import draw_tree
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def main(args):
    if args.workers:
        workers = args.workers
    else:
        workers = 4

    if args.budget:
        budget = args.budget
    else:
        budget = 100

    if args.send:
        send = args.send
    else:
        send = '5557'

    if args.receive:
        receive = args.receive
    else:
        receive = '5558'

    filename = args.file


    for _ in range(workers):
        os.system("bugdoc-cli-worker --file %s --receive %s --send %s & disown" %(filename, send, receive))


    with open(filename) as f:
        configuration = json.load(f)

    input_dict = {
        p["name"]:p["values"]
        for p in configuration["parameters"]
    }

    logging.info("Debugging: " + configuration["entry_point"])



    logging.debug("Parameters: " + str(input_dict.keys()))
    autodebug = StackedShortcut(separator="#",
                                origin="debug",
                                max_iter=budget,
                                send=send,
                                receive=receive)
    result = autodebug.run(configuration["entry_point"], input_dict, ['result'])
    if len(result) > 1:
        believedecisive, total, _ = result
        logging.info("Shortcut result: "+str(believedecisive))
    autodebug = DebuggingDecisionTrees(separator="#",
                                       max_iter=budget,
                                       num_tests=10,
                                       origin="debug",
                                       send=send,
                                       receive=receive)
    believedecisive, t, total = autodebug.run(configuration["entry_point"], input_dict, ['result'])
    draw_tree(t)
    results = prune_tree(t, list(input_dict.keys()))

    logging.info("Pruning result: " + str(results))

    with open(configuration["entry_point"] + ".result",'w+') as f:
        f.write(str(results))

    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    sender.bind("tcp://{0}:{1}".format("*", send))
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://{0}:{1}".format("*", receive))
    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)
    for _ in range(workers):
        time.sleep(1)
        sender.send_string('kill')

    poller.unregister(receiver)
    receiver.close()
    sender.close()
    context.term()


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="path to a configuration file describing the pipeline")
    parser.add_argument("--budget", type=int, help="maximum number of pipeline instances")
    parser.add_argument("--send", type=str, help="Socket port used to send messages to worker")
    parser.add_argument("--receive", type=int, help="Socket port used to receive messages from worker")
    parser.add_argument("--workers", type=int, help="number of parallel workers to execute pipelines")
    args = parser.parse_args()

    main(args)