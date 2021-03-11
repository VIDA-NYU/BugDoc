import os
import json
import ast
import copy
import psycopg2
import traceback
from helpers import *
from bugdoc.utils.utils import load_combinatorial



def workflow_function(kw_args, diagnosis):
    clauses = []
    for clause in diagnosis:
        clauses.append("".join([' kw_args[\'%s\'] %s %s and' % (p,
                                                                clause[p]['cp'],
                                                                "'{}'".format(clause[p]['v'])
                                                                if isinstance(clause[p]['v'], str)
                                                                else clause[p]['v']
                                                                )
                                for p in clause]
                               )
                       [:-4]
                       )
    booleans = []
    for clause in clauses:
        booleans.append(eval(clause))

    return not (bool(sum(booleans)))

def check_diag(diag,kw_args_list,answer_size):
    for clause in diag:
        remove = True
        for kw_args in kw_args_list:
            if not eval("".join([' kw_args[\'%s\'] %s %s and' % (p,
                                                                 clause[p]['cp'],
                                                                 "'{}'".format(clause[p]['v'])
                                                                 if isinstance(clause[p]['v'], str)
                                                                 else clause[p]['v']
                                                                 ) for p in clause])[:-4]):
                remove = False
                break
        if remove and (answer_size <= len(clause)):
            diag.remove(clause)

def false_positive(original_diag,kw_args_list):
    for kw_args in kw_args_list:
        if workflow_function(kw_args, original_diag):
            return True
    return False



