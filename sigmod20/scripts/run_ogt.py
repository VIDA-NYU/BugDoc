import ast
import os
import sys
import traceback
from bugdoc.algos.opportunistic_group_testing import AutoDebug


def execute(experiements_path):
    experiments_list_path = os.path.join(experiements_path, 'list.txt')
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    for experiment in alllines:
        experiment_name = os.path.join(experiements_path, experiment[:-1])
        try:
            debug = AutoDebug()
            believedecisive = debug.run(experiment_name, {},
                                        os.path.join(experiment_name, "fail.csv"),
                                        [os.path.join(experiment_name, "pass.csv")],
                                        ['result'])
            output_name = os.path.join(experiment_name, "ogt.res")
            f = open(output_name, "a")
            f.write(str(believedecisive))
            f.close()
        except:
            pass
            traceback.print_exc()
            output_name = os.path.join(experiment_name, "ogt.res")
            f = open(output_name, "a")
            f.write("FAIL")
            f.close()
