import sys, ast, traceback
import json
from bugdoc.algos.debugging_decision_trees import DebuggingDecisionTrees
from bugdoc.utils.quine_mccluskey import findallpaths, from_paths_to_binary
from bugdoc.utils.selective_instrumentation import Pipeline, node_to_instrument, exclusive_to
from bugdoc.utils.utils import load_runs
from bugdoc.utils import tree
from queue import Queue
import itertools


def execute(experiements_path, max_iter=sys.maxsize, k=1000, use_score=False):
    experiments_list_path = experiements_path + '/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    trees_execution_file = open('%s/trees_%d.txt' % (experiements_path, max_iter), 'a')
    for experiment in alllines:
        experiment_name = experiements_path + '/' + experiment[:-1]
        try:
            json_file = open(experiment_name + ".json", "r")
            json_str = json_file.read().strip()
            json_file.close()
            param_space = ast.literal_eval(json_str)

            #pipeline = Pipeline(param_space)
            #node = node_to_instrument(pipeline)
            mid = (len(param_space.keys()) // 2)
            exclusive_params = [p for p in list(param_space.keys())[:mid]]

            # Run Debugging Decision Trees on node
            selective_param_space = {k: v if k in exclusive_params else [v[0]] for k, v in param_space.items()}
            debug = DebuggingDecisionTrees(first_solution=False, max_iter=max_iter, num_tests=k, use_score=use_score)
            print('Line 35', selective_param_space)
            believedecisive, t, total = debug.run(experiment_name + ".vt", selective_param_space, ['result'])

            if tree.get_depth(t) > 0:
                goodpaths, badpaths, input_dict = findallpaths(t)
                minterms, flatten = from_paths_to_binary(badpaths, input_dict)
            else:
                # Run Debugging Decision Trees not on node
                selective_param_space = {k: v if k not in exclusive_params else [v[0]] for k, v in param_space.items()}
                print('Line 44', selective_param_space)
                debug = DebuggingDecisionTrees(first_solution=False, max_iter=max_iter, num_tests=k, use_score=use_score)
                believedecisive, t, total = debug.run(experiment_name + ".vt", selective_param_space, ['result'])

                if tree.get_depth(t) > 0:
                    goodpaths, badpaths, input_dict = findallpaths(t)
                    minterms, flatten = from_paths_to_binary(badpaths, input_dict)
                else:
                    badpaths = []
                    minterms = []
                    flatten = []
            output_name = ("%s_trees_%d.res") % (experiment_name, max_iter)
            f = open(output_name, "a")
            f.write(str(badpaths) + '\n')
            f.write(str(minterms) + '\n')
            f.write(str(flatten) + '\n')
            f.write(str(total) + '\n')
            f.close()
            trees_execution_file.write(('%s#%d\n') % (output_name, len(flatten)))
        except:
            pass
            traceback.print_exc()
            f = open("%s_trees_%d.res" % (experiment_name, max_iter), 'a')
            f.write("FAIL")
            f.close()
    trees_execution_file.close()
