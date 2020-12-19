import sys, ast,traceback
import json
from bugdoc.algos.debugging_decision_trees import AutoDebug
from bugdoc.utils.quine_mccluskey import findallpaths, from_paths_to_binary
from bugdoc.utils.utils import load_runs
from bugdoc.utils import tree
from queue import Queue
import itertools






def execute(experiements_path, max_iter = sys.maxsize, mode = 'all', prev = 0,k=1000,use_score=False):
    experiments_list_path = experiements_path+'/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    trees_execution_file = open('%s/trees_%d.txt'%(experiements_path,max_iter),'a')
    for experiment in alllines:
        experiment_name = experiements_path + '/' + experiment[:-1]
        try:
            json_file = open(experiment_name + ".json", "r")
            json_str = json_file.read().strip()
            json_file.close()
            param_space = ast.literal_eval(json_str)

            keys = list(param_space.keys())

            #In complement mode we only proceed if minimal pairs found nothing
            if mode == 'shortcut':
                filename = experiment_name + ".adb"
                lims = None if max_iter == sys.maxsize else [prev, prev + max_iter]
                runs, resultruns,_ = load_runs(filename, keys, lims=lims)
                my_cols = keys + ['result']
                total = len(resultruns)
                t = tree.build(resultruns, cols=my_cols)
            elif mode == 'first':
                debug = AutoDebug(first_solution=True, max_iter=max_iter,k=k,use_score=use_score)
                believedecisive, t, total = debug.run(experiment_name + ".vt", param_space, ['result'])
            else:
                debug = AutoDebug(first_solution=False, max_iter = max_iter,k=k,use_score=use_score)
                believedecisive, t, total = debug.run(experiment_name+".vt",param_space,['result'])

            if tree.get_depth(t) > 0:
                goodpaths,badpaths, input_dict = findallpaths(t)
                minterms, flatten = from_paths_to_binary(badpaths,input_dict)
            else:
                badpaths = []
                minterms = []
                flatten = []
            output_name = ("%s_trees_%d.res") % (experiment_name,max_iter)
            f = open(output_name, "a")
            f.write(str(badpaths) + '\n')
            f.write(str(minterms) + '\n')
            f.write(str(flatten) + '\n')
            f.write(str(total) + '\n')
            f.close()
            trees_execution_file.write(('%s#%d\n')%(output_name,len(flatten)))
        except:
            pass
            traceback.print_exc()
            f = open("%s_trees_%d.res" % (experiment_name,max_iter),'a')
            f.write("FAIL")
            f.close()
    trees_execution_file.close()


