import os
import json
import sys
import ast
sys.path.append(os.path.join(os.getcwd(), '..'))
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

fontP = FontProperties()
fontP.set_size('small')


def plot_answer_sizes(experiements_path, alllines,name_fig,algos,labels, folders, suffix=['a', 'b']):
    solution = {}
    for experiment in alllines:
        experiment_name = os.path.join(experiements_path,experiment[:-1] + '_%d' % (sys.maxsize))
        f = open(experiment_name + '.answers', 'r')
        experiment_lines = f.readlines()
        f.close()
        for line in experiment_lines:
            result_dict = json.loads(line[:-1])
            if result_dict['answers_per_root'] == 0.0: continue

            if result_dict['algo'] == 'workflowdoc':  # Workaround data legacy
                result_dict['algo'] = 'bugdoc'

            if result_dict['algo'] not in solution:
                solution[result_dict['algo']] = {'avg_size':result_dict['avg_size'] ,
                                                 'answers_per_root': result_dict['answers_per_root'],
                                                 'count': 1}
            else:
                solution[result_dict['algo']]['answers_per_root'] += result_dict['answers_per_root']
                solution[result_dict['algo']]['avg_size'] += result_dict['avg_size']
                solution[result_dict['algo']]['count'] += 1

        for folder in folders[1:]:
            f = open(experiment_name.replace(folders[0], folder) + '.answers', 'r')
            experiment_lines = f.readlines()
            f.close()
            for line in experiment_lines:
                result_dict = json.loads(line[:-1])
                if result_dict['answers_per_root'] == 0.0: continue
                algo_folder = result_dict['algo'] + '_' + folder
                if algo_folder not in solution:
                    solution[algo_folder] = {
                        'avg_size': result_dict['avg_size'],
                        'answers_per_root': result_dict['answers_per_root'],
                        'count': 1}
                else:
                    solution[algo_folder]['answers_per_root'] += result_dict['answers_per_root']
                    solution[algo_folder]['avg_size'] += result_dict['avg_size']
                    solution[algo_folder]['count'] += 1

    fig, ax = plt.subplots()
    bar_width = 0.05
    index = np.arange(1)
    metrics = tuple(['Algorithms'])
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    hatchs = ['', '\\', '//', 'x', '-', 'xx', '+']
    algo_index = 0

    for algo in algos:
        ax.bar(index + (algo_index * bar_width), [0.0 if algo not in solution else solution[algo]['avg_size']/solution[algo]['count']], bar_width, edgecolor='black',
               color=colors[algo_index % len(colors)], label=labels[algo_index], hatch=hatchs[algo_index % len(hatchs)])
        algo_index += 1

    ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
    ax.set_xticklabels(metrics)
    plt.ylabel('# of parameters per explanation')
    fig.savefig(name_fig+suffix[0])

    fig, ax = plt.subplots()
    algo_index = 0

    for algo in algos:
        ax.bar(index + (algo_index * bar_width), [0.0 if algo not in solution else np.log1p(solution[algo]['answers_per_root'] / solution[algo]['count'])], bar_width,
               edgecolor='black',
               color=colors[algo_index % len(colors)], label=labels[algo_index], hatch=hatchs[algo_index % len(hatchs)])
        algo_index += 1

    ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
    ax.set_xticklabels(metrics)
    plt.ylabel('# of explanations per root cause')
    fig.savefig(name_fig+suffix[1])


