import smac
import sys, os
import json
import ast
import numpy as np

import shutil

# Import ConfigSpace and different types of parameters
from smac.configspace import ConfigurationSpace
from smac.facade.smac_hpo_facade import SMAC4HPO
# Import SMAC-utilities
from smac.scenario.scenario import Scenario

from ConfigSpace.hyperparameters import CategoricalHyperparameter,UniformFloatHyperparameter,\
UniformIntegerHyperparameter

def workflow_function(kw_args,diagnosis):
    clauses = []
    for clause in diagnosis:
        clauses.append("".join([' kw_args[\'%s\'] %s %s and'%(p,
                                                          clause[p]['cp'],
                                                          "'{}'".format(clause[p]['v'])
                                                          if isinstance(clause[p]['v'],str)
                                                          else clause[p]['v'] 
                                                          )
                             for p in clause]
                            )
                   [:-4]
                   )
    booleans = []
    for clause in clauses:
        booleans.append(eval(clause))
        
    return not(bool(sum(booleans)))

def record_python_run(paramDict, file_name):
    f = open(file_name, "a")
    f.write(json.dumps(paramDict) + '\n')
    f.close()

def cfg_from_param_space(param_space):
    # Build Configuration Space which defines all parameters and their ranges
    cs = ConfigurationSpace()
    for param in param_space:
        values = param_space[param]
        default = values[0]
        if isinstance(default,str):
            cs_param = CategoricalHyperparameter(param, values, default_value=default)
        elif isinstance(default,int):
            cs_param = UniformIntegerHyperparameter(param,default,values[-1], default_value = default)
        else:
            cs_param = UniformFloatHyperparameter(param,default,values[-1], default_value = default)
        cs.add_hyperparameter(cs_param)
    return cs

def get_smac(experiment_name, max_tests):
    f = open(experiment_name+".json", "r")
    param_space = ast.literal_eval(f.read())
    f.close()
    f = open(experiment_name+".vt", "r")
    diag = ast.literal_eval(f.read())
    f.close()

    if max_tests == 0:
        f = open(experiment_name.replace('data_smac','data')+ ".adb", "r")
        max_tests = len(f.readlines())
        f.close()

    dims = experiment_name[experiment_name.rfind('space_'):].split('_')
    pot = int(dims[1])
    base = int(dims[2])
    permutations = base ** pot


    def runner(cfg):
        kw_args = {k: cfg[k] for k in cfg}
        kw_args['result'] = str(workflow_function(kw_args,diag))
        record_python_run(kw_args,experiment_name+'.adb')
        return int(eval(kw_args['result']))
    
    cs = cfg_from_param_space(param_space)
    scenario = Scenario({"run_obj": "quality",  # we optimize quality (alternatively runtime)
                             "runcount-limit": min([permutations,max_tests]),  # maximum function evaluations
                             "cs": cs,  # configuration space
                             "deterministic": "true",
                             "output_dir": "/tmp/"
                             })
    smac_instance = SMAC4HPO(scenario=scenario, rng=np.random.RandomState(42),
                    tae_runner=runner)
    return smac_instance




def execute(experiements_path, max_iter = 0):
    experiments_list_path = experiements_path+'/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()
    for experiment in alllines:
        experiment_name = os.path.join(experiements_path,experiment[:-1])
        print('experiment_name', experiment_name,str(max_iter))
        smac_instance = get_smac(experiment_name,max_iter)
        cfg = smac_instance.optimize()
        print('experiment_name', experiment_name,'finished')
        result_dict = {k: cfg[k] for k in cfg}
        #result_dict['runs'] = smac_instance.stats.ta_runs
        f = open("%s_smac_%d.res"%(experiment_name,max_iter),"a")
        f.write(json.dumps(result_dict))
        f.close()
        for f in os.listdir('/tmp'):
            if 'run_1' in f:
                shutil.rmtree('/tmp/'+f)


if __name__== '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], max_iter=int(sys.argv[2]))
    else:
        execute(sys.argv[1])

