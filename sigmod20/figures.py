import os
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties
import numpy as np
from scripts.plots import  plot_parallel, plot_answer_sizes, plot_budget_complete_general, plot_first_real

fontP = FontProperties()
fontP.set_size('small')


# ===================================== Find One Start ==========================================================

folders = ['data','data_smac']
algos = ['shortcut','stacked','bugdoc','dataxray','dataxray_data_smac','explanation','explanation_data_smac']
labels = ['Shortcut','Stacked Shortcut','Debugging Decision Trees','Data X-Ray (BugDoc)','Data X-Ray (SMAC)','Explanation Tables (BugDoc)','Explanation Tables (SMAC)']
iterations = ['Shortcut budget','Stacked budget','Decision Trees budget']

budgetlines = []
experiements_paths = []

experiements_path = os.getcwd()+'/experiments/find_one_shortcut/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
experiements_paths.append(experiements_path)


budgetlines.append(alllines)


experiements_path = os.getcwd()+'/experiments/find_one_stacked/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
experiements_paths.append(experiements_path)

budgetlines.append(alllines)


experiements_path = os.getcwd()+'/experiments/find_one/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
experiements_paths.append(experiements_path)

budgetlines.append(alllines)



# Figures 2a, 2b, 2c
filtered_lines = [[experiment for experiment in alllines if int(experiment.split('_')[-2]) == 1 and int(experiment.split('_')[-1][:-1]) == 1] for alllines in budgetlines]
plot_budget_complete_general(experiements_paths, filtered_lines, 'Figure 2',algos,labels,folders,iterations,
                             suffix = ['a','b', 'c'], findAll=False)

# Figures 2d, 2e, 2f
filtered_lines = [[experiment for experiment in alllines if int(experiment.split('_')[-2]) == 1 and int(experiment.split('_')[-1][:-1]) > 1]for alllines in budgetlines]
plot_budget_complete_general(experiements_paths, filtered_lines, 'Figure 2',algos,labels,folders,iterations,
                             suffix=['d', 'e', 'f'], findAll=False)

# Figures 2g, 2h, 2i
filtered_lines = [[experiment for experiment in alllines if int(experiment.split('_')[-2]) > 1 and int(experiment.split('_')[-1][:-1]) >= 1]for alllines in budgetlines]
plot_budget_complete_general(experiements_paths, filtered_lines, 'Figure 2',algos,labels,folders,iterations,
                             suffix=['g', 'h', 'i'], findAll=False)


# ===================================== Find All ==========================================================


budgetlines = []
experiements_paths = []

experiements_path = os.getcwd()+'/experiments/find_all_shortcut/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
experiements_paths.append(experiements_path)


budgetlines.append(alllines)


experiements_path = os.getcwd()+'/experiments/find_all_stacked/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
experiements_paths.append(experiements_path)

budgetlines.append(alllines)


experiements_path = os.getcwd()+'/experiments/find_all/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
experiements_paths.append(experiements_path)

budgetlines.append(alllines)


folders = ['data','data_smac']
algos = ['shortcut','stacked','bugdoc','dataxray','dataxray_data_smac','explanation','explanation_data_smac']
labels = ['Shortcut','Stacked Shortcut','Debugging Decision Trees','Data X-Ray (BugDoc)','Data X-Ray (SMAC)','Explanation Tables (BugDoc)','Explanation Tables (SMAC)']
iterations = ['Shortcut budget','Stacked budget','Decision Trees budget']

#Figure 3a, 3b, 3c
filtered_lines = [[experiment for experiment in alllines if int(experiment.split('_')[-2]) > 1 and int(experiment.split('_')[-1][:-1]) >= 1]for alllines in budgetlines]
plot_budget_complete_general(experiements_paths, filtered_lines, 'Figure 3',algos,labels,folders,iterations, findAll=True)

# ===================================== Answer size ==========================================================

experiements_path = os.getcwd()+'/experiments/find_all/data/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()

folders = ['data','data_smac']
algos = ['shortcut','stacked','bugdoc','dataxray','dataxray_data_smac','explanation','explanation_data_smac']
labels = ['Shortcut','Stacked Shortcut','Debugging Decision Trees','Data X-Ray (BugDoc)','Data X-Ray (SMAC)','Explanation Tables (BugDoc)','Explanation Tables (SMAC)']

#Figure 4a, 4b
plot_answer_sizes(experiements_path,alllines, 'Figure 4',algos,labels,folders)



# ===================================== Count Intances ==========================================================
plt.clf()
experiements_path = os.getcwd() + '/experiments/count_instances/data_shortcut'
experiments_list_path = experiements_path + '/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()
totals_shortcut = []
totals_trees = []
totals_trees_stacked = []
totals_shortcut_tmp = []
totals_trees_tmp = []
totals_trees_stacked_tmp = []
index_param = 0
for experiment in alllines:
    experiment_name = os.path.join(experiements_path, experiment[:-1])
    index_param += 1
    f = open(experiment_name + '_shortcut_%d.res' % (sys.maxsize), 'r')
    list_result = json.loads(f.read())
    f.close()

    totals_shortcut_tmp.append(list_result["total"])

    f = open(experiment_name + '_stacked_%d.res' % (sys.maxsize), 'r')
    list_result = json.loads(f.read())
    f.close()

    totals_trees_stacked_tmp.append(list_result["total"])

    f = open(experiment_name.replace('data_shortcut', 'data_trees') + '_trees_%d.res' % (sys.maxsize), 'r')
    tree_outputs = f.readlines()
    f.close()

    totals_trees_tmp.append(int(tree_outputs[3]))

    if index_param == 3:
        totals_shortcut.append(np.mean(totals_shortcut_tmp))
        totals_trees.append(np.mean(totals_trees_tmp))
        totals_trees_stacked.append(np.mean(totals_trees_stacked_tmp))
        index_param = 0
        totals_shortcut_tmp = []
        totals_trees_tmp = []
        totals_trees_stacked_tmp = []

horizontal = [c for c in range(3,20) for b in range(5,6)]
plt.plot(horizontal, totals_shortcut, color='#1f77b4',linestyle='-', label='Shortcut')
plt.plot(horizontal, totals_trees_stacked, color='#ff7f0e',linestyle='--', label='Stacked Shorcut')
plt.plot(horizontal, totals_trees, color='#2ca02c',linestyle='-.', label='Debugging Decision Trees')
plt.xlabel('Number of Parameters')
plt.ylabel('Number of Instances')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1),
               fancybox=True, ncol=3)

plt.savefig("Figure 5")
plt.clf()
# ===================================== Parallel ==========================================================
#Figure 5
plot_parallel(os.getcwd()+'/experiments/parallel_evaluation/data/evaluation.json', 'Figure 6')
plt.clf()

# ===================================== Real-World ==========================================================
#Figure 5
plot_first_real([os.getcwd()+'/experiments/world/data/world\n'], 'Figure 7')