def plot_budget_complete_general(experiements_paths, budgetlines,name_fig,algos,labels,folders,iterations,
                                 suffix=['a', 'b', 'c'],findAll=True):
    solutions = []
    budget_index = 0
    for alllines in budgetlines:
        solution = {}
        experiements_path = experiements_paths[budget_index]
        budget_index += 1
        for experiment in alllines:
            experiment_name = os.path.join(experiements_path,experiment[:-1] + '_%d' % (sys.maxsize))
            f = open(experiment_name + '.agg', 'r')
            experiment_lines = f.readlines()
            f.close()
            for line in experiment_lines:
                result_dict = json.loads(line[:-1])
                if result_dict['algo'] == 'workflowdoc': # Workaround data legacy
                    result_dict['algo'] = 'bugdoc'
                if result_dict['algo'] not in solution:
                    solution[result_dict['algo']] = {'fp': result_dict['fp'],
                                                     'fn': result_dict['fn'],
                                                     'tp': result_dict['tp'],
                                                     'found': 1 if result_dict['tp'] > 0 else 0,
                                                     'failed': 1 if result_dict['fp'] > 0 else 0,
                                                     'minimal': 1 if result_dict['minimal'] else 0,
                                                     'count': 1}
                else:
                    solution[result_dict['algo']]['fp'] += result_dict['fp']
                    solution[result_dict['algo']]['tp'] += result_dict['tp']
                    solution[result_dict['algo']]['fn'] += result_dict['fn']
                    solution[result_dict['algo']]['count'] += 1
                    if result_dict['tp'] > 0:
                        solution[result_dict['algo']]['found'] += 1
                    if result_dict['fp'] > 0:
                        solution[result_dict['algo']]['failed'] += 1
                    if result_dict['minimal']:
                        solution[result_dict['algo']]['minimal'] += 1
            for folder in folders[1:]:
                f = open(experiment_name.replace(folders[0], folder) + '.agg', 'r')
                experiment_lines = f.readlines()
                f.close()
                for line in experiment_lines:
                    result_dict = json.loads(line[:-1])
                    algo_folder = result_dict['algo'] +'_'+ folder
                    if algo_folder not in solution:
                        solution[algo_folder] = {'fp': result_dict['fp'],
                                               'fn': result_dict['fn'],
                                               'tp': result_dict['tp'],
                                               'found': 1 if result_dict['tp'] > 0 else 0,
                                               'failed': 1 if result_dict['fp'] > 0 else 0,
                                               'minimal': 1 if result_dict['minimal'] else 0,
                                               'count': 1}
                    else:
                        solution[algo_folder]['fp'] += result_dict['fp']
                        solution[algo_folder]['tp'] += result_dict['tp']
                        solution[algo_folder]['fn'] += result_dict['fn']
                        solution[algo_folder]['count'] += 1
                        if result_dict['tp'] > 0:
                            solution[algo_folder]['found'] += 1
                        if result_dict['fp'] > 0:
                            solution[algo_folder]['failed'] += 1
                        if result_dict['minimal']:
                            solution[algo_folder]['minimal'] += 1
        solutions.append(solution)
    precisions = {}
    recalls = {}
    scores = {}
    counts = {}
    fails = {}
    minimals = {}
    tps = {}
    fps = {}
    for solution in solutions:
        for algo in algos:
            if algo not in precisions:
                precisions[algo] = []
                recalls[algo] = []
                scores[algo] = []
                counts[algo] = []
                fails[algo] = []
                minimals[algo] = []
                tps[algo] = []
                fps[algo] = []

            if findAll:
                precision = 0.0 if (solution[algo]['tp'] + solution[algo]['fp']) == 0 else float(
                    solution[algo]['tp']) / float(solution[algo]['tp'] + solution[algo]['fp'])
                recall = 0.0 if (solution[algo]['tp'] + solution[algo]['fn']) == 0 else float(
                    solution[algo]['tp']) / float(
                    solution[algo]['tp'] + solution[algo]['fn'])
            else:
                print(algo, solution[algo])
                precision = 0.0 if (solution[algo]['found'] + solution[algo]['fp']) == 0 else float(
                    solution[algo]['found']) / float(solution[algo]['found'] + solution[algo]['fp'])
                recall = float(solution[algo]['found']) / float(solution[algo]['count'])
            fail = float(solution[algo]['failed']) / float(solution[algo]['count'])
            minimal = float(solution[algo]['minimal']) / float(solution[algo]['count'])
            score = 0 if ((precision + recall) == 0) else 2.0 * ((precision * recall) / (precision + recall))
            precisions[algo].append(precision)
            recalls[algo].append(recall)
            fails[algo].append(fail)
            minimals[algo].append(minimal)
            scores[algo].append(score)
            counts[algo].append(solution[algo]['count'])
            tps[algo].append(solution[algo]['tp'])
            fps[algo].append(solution[algo]['fp'])

    fig, ax = plt.subplots()
    bar_width = 0.1

    index = np.arange(3)
    metrics = tuple(iterations)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    hatchs = ['', '\\', '//', 'x', '-', 'xx','+']

    algo_index = 0
    print(precisions)
    for algo in algos:
        ax.bar(index + (algo_index * bar_width), precisions[algo],
               bar_width,
               edgecolor='black',
               color=colors[algo_index % len(colors)],
               label=labels[algo_index],
               hatch=hatchs[algo_index % len(hatchs)])
        algo_index += 1
    ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
    ax.set_xticklabels(metrics)
    plt.ylim([0.0, 1.1])
    plt.ylabel('Precision')
    fig.tight_layout()
    fig.savefig(name_fig+suffix[0])

    fig, ax = plt.subplots()
    algo_index = 0
    for algo in algos:
        ax.bar(index + (algo_index * bar_width), recalls[algo], bar_width, edgecolor='black',
               color=colors[algo_index % len(colors)], label=labels[algo_index], hatch=hatchs[algo_index % len(hatchs)])
        algo_index += 1
    ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
    ax.set_xticklabels(metrics)
    plt.ylim([0.0, 1.1])
    plt.ylabel('Recall')
    fig.tight_layout()
    fig.savefig(name_fig+suffix[1])

    fig, ax = plt.subplots()

    algo_index = 0
    for algo in algos:
        ax.bar(index + (algo_index * bar_width), scores[algo], bar_width, edgecolor='black',
               color=colors[algo_index % len(colors)], label=labels[algo_index], hatch=hatchs[algo_index % len(hatchs)])
        algo_index += 1
    ax.set_xticks(index + (len(algos) * bar_width) / 2.0)
    ax.set_xticklabels(metrics)
    plt.ylim([0.0, 1.1])
    plt.ylabel('F-measure')
    fig.tight_layout()
    fig.savefig(name_fig+suffix[2])