def record_algo_result(experiment_name, algo, max_iter):
    agg = open(experiment_name + "_%d.agg" % (max_iter), "a")
    f = open(experiment_name + ".adb", "r")
    provenance = f.readlines()
    f.close()
    false_provenance = []
    for prov in provenance:
        execution = json.loads(prov[:-1])
        if not eval(execution['result']):
            false_provenance.append(execution)

    f = open(experiment_name + ".json", "r")
    param_space = json.loads(f.read())
    f.close()
    params = list(param_space.keys())
    f = open(experiment_name + ".vt", "r")
    diag = ast.literal_eval(f.read())
    f.close()
    original_diag = copy.deepcopy(diag)
    fp = 0
    fn = 0
    tp = 0
    minimal = True
    if algo == 'explanation':
        dbconf = {}
        with open("db.conf") as conffile:
            for line in conffile:
                name, var = line.partition("=")[::2]
                dbconf[name.strip()] = var.strip()

        db = psycopg2.connect(dbname=dbconf['dbname'], user=dbconf['user'], password=dbconf['pass'])
        cur = db.cursor()
        directories = experiment_name.split('/')
        name = directories[-3] + "_" + directories[-2] + "_" + directories[-1]
        sql = "SELECT * FROM %s_%d_richsummary;" %(name,max_iter)
        if exc(db,cur,sql):
            for row in cur:
                kw_args_space = {}
                answer_size = 0
                for param_index in range(len(params)):
                    if row[param_index] is None:
                        kw_args_space[params[param_index]] = param_space[params[param_index]]
                    else:
                        answer_size += 1
                        value = (type(param_space[params[param_index]][0]))(row[param_index])
                        kw_args_space[params[param_index]] = [value]
                if (answer_size == 0) or not (row[len(params) + 2] == 1.0): continue
                num_clauses = len(diag)
                kw_args_list = load_combinatorial(kw_args_space)
                check_diag(diag, kw_args_list, answer_size)
                if num_clauses == len(diag):
                    if false_positive(original_diag, kw_args_list):
                        print(algo, row, original_diag)
                        fp += 1
                    else:
                        minimal = False
                else:
                    tp += (num_clauses - len(diag))

        cur.close()
        db.close()
        fn = len(diag)
    elif algo == 'dataxray':
        f = open(experiment_name + '_output_%d'%(max_iter), 'r')
        xray_result = f.readlines()
        f.close()
        fp = 0
        for line in xray_result:
            xray_cfg = line.split(':')
            kw_args_space = {}
            answer_size = 0
            for param_index in range(len(params)):
                if params[param_index] not in xray_cfg[param_index]:
                    kw_args_space[params[param_index]] = param_space[params[param_index]]
                else:
                    answer_size += 1
                    value = (type(param_space[params[param_index]][0]))(xray_cfg[param_index].split('#')[1])
                    kw_args_space[params[param_index]] = [value]

            num_clauses = len(diag)
            kw_args_list = load_combinatorial(kw_args_space)
            check_diag(diag, kw_args_list,answer_size)
            if num_clauses == len(diag):
                if false_positive(original_diag,kw_args_list):
                    print(algo, line, original_diag)
                    fp += 1
                else:
                    minimal = False
            else:
                tp += (num_clauses - len(diag))
        fn = len(diag)
    elif algo == 'denial4':
        f = open(experiment_name + '_%d.fdr'%(max_iter), 'r')
        denial = f.readlines()
        f.close()
        fp = 0
        for line in denial:
            if '.result<>' not in line: continue
            subresult = line.replace('.result<>','#')
            if '<' in subresult: continue
            if '>' in subresult: continue
            kw_args_space = {}
            answer_size = 0
            answer_params = []
            for param in params:
                if str(param) not in line:
                    kw_args_space[param] = param_space[param]
                else:
                    answer_size += 1
                    answer_params.append(param)
            if len(answer_params) == 0: continue
            matches = []
            for cfg in false_provenance:
                match = {}
                for param in answer_params:
                    match[param] = [cfg[param]]
                match.update(kw_args_space)
                if match not in matches:
                    matches.append(match)
            for match in matches:
                num_clauses = len(diag)
                kw_args_list = load_combinatorial(match)
                check_diag(diag, kw_args_list,answer_size)
                if num_clauses == len(diag):
                    if false_positive(original_diag,kw_args_list):
                        print(algo, line, original_diag)
                        fp += 1
                    else:
                        minimal = False
                else:
                    tp += (num_clauses - len(diag))
        fn = len(diag)
    elif algo == 'bugdoc':
        if os.path.isfile(experiment_name + '_qm_%d.res'%(max_iter)):
            f = open(experiment_name + '_qm_%d.res'%(max_iter), 'r')
            trees_results = ast.literal_eval(f.read())
            f.close()
            fp = 0
            if trees_results is None:
                trees_results = []
            #elif len(trees_results) == 0:
            #    trees_results.append([])

            for triple_list in trees_results:
                param_space_copy = {}
                answer_size = 0
                for triple in triple_list:
                    print(triple)
                    print(param_space_copy)
                    print(param_space)
                    if triple[0] not in param_space_copy:
                        print(param_space[triple[0]])
                        values = [v for v in param_space[triple[0]]
                                  if eval(("'{}'".format(v) if type(v) == str else str(v)) +
                                          triple[1]
                                          + ("'{}'".format(triple[2]) if type(v) == str else str(
                                triple[2])))
                                  ]
                        param_space_copy[triple[0]] = values
                    else:
                        values = [v for v in param_space_copy[triple[0]]
                                  if eval(("'{}'".format(v) if type(v) == str else str(v)) +
                                          triple[1]
                                          + ("'{}'".format(triple[2]) if type(v) == str else str(
                                triple[2])))
                                  ]
                        param_space_copy[triple[0]] = values
                kw_args_space = {}
                for param in params:
                    if param in param_space_copy:
                        answer_size += 1
                        kw_args_space[param] = param_space_copy[param] if len(param_space_copy[param]) > 0 else param_space[param]
                    else:
                        kw_args_space[param] = param_space[param]

                num_clauses = len(diag)
                kw_args_list = load_combinatorial(kw_args_space)
                check_diag(diag, kw_args_list,answer_size)
                if num_clauses == len(diag):
                    if false_positive(original_diag, kw_args_list):
                        print(algo, triple_list, original_diag)
                        fp += 1
                    else:
                        minimal = False
                else:
                    tp += (num_clauses - len(diag))
            fn = len(diag)
        elif os.path.isfile(experiment_name + '_trees_%d.res'%(max_iter)):
            f = open(experiment_name + '_trees_%d.res'%(max_iter), 'r')
            tree_outputs = f.readlines()
            f.close()
            badpaths = None if 'FAIL' in tree_outputs[0] else ast.literal_eval(tree_outputs[0][:-1])
            fp = 0
            if badpaths is None:
                badpaths = []
            elif len(badpaths) == 0:
                badpaths.append([])

            for path in badpaths:
                param_space_copy = {}
                answer_size = 0
                for triple in path:
                    print(triple)
                    print(param_space_copy)
                    print(param_space)
                    isstring = type(triple[1]) == str
                    if triple[2]:
                        comparator = '==' if isstring else '>='
                    else:
                        comparator = '!=' if isstring else '<'
                    if params[triple[0]] not in param_space_copy:
                        for v in param_space[params[triple[0]]]:
                            print(isstring)
                            print(("'{}'".format(v) if isstring else str(v)) +
                                          comparator
                                          + ("'{}'".format(triple[1]) if isstring else str(
                                triple[1])))
                        values = [v for v in param_space[params[triple[0]]]
                                  if eval(("'{}'".format(v) if isstring else str(v)) +
                                          comparator
                                          + ("'{}'".format(triple[1]) if isstring else str(
                                triple[1])))
                                  ]
                        param_space_copy[params[triple[0]]] = values
                    else:
                        values = [v for v in param_space_copy[params[triple[0]]]
                                  if eval(("'{}'".format(v) if isstring else str(v)) +
                                          comparator
                                          + ("'{}'".format(triple[1]) if isstring else str(
                                triple[1])))
                                  ]
                        param_space_copy[params[triple[0]]] = values
                kw_args_space = {}
                for param in params:
                    if param in param_space_copy:
                        answer_size += 1
                        kw_args_space[param] = param_space_copy[param] if len(param_space_copy[param]) > 0 else param_space[param] 
                    else:
                        kw_args_space[param] = param_space[param]

                num_clauses = len(diag)
                kw_args_list = load_combinatorial(kw_args_space)
                check_diag(diag, kw_args_list,answer_size)
                if num_clauses == len(diag):
                    if false_positive(original_diag, kw_args_list):
                        print(algo, path, original_diag)
                        fp += 1
                    else:
                        minimal = False
                else:
                    tp += (num_clauses - len(diag))
            fn = len(diag)
        else:
            f = open(experiment_name + '_list_%d.res' % (max_iter), 'r')
            list_result = json.loads(f.read())
            f.close()
            fp = 0
            for belief in list_result['believedecisive']:
                kw_args_space = {}
                for param_index in range(len(params)):
                    if param_index == belief[0]:
                        kw_args_space[params[param_index]] = [belief[2]]
                    else:
                        kw_args_space[params[param_index]] = param_space[params[param_index]]
                num_clauses = len(diag)
                kw_args_list = load_combinatorial(kw_args_space)
                check_diag(diag, kw_args_list, 1)
                if num_clauses == len(diag):
                    if false_positive(original_diag, kw_args_list):
                        print(algo, belief, original_diag)
                        fp += 1
                    else:
                        minimal = False
                else:
                    tp += (num_clauses - len(diag))
            fn = len(diag)
    elif algo == 'stacked':
        f = open(experiment_name + '_stacked_%d.res' % (max_iter), 'r')
        list_result = json.loads(f.read())
        f.close()
        fp = 0
        for pair_list in list_result["believedecisive"]:
            param_space_copy = {}
            answer_size = 0
            for pair in pair_list:
                param_space_copy[params[pair[0]]] = [pair[1]]
            kw_args_space = {}
            for param in params:
                if param in param_space_copy:
                    answer_size += 1
                    kw_args_space[param] = param_space_copy[param]
                else:
                    kw_args_space[param] = param_space[param]

            num_clauses = len(diag)
            kw_args_list = load_combinatorial(kw_args_space)
            check_diag(diag, kw_args_list, answer_size)
            if num_clauses == len(diag):
                if false_positive(original_diag, kw_args_list):
                    print(algo, pair_list, original_diag)
                    fp += 1
                else:
                    minimal = False
            else:
                tp += (num_clauses - len(diag))
        fn = len(diag)
    elif algo == 'shortcut':
        f = open(experiment_name + '_shortcut_%d.res' % (max_iter), 'r')
        list_result = json.loads(f.read())
        f.close()
        fp = 0
        param_space_copy = {}
        answer_size = 0
        if len(list_result["believedecisive"]) > 0:
            for pair in list_result["believedecisive"]:
                param_space_copy[params[pair[0]]] = [pair[1]]
            kw_args_space = {}
            for param in params:
                if param in param_space_copy:
                    answer_size += 1
                    kw_args_space[param] = param_space_copy[param]
                else:
                    kw_args_space[param] = param_space[param]

            num_clauses = len(diag)
            kw_args_list = load_combinatorial(kw_args_space)
            check_diag(diag, kw_args_list, answer_size)
            if num_clauses == len(diag):
                if false_positive(original_diag, kw_args_list):
                    print(algo, list_result["believedecisive"], original_diag)
                    fp += 1
                else:
                    minimal = False
            else:
                tp += (num_clauses - len(diag))
        fn = len(diag)
    elif algo == 'smac':
        f = open(experiment_name + "_smac_%d.res"%(max_iter), "r")
        kw_args_list = [json.loads(f.read())]
        f.close()
        num_clauses = len(diag)
        check_diag(diag,kw_args_list)
        if num_clauses == len(diag):
            fp += 1
        else:
            tp += (num_clauses - len(diag))
        fn = len(diag)

    agg_result = {'algo': algo, 'fp': fp, 'tp': tp, 'fn': fn, 'minimal':minimal}
    agg.write(json.dumps(agg_result) + '\n')
    agg.close()


def execute(experiements_path, algos, iterations):
    experiments_list_path = experiements_path+'/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    for max_iter in iterations:
        for experiment in alllines:
            experiment_name = os.path.join(experiements_path, experiment[:-1])
            print(experiment_name)
            for algo in algos:
                try:
                    record_algo_result(experiment_name,algo,max_iter)
                except:
                    print("Error")
                    print("-" * 60)
                    traceback.print_exc(file=sys.stdout)
                    print("-" * 60)
