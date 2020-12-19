import os
import sys
import subprocess
import time
import ast
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.path.join(os.getcwd(), '../vistrails'))
from bugdoc.utils.utils import load_dataxray

def execute(experiements_path, max_iter = sys.maxsize, prev = 0):
    experiments_list_path = experiements_path+'/list.txt'
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    dataxray_folder = '../../../dataxray-source-code/dataxray'

    for experiment in alllines:
        experiment_name = experiements_path + '/' + experiment[:-1]
        print(experiment_name)
        json_file = open(experiment_name + ".json", "r")
        json_str = json_file.read().strip()
        json_file.close()
        param_space = ast.literal_eval(json_str)
        filename = experiment_name+".adb"
        keys = list(param_space.keys())

        lims = None if max_iter == sys.maxsize else [prev,prev+max_iter]
        dataxrayinput = load_dataxray(filename,keys, lims)

        #Save data dataxrayinput to file
        infile = experiment_name+"_input_"+str(max_iter)
        text_file = open(infile, "w")
        text_file.write(dataxrayinput)
        text_file.close()

        #creating output file
        outfile = experiment_name+"_output_"+str(max_iter)
        open(outfile, 'a').close


        start_time = time.time()
        subprocess.call('java -jar %s/dataxray.jar -I %s -O %s'%(dataxray_folder,infile,outfile),shell=True)
        end_time = time.time()

        text_file = open(outfile, "r")
        output_string = text_file.read()
        text_file.close()
        print(output_string)

