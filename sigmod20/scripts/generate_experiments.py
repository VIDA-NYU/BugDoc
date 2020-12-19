import numpy as np
import random
import sys, os
import json

import shutil


param_types = [list,int,float]
#param_types = [list] #this is just for the shortcut

def clause_generator(param_space):
    keys = list(param_space.keys())
    keys = np.random.choice(keys,np.random.randint(1,len(keys)), replace = False)
    clause = {}
    for key in keys:
        if isinstance(param_space[key][0],str):
            clause[key] = {'v':random.choice(param_space[key]),'cp':random.choice(["==","!="])}
            #clause[key] = {'v': random.choice(param_space[key]), 'cp': "=="}#again shortcut
        else:
            v = random.choice(param_space[key])
            if v == min(param_space[key]):
                cp = random.choice(["==",">="])
            elif v == max(param_space[key]):
                cp = random.choice(["==","<"])
            else:
                cp = random.choice(["==",">=","<"])
            clause[key] = {'v': v,'cp':cp}
    return clause

def generate_diagnosis(param_space, stop_probability):
    diagnosis = []
    max_clause = 0
   
    while(not(np.random.binomial(1,stop_probability)) or max_clause == 0):
        clause = clause_generator(param_space)
        if len(clause) < 5:
            if len(clause) > max_clause:
                max_clause = len(clause)
            diagnosis.append(clause)
            if len(diagnosis) > 3:
                break
   
    return diagnosis, max_clause

def generate_param_space(num_params, len_param_values):
    param_space = {}
    for i in range(num_params):
        name = 'p' + str(i)
        value_type = random.choice(param_types)
        if (value_type == list):
            values = [name+str(j) for j in range(len_param_values)]
        elif (value_type == int):
            values = list(range(len_param_values))
        else:
            values = list(np.arange(len_param_values*1.0))
        param_space[name] = values
    return param_space

def generate_workflow(param_space, diagnosis, filename,  engine = 'python'):
    print(param_space)
    if engine == 'python':
        params = open(filename+".json", "w+")
        params.write(json.dumps(param_space))
        params.close()
        vt = open(filename+".vt", "w+")
        vt.write(str(diagnosis))
        vt.close()


def generate(num_params, num_values,output_folder):

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    experiments_list_path = output_folder+'/list.txt'
    experiments_list_file = open(experiments_list_path,"a")
    for num_params in range(3,num_params):
        for len_param_values in range(5,num_values):
            param_space = generate_param_space(num_params,len_param_values)
            for i in range(1,4):
                diag, max_clause = generate_diagnosis(param_space,0.1*i)
                workflow_name = "%s/space_%d_%d_%d_%d_%d"%(output_folder,num_params,len_param_values,i,len(diag),max_clause)
                generate_workflow(param_space,diag, workflow_name)
                experiments_list_file.write("space_%d_%d_%d_%d_%d"%(num_params,len_param_values,i,len(diag),max_clause) + '\n')
    experiments_list_file.close()

