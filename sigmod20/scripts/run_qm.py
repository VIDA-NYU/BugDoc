import sys, traceback
from bugdoc.utils.quine_mccluskey import reduce_terms
import ast

def execute(experiements_path, max_iter = sys.maxsize):
    experiments_list_path = '%s/trees_%d.txt'%(experiements_path,max_iter)
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    alllines = sorted(alllines, key=lambda line: int(line.split('#')[-1][:-1]))
    print(str(alllines))
    for experiment in alllines:
        try:
            experiment_name = experiment[:experiment.rfind('_trees')]
            print(experiment_name)
            json_file = open(experiment_name + ".json", "r")
            json_str = json_file.read().strip()
            json_file.close()
            param_space = ast.literal_eval(json_str)
            f = open('%s_trees_%d.res'%(experiment_name,max_iter), "r")
            tree_outputs = f.readlines()
            f.close()
            results = [] if ( ast.literal_eval(tree_outputs[0][:-1]) is not None) else None
            minterms = ast.literal_eval(tree_outputs[1][:-1])
            flatten = ast.literal_eval(tree_outputs[2][:-1])
            keys = list(param_space.keys())
            if len(flatten) > 0:
                if len(flatten) > 10: continue
                s = reduce_terms(len(flatten),minterms)
                for prime in s:
                    result = []
                    for i in range(len(prime)):
                        if prime[i] == '1':
                            comparator = '==' if isinstance(flatten[i][1], str)  else '>='
                            result.append((keys[flatten[i][0]], comparator , str(flatten[i][1])))
                        elif prime[i] == '0':
                            comparator = '!=' if isinstance(flatten[i][1], str) else '<'
                            result.append((keys[flatten[i][0]] , comparator , str(flatten[i][1])))
                    results.append(result)

            print(results)
            f = open("%s_qm_%d.res" % (experiment_name,max_iter),"a")
            f.write(str(results))
            f.close()
        except:
            traceback.print_exc()
            f = open("%s_qm_%d.res" % (experiment_name,max_iter),"a")
            f.write("FAIL")
            f.close()


