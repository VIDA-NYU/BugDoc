###############################################################################
##
## Copyright (C) 2020-2022, New York University.
## All rights reserved.
## Contact: raoni@nyu.edu
##
## This file is part of BugDoc.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

#Following blog post at: http://kldavenport.com/pure-python-decision-trees/

from __future__ import division
from __future__ import print_function

from builtins import str
from builtins import range
from builtins import object
import collections
from PIL import Image, ImageDraw


def unique_counts(rows):
    """
    :param rows:
    :return:
    """
    results = {}
    for row in rows:
        # The result is the last column
        r = row[len(row) - 1]
        if r not in results: results[r] = 0
        results[r] += 1
    return results


def unique_counts_dd(rows):
    """
    :param rows:
    :return:
    """
    results = collections.defaultdict(lambda: 0)
    for row in rows:
        r = row[len(row) - 1]
        results[r] += 1
    return dict(results)


# Entropy is the sum of p(x)log(p(x)) across all the different possible results

def entropy(rows):
    """
    :param rows:
    :return:
    """
    from math import log
    log2 = lambda x: log(x) // log(2)
    results = unique_counts(rows)

    # Now calculate the entropy
    ent = 0.0
    for r in list(results.keys()):
        # current probability of class
        p = float(results[r]) / len(rows)
        ent -= p * log2(p)
    return ent


class DecisionNode(object):
    """
    """
    def __init__(self, col=-1, cols=[], value=None, best_gain=None, results=None, tb=None, fb=None, parent=None):
        self.col = col  # column index of criteria being tested
        self.best_gain = best_gain
        self.col_str = cols[col] if len(cols) > 0 else '<col>'  # column factor str
        self.value = value  # value necessary to get a true result
        self.results = results  # dict_ of results for a branch, None for everything except endpoints
        self.tb = tb  # true decision nodes
        self.fb = fb  # false decision nodes
        self.parent = parent


class Stats(object):
    """
    """
    leaf_nodes = 0
    pure_nodes = 0

    def __init__(self, tree):
        self.leaf_nodes = self.count_leaf(tree)

    def count_leaf(self, tree):
        """
        :param tree:
        :return:
        """
        if not tree:
            return 0
        if not tree.fb and not tree.tb:
            if len(list(tree.results.keys())) == 1:
                self.pure_nodes += 1
            return 1
        else:
            return self.count_leaf(tree.fb) + self.count_leaf(tree.tb)


def __init__(self, t_set, cols):
    self.t_set = t_set
    self.cols = cols


# Divides a set on a specific column. Can handle numeric or nominal values
def divide_set(rows, column, value):
    """
    :param rows:
    :param column:
    :param value:
    :return:
    """
    # for numerical values
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value

    # for nominal values
    else:
        split_function = lambda row: row[column] == value

        # Divide the rows into two sets and return them
    set1 = [row for row in rows if split_function(row)]  # if split_function(row)
    set2 = [row for row in rows if not split_function(row)]
    return set1, set2


# **Caveats:**
# Information gain is generally a good measure for deciding the relevance of an attribute,
# but there are some distinct shortcomings. One case is when information gain is applied to
# variabless that take on a large number of unique values. This is a concern not necessarily
# from a pure variance perspective, rather that the variable is too descriptive of the current observations.
#
# **High mutual information** indicates a large reduction in uncertainty,
# credit card numbers or street addresss variables in a dataset uniquely identify a customer.
# These variables provide a great deal of identifying information if we are trying to predict a customer, but will not
# generalize well to unobserved/trained-on instances (overfitting).


