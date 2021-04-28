import argparse
import os
import logging
import json
from bugdoc.algos.debugging_decision_trees import DebuggingDecisionTrees
from bugdoc.algos.stacked_shortcut import StackedShortcut
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def main(args):
    filename = args.file
    logging.info("Debugging: " + filename)
    with open(args.params) as f:
        input_dict = json.load(f)
    logging.debug("Parameters: " + str(input_dict.keys()))
    autodebug = StackedShortcut(separator="#",origin="debug",max_iter=args.budget)
    result = autodebug.run(filename, input_dict, ['result'])
    if len(result) > 1:
        believedecisive, total, _ = result
        logging.info("Shortcut result: "+str(believedecisive))
    autodebug = DebuggingDecisionTrees(separator="#",max_iter=args.budget,k=10,origin="debug")
    believedecisive, t, total = autodebug.run(filename, input_dict, ['result'])
    draw_tree(t)
    results = prune_tree(t, list(input_dict.keys()))
    logging.info("Pruning result: " + str(results))
    with open(args.output,'w+') as f:
        f.write(str(results))


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="path to pipeline entry point")
    parser.add_argument("--budget", type=int, help="maximum number of pipeline instances")
    parser.add_argument("--params", type=str, help="path to json with parameters and values to be investigated")
    parser.add_argument("--output", type=int, help="path to file where results will written to")
    args = parser.parse_args()

    main(args)