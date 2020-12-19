import sys, ast
import json
from bugdoc.algos.shortcut import AutoDebug

def execute(experiements_path,max_iter = sys.maxsize, k=4,use_score=False):

    experiments_list_path = experiements_path+'/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    for experiment in alllines:
        experiment_name = experiements_path + '/' + experiment[:-1]
        json_file = open(experiment_name+".json", "r")
        json_str = json_file.read().strip()
        json_file.close()
        param_space = ast.literal_eval(json_str)

        autodebug = AutoDebug(max_iter=max_iter,k=k,use_score=use_score)
        believedecisive, num_tests = autodebug.run(experiment_name+".vt",param_space,['result'])
        result_dict = {'believedecisive': believedecisive, 'total':num_tests}
        f = open(experiment_name+"_shortcut_%d.res"%(max_iter),"a")
        f.write(json.dumps(result_dict))
        f.close()
        print('believedecisive',believedecisive)