def plot_parallel(evaluation_file, name_fig):
    f = open(evaluation_file,'r')
    parallel_evaluation = f.read()
    f.close()
    parallel_evaluation = json.loads(parallel_evaluation)
    instances_per_core = []
    totals = []
    horizontal = []
    for core in ['1', '2', '5', '10', '20', '30', '40', '50']:
        int_core = int(core)
        horizontal.append(int_core)
        instances_per_core.append((parallel_evaluation[core]["max_instances"] / float(int_core)))
        totals.append(parallel_evaluation[core]["total"])

    plt.plot(horizontal, instances_per_core, 'go-', label='Max Instances per core')
    plt.plot(horizontal, totals, 'y^-', label='Total Instances')
    plt.xlabel('Number of Cores')
    plt.ylabel('Number of Instances')
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1),
               fancybox=True, ncol=3)

    plt.savefig(name_fig)


def plot_first_real(alllines, name_fig):
    solution = {}
    for experiment in alllines:
        experiment_name = experiment[:-1].replace('/Users/raonilourenco/reps/debugging-science/study',
                                                  os.getcwd()) + '_%d' % (sys.maxsize)
        f = open(experiment_name + '.agg', 'r')
        experiment_lines = f.readlines()
        f.close()
        for line in experiment_lines:
            result_dict = json.loads(line[:-1])
            if result_dict['algo'] not in solution:
                solution[result_dict['algo']] = {'fp': result_dict['fp'],
                                                 'fn': result_dict['fn'],
                                                 'tp': result_dict['tp'],
                                                 'found': 1 if result_dict['tp'] > 0 else 0,
                                                 'count': 1}
                '''
                if result_dict['algo'] == 'explanation':
                    solution[result_dict['algo']] = {'fp': 0,
                                                     'fn': 0,
                                                     'tp': 0,
                                                     'found': 1 if result_dict['tp'] > 0 else 0,
                                                     'count': 0}
                '''
            else:
                solution[result_dict['algo']]['fp'] += result_dict['fp']
                solution[result_dict['algo']]['tp'] += result_dict['tp']
                solution[result_dict['algo']]['fn'] += result_dict['fn']
                solution[result_dict['algo']]['count'] += 1
                if result_dict['tp'] > 0:
                    solution[result_dict['algo']]['found'] += 1
    fig, ax = plt.subplots()
    bar_width = 0.2
    scores = []
    precisions = []
    recalls = []
    for algo in [u'bugdoc', u'dataxray', u'explanation']:
        precision = 0.0 if (solution[algo]['tp'] + solution[algo]['fp']) == 0 else float(solution[algo]['tp']) / float(
            solution[algo]['tp'] + solution[algo]['fp'])
        precisions.append(precision)
        recall = float(solution[algo]['tp']) / float(
                    solution[algo]['tp'] + solution[algo]['fn'])
        recalls.append(recall)
        score = 0 if ((precision + recall) == 0.0) else 2.0 * ((precision * recall) / (precision + recall))
        scores.append(score)

    index = np.arange(3)
    metrics = tuple(['Precision', 'Recall', 'F-Measure'])
    scores = tuple(scores)

    ax.bar(index, [precisions[0], recalls[0], scores[0]], bar_width, edgecolor='black',
           color='g', label='BugDoc')
    ax.bar(index + (bar_width), [precisions[1], recalls[1], scores[1]], bar_width, edgecolor='black',
           color='white', label='Data X-Ray', hatch='\\')
    ax.bar(index + (2.0 * bar_width), [precisions[2], recalls[2], scores[2]], bar_width, edgecolor='black',
           color='pink', label='Explanation Tables', hatch='//')
    ax.set_xticks(index + ((2.0 * bar_width) / 2))
    ax.set_xticklabels(metrics)
    plt.ylim([0.0, 1.1])
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1),
              fancybox=True, ncol=3)
    plt.ylabel('Quality Scores')
    fig.tight_layout()
    fig.savefig(name_fig)