import os
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties
import numpy as np
import seaborn as sns
import pandas as pd

algos = ["ogt", "if", "ee"]
labels = ["Opportunistic Group Testing", "Isolation Forest", "Elliptic Envelope"]
counts = {
    "ogt": {},
    "if": {},
    "ee": {}
}
num_rows = set()

experiements_path = os.getcwd() + '/experiments/ogt_outliers/data'
experiments_list_path = experiements_path + '/list.txt'
fileicareabout = open(experiments_list_path, "r")
alllines = fileicareabout.readlines()
fileicareabout.close()

filtered = alllines  # [experiment for experiment in alllines if int(experiment.split('_')[-2]) == 1 and int(experiment.split('_')[-1][:-1]) == 1]
for experiment in filtered:
    _, _, _, r, _, _, _ = experiment.split('_')
    if r not in num_rows:
        num_rows.add(r)
        counts["ogt"][r] = {'tp': np.zeros(6), 'fp': np.zeros(6), 'fn': np.zeros(6)}
        counts["if"][r] = {'tp': np.zeros(6), 'fp': np.zeros(6), 'fn': np.zeros(6)}
        counts["ee"][r] = {'tp': np.zeros(6), 'fp': np.zeros(6), 'fn': np.zeros(6)}
    experiment_name = os.path.join(experiements_path, experiment[:-1])
    f = open(os.path.join(experiment_name, 'results.agg'), 'r')
    experiment_lines = f.readlines()
    f.close()
    for line in experiment_lines:
        result_dict = json.loads(line[:-1])
        counts[result_dict['algo']][r]['fp'] += np.array(result_dict['fp'])
        counts[result_dict['algo']][r]['tp'] += np.array(result_dict['tp'])
        counts[result_dict['algo']][r]['fn'] += np.array(result_dict['fn'])

print(counts)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
hatches = ['', '\\', '//', 'x', '-', 'xx', '+']

# precisions = []
# for algo in algos:
#     for r in ["2", "4", "8", "16", "32", "64"]:
#         for i in range(6):
#             row = {
#                     "precision": counts[algo][r]['tp'][i] / (counts[algo][r]['tp'][i] + counts[algo][r]['fp'][i]),
#                     "algo": algo,
#                     "row": r
#                 }
#             precisions.append(row)
#             print("adding row", row)
# df = pd.DataFrame(precisions)
# g = sns.catplot(x="row", y="precision", hue="algo", hue_order=["ogt", "if", "ee"], data=df,
#                 kind="box", palette=colors, legend=False,
#                 aspect=2)
#
#
# print(df)

fig, ax = plt.subplots()
bar_width = 0.1
algo_index = 0
index = np.arange(6)
metrics = tuple(["2", "4", "8", "16", "32", "64"])
precisions = {}
for algo in algos[:2]:
    precisions[algo] = [
        counts[algo][r]['tp'][2] / (counts[algo][r]['tp'][2] + counts[algo][r]['fp'][2])
        for r in metrics
    ]
    ax.bar(
        index + (algo_index * bar_width),
        precisions[algo],
        bar_width,
        edgecolor='black',
        color=colors[algo_index % len(colors)],
        label=labels[algo_index],
        hatch=hatches[algo_index % len(hatches)]
    )
    algo_index += 1
ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
ax.set_xticklabels(metrics)
plt.ylim([0.0, 1.1])

plt.ylim([0.0, 1.1])
# plt.yscale('log')
# plt.xscale('log')
plt.ylabel('Precision')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 0.92),
           fancybox=True, ncol=2)
plt.tight_layout()
plt.savefig("ogt_precision")

fig, ax = plt.subplots()
bar_width = 0.1
algo_index = 0
recalls = {}
for algo in algos[:2]:
    recalls[algo] = [
        counts[algo][r]['tp'][2] / (counts[algo][r]['tp'][2] + counts[algo][r]['fn'][2])
        for r in metrics
    ]
    ax.bar(
        index + (algo_index * bar_width),
        recalls[algo],
        bar_width,
        edgecolor='black',
        color=colors[algo_index % len(colors)],
        label=labels[algo_index],
        hatch=hatches[algo_index % len(hatches)]
    )
    algo_index += 1
ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
ax.set_xticklabels(metrics)
plt.ylim([0.0, 1.1])
# plt.yscale('log')
# plt.xscale('log')
plt.ylabel('Recall')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 0.92),
           fancybox=True, ncol=2)
fig.tight_layout()
fig.savefig("ogt_recall")

fig, ax = plt.subplots()
bar_width = 0.1
algo_index = 0
for algo in algos[:2]:
    print("recalls", recalls[algo])
    scores = [
        0 if ((precisions[algo][i] + recalls[algo][i]) == 0) else 2.0 * (
            (precisions[algo][i] * recalls[algo][i]) / (precisions[algo][i] + recalls[algo][i])
        )
        for i in range(6)
    ]
    print(scores)
    ax.bar(
        index + (algo_index * bar_width),
        scores,
        bar_width,
        edgecolor='black',
        color=colors[algo_index % len(colors)],
        label=labels[algo_index],
        hatch=hatches[algo_index % len(hatches)]
    )
    algo_index += 1
ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
ax.set_xticklabels(metrics)
plt.ylim([0.0, 1.1])
# plt.yscale('log')
# plt.xscale('log')
plt.ylabel('F-measure')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 0.92),
           fancybox=True, ncol=2)
fig.tight_layout()
fig.savefig("ogt_score")