def build(rows, score_fun=entropy, cols=None, parent=None):
    """
    :param rows:
    :param score_fun:
    :param cols:
    :param parent:
    :return:
    """
    if len(rows) == 0:
        return DecisionNode()

    current_score = score_fun(rows)

    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1  # last column is result
    for col in range(0, column_count):
        # find different values in this column
        column_values = set([row[col] for row in rows])

        # for each possible value, try to divide on that value
        for value in column_values:
            set1, set2 = divide_set(rows, col, value)

            # Information gain
            p = float(len(set1)) / len(rows)
            gain = current_score - p * score_fun(set1) - (1 - p) * score_fun(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    if best_gain > 0:
        true_branch = build(best_sets[0], cols=cols)
        false_branch = build(best_sets[1], cols=cols)
        return DecisionNode(col=best_criteria[0], value=best_criteria[1], cols=cols,
                            best_gain=best_gain, tb=true_branch, fb=false_branch)
    else:
        return DecisionNode(results=unique_counts(rows))


# We now have a function that returns a trained decision tree. We can print a rudimentary tree.

def print_tree(tree, indent=''):
    """
    :param tree:
    :param indent:
    :return:
    """
    # Is this a leaf node?
    if tree.results is not None:
        print(str(tree.results))
    else:
        # Print the criteria
        print('Column ' + str(tree.col_str) + ' : ' + str(tree.value) + '? ')

        # Print the branches
        print(indent + 'True->', end=' ')
        print_tree(tree.tb, indent + '  ')
        print(indent + 'False->', end=' ')
        print_tree(tree.fb, indent + '  ')


# printing stuff
def get_width(tree):
    """
    :param tree:
    :return:
    """
    if tree.tb is None and tree.fb is None:
        return 1
    return get_width(tree.tb) + get_width(tree.fb)


def get_depth(tree):
    """
    :param tree:
    :return:
    """
    if tree.tb is None and tree.fb is None:
        return 0
    return max(get_depth(tree.tb), get_depth(tree.fb)) + 1


def draw_tree(tree, jpeg='tree.jpg'):
    """
    :param tree:
    :param jpeg:
    :return:
    """
    w = get_width(tree) * 100
    h = get_depth(tree) * 100 + 120

    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw_node(draw, tree, w // 2, 20)
    img.save(jpeg, 'JPEG')
    # img.show()
    # IPython.display.display(IPython.display.Image(filename=jpeg))


def draw_node(draw, tree, x, y):
    """
    :param draw:
    :param tree:
    :param x:
    :param y:
    :return:
    """
    if tree.results is None:
        # Get the width of each branch
        w1 = get_width(tree.fb) * 100
        w2 = get_width(tree.tb) * 100

        # Determine the total space required by this node
        left = x - (w1 + w2) // 2
        right = x + (w1 + w2) // 2

        # Draw the condition string
        draw.text((x - 20, y - 10),
                  str(tree.col_str) + ':' + str(tree.value) + ' (' + str(round(tree.best_gain, 2)) + ')',
                  (0, 0, 0))

        # Draw links to the branches
        draw.line((x, y, left + w1 // 2, y + 100), fill=(255, 0, 0))
        draw.line((x, y, right - w2 // 2, y + 100), fill=(255, 0, 0))

        # Draw the branch nodes
        draw_node(draw, tree.fb, left + w1 // 2, y + 100)
        draw_node(draw, tree.tb, right - w2 // 2, y + 100)
    else:
        txt = ' \n'.join(['%s:%d' % v for v in list(tree.results.items())])
        draw.text((x - 20, y), txt, (0, 0, 0))


# Now that we have built our tree, we can feed new observations and classify them.
# The following code basically do what we could do manually by using the tree and answering the questions.

def classify(observation, tree):
    """
    :param observation:
    :param tree:
    :return:
    """
    if tree.results is not None:
        return tree.results
    else:
        v = observation[tree.col]
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if v == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        return classify(observation, branch)


def precision(df, tree, n=100):
    """
    :param df:
    :param tree:
    :param n:
    :return:
    """
    import pyprind
    bar = pyprind.ProgBar(n, track_time=True, stream=1)
    p = 0
    for i in range(n):
        obs = df.sample(n=1).values[0]
        t = obs[-1]
        obs = obs[:-1]
        clf = classify(obs, tree)
        if t in clf: p += 1
        bar.update()
    return float(p) / float(n)


