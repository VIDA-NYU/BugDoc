import os
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties
import numpy as np


fig, ax = plt.subplots()
bar_width = 0.1

algos = ["BugDoc", "BugDoc SI"]

counts = {"BugDoc": {}, "BugDoc SI": {}}
permutations = set()


experiements_path = os.getcwd()+'/experiments/selective_evaluation_ineq_dis_parameters/data_trees/'
experiments_list_path = experiements_path+'/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()

filtered = alllines#[experiment for experiment in alllines if int(experiment.split('_')[-2]) == 1 and int(experiment.split('_')[-1][:-1]) == 1]
for experiment in filtered:
    _, p, v, i, _, _ = experiment.split('_')
    p = int(v) ** int(p)
    if p not in permutations:
        permutations.add(p)
        counts["BugDoc"][p] = []
        counts["BugDoc SI"][p] = []
    experiment_name = os.path.join(experiements_path, experiment[:-1])
    f = open(experiment_name + '.adb', 'r')
    experiment_lines = f.readlines()
    f.close()

    counts["BugDoc"][p].append(len(experiment_lines))

    experiment_name = os.path.join(experiements_path.replace("trees","selective"), experiment[:-1])
    f = open(experiment_name + '.adb', 'r')
    experiment_lines = f.readlines()
    f.close()

    counts["BugDoc SI"][p].append(len(experiment_lines))

algo_index = 0
index = np.arange(len(permutations))
sorted_p = sorted(permutations)
metrics = tuple(sorted_p)
colors = ['#1f77b4', '#ff7f0e']
hatchs = ['', '\\']

for algo in algos:
    ax.bar(index + (algo_index * bar_width), [np.mean(counts[algo][p]) for p in sorted_p],
           bar_width,
           edgecolor='black',
           color=colors[algo_index % len(colors)],
           label=algos[algo_index],
           hatch=hatchs[algo_index % len(hatchs)])
    algo_index += 1
ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
ax.set_xticklabels(metrics)
plt.ylim([0.0, 10**3])
#plt.yscale('log')
#plt.xscale('log')
plt.ylabel('# Instances')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1),
               fancybox=True, ncol=2)
fig.tight_layout()
fig.savefig("selective_ineq_dis_parameters")
print(permutations)