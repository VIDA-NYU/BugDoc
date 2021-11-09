import json
import pandas as pd
import numpy as np
import os
import random
import shutil
import sys




param_types = [int,float]
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
                cp = random.choice([">="])
            elif v == max(param_space[key]):
                cp = random.choice(["<"])
            else:
                cp = random.choice([">=","<"])
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
            if len(diagnosis) > 1:
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


def generate(num_params, num_values,output_folder, min_params=3):

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    experiments_list_path = output_folder+'/list.txt'
    experiments_list_file = open(experiments_list_path,"a")
    for num_params in [2,4,8,16,32]:#range(min_params,num_params):
        for len_param_values in range(4,5):
            param_space = generate_param_space(num_params,len_param_values)
            for i in range(1,5):
                diag, max_clause = generate_diagnosis(param_space,0.1*i)
                workflow_name = "%s/space_%d_%d_%d_%d_%d"%(output_folder,num_params,len_param_values,i,len(diag),max_clause)
                generate_workflow(param_space,diag, workflow_name)
                experiments_list_file.write("space_%d_%d_%d_%d_%d"%(num_params,len_param_values,i,len(diag),max_clause) + '\n')
    experiments_list_file.close()


def generate_bugs(num_attr, len_bug, num_bugs):
    bugs = []

    for _ in range(num_bugs):
        bugs.append(list(np.random.choice(range(num_attr), len_bug, replace=False)))

    return bugs


def generate_datasets(num_attrs, buggy_cols, buggy_rows):
    df_pass = pd.DataFrame()
    df_fail = pd.DataFrame()

    j = 0
    while j < num_attrs:
        lst_pass = []
        lst_fail = []
        i = 0
        while i < 100:
            lst_pass.append(random.randint(0, 5))
            if j in buggy_cols and i in buggy_rows:
                lst_fail.append(random.randint(200, 300))
            else:
                lst_fail.append(random.randint(0, 5))
            i += 1
        df_pass[j] = lst_pass
        df_fail[j] = lst_fail
        j += 1
    return df_pass, df_fail


def generate_ogt_experiments(max_attrs, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    experiments_list_path = output_folder + '/list.txt'
    experiments_list_file = open(experiments_list_path, "a")
    for num_attrs in range(5, max_attrs):

        for len_bugs in range(1, 2):
            for len_dis in range(1,2):

                bugs = generate_bugs(num_attrs,len_bugs,len_dis)
                print(num_attrs,len_bugs,len_dis, bugs)
                buggy_cols = {x for l in bugs for x in l} # Find columns in bugs

                for affected_rows in [2,4,8,16,32,64]:
                    buggy_rows = np.random.choice(range(100), affected_rows, replace=False)
                    df_pass, df_fail = generate_datasets(num_attrs, buggy_cols, buggy_rows)
                    pipeline_name = os.path.join(output_folder,"synthetic_%d_%d_%d_%d_%d" % (
                        num_attrs,
                        affected_rows,
                        len(buggy_cols),
                        len(bugs),
                        max([len(bug) for bug in bugs])
                    ))
                    print(pipeline_name)
                    os.makedirs(pipeline_name)

                    df_pass.to_csv(os.path.join(pipeline_name,"pass.csv"), index=False)
                    df_fail.to_csv(os.path.join(pipeline_name, "fail.csv"), index=False)

                    config = {
                        "python_module": "synthetic_pipeline",
                        "run": "run",
                        "datasets":
                            [
                                "pass.csv",
                                "fail.csv"
                            ],
                        "columns": [str(a) for a in range(num_attrs)],
                        "encoding": None,
                        "threshold": "0",
                        "bugs": [[str(c) for c in bug] for bug in bugs]
                    }
                    with open(os.path.join(pipeline_name,"config.json"), 'w') as outfile:
                        json.dump(config,outfile)
                    experiments_list_file.write(pipeline_name + '\n')
    experiments_list_file.close()