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

from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
from six import string_types
import ast
import copy
import queue
import logging
import time
import zmq

import bugdoc.utils.tree as tree
from bugdoc.utils.utils import load_runs, compute_score, goodbad, numtests, load_combinatorial, load_permutations

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class AutoDebug(object):

    def determinenodepurity(self, node, path):
        if node.results is None:
            pathfalse = copy.deepcopy(path)
            pathfalse.append((node.col, node.value, False))
            path.append((node.col, node.value, True))
            self.determinenodepurity(node.fb, pathfalse)
            self.determinenodepurity(node.tb, path)
        elif (len(node.results.items()) > 1):
            self.mixedlist.append(path)
        elif (node.results.items()[0][0]):
            self.puregoodlist.append(path)
        else:
            self.purebadlist.append(path)

    def findshoertestpaths(self, node):
        q = queue.Queue()
        q.put((node, []))
        puregoodpath = None
        purebadpath = None
        while (not q.empty()) and ((puregoodpath is None) or (purebadpath is None)):
            current = q.get()
            if current[0].results is None:
                q.put((current[0].fb, current[1] + [(current[0].col, current[0].value, False)]))
                q.put((current[0].tb, current[1] + [(current[0].col, current[0].value, True)]))
            elif (len(list(current[0].results.items())) > 1):
                continue
            elif (list(current[0].results.items())[0][0]) and (puregoodpath is None):
                puregoodpath = current[1]
            elif (not list(current[0].results.items())[0][0]) and (purebadpath is None):
                purebadpath = current[1]
        return [puregoodpath, purebadpath]

    def findallpaths(self, node):
        q = queue.Queue()
        q.put((node, []))
        puregoodpaths = []
        purebadpaths = []

        while (not q.empty()):
            current = q.get()
            if current[0].results is None:
                key = current[0].col
                value = current[0].value
                q.put((current[0].fb, current[1] + [(key, value, False)]))
                q.put((current[0].tb, current[1] + [(key, value, True)]))
            elif (len(list(current[0].results.items())) > 1):
                continue
            elif (list(current[0].results.items())[0][0]):
                puregoodpaths.append(current[1])
            elif (not list(current[0].results.items())[0][0]):
                purebadpaths.append(current[1])
        return [puregoodpaths, purebadpaths]

    def manufacturetests(self, moralflag, alist):
        rebuild = False
        logging.debug("a list: " + str(alist))
        if (moralflag == 'bad'):
            for path in alist:
                logging.debug("at step 2.5, path: " + str(path))
                z = self.assembletests('bad', path)
                if z:
                    logging.debug("believeddecisive for bad: " + str(path))
                    self.believeddecisive.append(('bad', path))
                else:
                    rebuild = True

        if (moralflag == 'good'):
            for path in alist:
                logging.debug("at step 3.5, path: " + str(path))
                z = self.assembletests('good', path)
                if z:
                    logging.debug("believeddecisive for good: " + str(path))
                    self.believeddecisive.append(('good', path))
                else:
                    rebuild = True
        return rebuild

    def assembletests(self, moralflag, path):
        outlist = []
        myarrtrans = list(zip(*self.allexperiments))

        input_dict = {}
        for j in range(len(self.cols) - 1):
            y = set(myarrtrans[j])
            for index, value, flag in [tup for tup in path if tup[0] == j]:
                if flag:
                    if isinstance(value, string_types):
                        y = {value}
                    else:
                        y = {element for element in y if element >= value}
                else:
                    if isinstance(value, string_types):
                        y = y - {value}
                    else:
                        y = {element for element in y if element < value}
            outlist.append(list(y))
            input_dict[self.my_inputs[j]] = y

        costs = []
        experiments = []
        isempty = False

        for key in input_dict:
            if len(input_dict[key]) == 0:
                isempty = True
        if not isempty:
            if self.use_score:
                permutations = load_permutations(input_dict)
            else:
                permutations = load_combinatorial(input_dict)
            for d in permutations:
                x = []
                for param in self.my_inputs:
                    value = d[param]
                    x.append(value)
                if (x not in self.expers):
                    experiments.append(x)
                    costs.append(compute_score(x, self.my_inputs, self.pv_goodness, moralflag))
                else:
                    logging.debug("Skipping: " + str(x))
        logging.debug("Number of experiments: " + str(len(experiments)))
        # Executing experiments in ascending order of costs
        allrets = []
        indices = [t[0] for t in sorted(enumerate(costs), key=lambda x: x[1])]
        if len(indices) > self.k: indices = indices[:self.k]
        requests = set()
        for i in indices:
            if (len(self.allexperiments) + len(requests)) < self.max_iter:
                e = experiments[i]
                self.workflow(e)
                if self.is_poller_not_sync:
                    time.sleep(1)
                    self.is_poller_not_sync = False
                requests.add(str(e))

        while len(requests) > 0:
            if len(requests) > self.max_instances:
                self.max_instances = len(requests)
            socks = dict(self.poller.poll(1000))
            if socks:
                if socks.get(self.receiver) == zmq.POLLIN:
                    msg = self.receiver.recv_string(zmq.NOBLOCK)
                    exp = ast.literal_eval(msg)
                    self.allexperiments.append(exp)
                    result_value = exp[-1]
                    for i in range(len(self.my_inputs)):
                        key = self.my_inputs[i]
                        v = exp[i]
                        if key not in self.pv_goodness:
                            self.pv_goodness[key] = {}
                        if v not in self.pv_goodness[key]:
                            self.pv_goodness[key][v] = {'good': 0, 'bad': 0}
                        if eval(result_value):
                            self.pv_goodness[key][v]['good'] += 1
                        else:
                            self.pv_goodness[key][v]['bad'] += 1
                    requests.discard(str(exp[:-1]))
                    x = copy.deepcopy(exp)
                    x[-1] = eval(x[-1])
                    result = x[-1]
                    # We could run the experiment
                    if result is not None:
                        self.allresults.append(x)
                        self.expers.append(x[:-1])
                        self.rets.append(x[-1])
                        allrets.append(x[-1])

            else:
                for tup in requests:
                    exp = list(tup)
                    # self.workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

        if (1 == len(set(allrets))):
            if ((moralflag == 'good') and (not allrets[0])) or ((moralflag == 'bad') and allrets[0]):
                return False
            else:
                return True
        elif (0 == len(set(allrets))):
            return True
        else:
            return False

    def run(self, filename, input_dict, outputs, rebuild=True):
        self.my_inputs = list(input_dict.keys())
        self.my_outputs = outputs
        self.filename = filename
        self.allexperiments, self.allresults, self.pv_goodness = load_runs(filename.replace(".vt", ".adb"),
                                                                           self.my_inputs)
        logging.debug("pv_goodness is: " + str(self.pv_goodness))
        logging.debug("allresults is: " + str(self.allresults))
        requests = set()
        self.expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        self.rets = [self.allresults[j][-1] for j in range(len(self.allresults))]
        permutations = load_combinatorial(input_dict)
        for d in permutations:
            exp = []
            for param in self.my_inputs:
                value = d[param]
                exp.append(value)
            if ([p for p in exp] not in self.expers):
                if (len(self.allexperiments) + len(requests)) < self.max_iter:
                    self.workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False
                    requests.add(str(exp))

        while len(requests) > 0:
            if len(requests) > self.max_instances:
                self.max_instances = len(requests)
            socks = dict(self.poller.poll(10000))
            if socks:
                if socks.get(self.receiver) == zmq.POLLIN:
                    msg = self.receiver.recv_string(zmq.NOBLOCK)
                    exp = ast.literal_eval(msg)
                    self.allexperiments.append(exp)
                    result_value = exp[-1]
                    for i in range(len(self.my_inputs)):
                        key = self.my_inputs[i]
                        v = exp[i]
                        if key not in self.pv_goodness:
                            self.pv_goodness[key] = {}
                        if v not in self.pv_goodness[key]:
                            self.pv_goodness[key][v] = {'good': 0, 'bad': 0}
                        if eval(result_value):
                            self.pv_goodness[key][v]['good'] += 1
                        else:
                            self.pv_goodness[key][v]['bad'] += 1

                    requests.discard(str(exp[:-1]))
                    x = copy.deepcopy(exp)
                    x[-1] = eval(x[-1])
                    result = x[-1]
                    # We could run the experiment
                    if result is not None:
                        self.allresults.append(x)
            else:
                for tup in requests:
                    exp = list(tup)
                    # self.workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

        self.expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        self.rets = [self.allresults[j][-1] for j in range(len(self.allresults))]
        self.cols = self.my_inputs + self.my_outputs
        iter = 0
        initial_experiments_num = len(self.allexperiments)
        while rebuild:
            self.cohort += 1
            rebuild = len(self.allexperiments) < self.max_iter and len(self.allexperiments) > iter
            iter = len(self.allexperiments)
            logging.debug("rebuild")
            logging.debug("allresults is: " + str(self.allresults))
            logging.debug("allexperiments are: " + str(self.allexperiments))
            t = tree.build(self.allresults, cols=self.cols)
            # tree.draw_tree(t)
            if self.window:
                self.window.updateTree()
            if self.first_solution:
                goodpath, badpath = self.findshoertestpaths(t)
                if badpath:
                    rebuild = rebuild and self.manufacturetests('bad', [badpath])
            else:
                goodpaths, badpaths = self.findallpaths(t)
                rebuild = rebuild and self.manufacturetests('bad', badpaths)

        self.puregoodlist = []
        self.purebadlist = []
        self.mixedlist = []
        t = tree.build(self.allresults, cols=self.cols)
        # tree.draw_tree(t)
        if self.window:
            self.window.updateTree()
        logging.debug("length of all experiments is: " + str(len(self.allexperiments)))
        # logging.debug("The current goodness count is: " + str(self.pv_goodness))
        self.poller.unregister(self.receiver)
        self.receiver.close()
        self.sender.close()
        self.context.term()
        if self.return_max_instances:
            return self.believeddecisive, t, len(self.allexperiments), self.max_instances
        if self.created_instances:
            return (len(self.allexperiments) - initial_experiments_num)
        return self.believeddecisive, t, len(self.allexperiments)

    def workflow(self, parameter_list):
        message = self.filename
        message += self.separator + str(parameter_list)
        message += self.separator + str(list(self.my_inputs))
        message += self.separator + str(self.my_outputs)
        if self.origin:
            message += self.separator + str(self.origin) + "_trees_" + str(self.cohort)
        self.sender.send_string(message)

    def __init__(self, created_instances=False, first_solution=False, max_iter=10000, return_max_instances=False,
                 k=10000, use_score=False, window=None, origin=None, separator="|"):
        self.created_instances = created_instances
        self.filename = None
        self.puregoodlist = []
        self.purebadlist = []
        self.mixedlist = []
        self.allexperiments = []
        self.allresults = []
        self.cost = '1'
        self.cols = []
        self.believeddecisive = []
        self.expers = []
        self.myalllists = []
        self.rets = []
        self.my_inputs = []
        self.my_outputs = []
        self.pv_goodness = {}
        self.context = zmq.Context()
        self.first_solution = first_solution
        self.max_iter = max_iter
        self.return_max_instances = return_max_instances
        self.max_instances = 0
        self.k = k
        self.use_score = use_score
        self.window = window

        # Socket to send messages on
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:5557")

        # Socket with direct access to the sink: used to syncronize start of batch
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:5558")

        self.poller = zmq.Poller()
        self.poller.register(self.receiver, zmq.POLLIN)
        self.is_poller_not_sync = True
        self.origin = origin
        self.cohort = 0
        self.separator = separator