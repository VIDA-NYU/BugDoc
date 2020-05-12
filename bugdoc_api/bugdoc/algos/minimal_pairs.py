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

import copy
import logging
import zmq
import ast
import time
from bugdoc.utils.utils import load_runs, evaluate, goodbad, numtests, load_combinatorial, compute_score,\
                                load_permutations

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class AutoDebug(object):

    # Given a matrix myarr and a target vector mytarg,
    # determine for each column of the matrix the puregood values
    # the purebad values and the mixed ones
    # goodbad[0] is the good value and goodbad[1] is the bad value
    def determinepurity(self, myarr, mytarg):
        myarrtrans = zip(*myarr)  # transpose it
        puregoodlist = []
        purebadlist = []
        mixedlist = []
        for a in myarrtrans:
            mygood = set([a[i] for i in range(len(mytarg)) if mytarg[i] == goodbad[0]])
            mybad = set([a[i] for i in range(len(mytarg)) if mytarg[i] == goodbad[1]])
            mymixed = mygood & mybad
            mypuregood = mygood - mybad
            mypurebad = mybad - mygood
            puregoodlist.append(list(mypuregood))
            purebadlist.append(list(mypurebad))
            mixedlist.append(list(mymixed))
        return [puregoodlist, purebadlist, mixedlist]

    # Given the puregood, purebad, mixed values of each column,
    # manufacture new test cases.
    # take an index and a moralflag and determine if there is purity.
    # If the candidate index appears to be pure, then puts it into
    # believeddecisive [variableindex, moralflag, value]
    def manufacturetests(self, i, moralflag, alllists):
        global believeddecisive
        (puregoodlist, purebadlist, mixedlist) = alllists
        if (moralflag == 'bad') and (0 < len(purebadlist[i])):
            for j in range(len(purebadlist[i])):
                z = self.assembletests(i, 'bad', purebadlist[i][j], alllists)
                if self.first_solution and len(self.believeddecisive) > 0: break
            return i
        if (moralflag == 'good') and (0 < len(puregoodlist[i])):
            for j in range(len(puregoodlist[i])):
                z = self.assembletests(i, 'good', puregoodlist[i][j], alllists)
                if self.first_solution and len(self.believeddecisive) > 0: break
            return i

    # assembletests creates tests for index testindex either good or bad
    # If the test is for good, then it takes val at location testindex
    # and then it takes values from bad or mixed for all other indexes.
    # It takes at a maximum k such tests.
    def assembletests(self, testindex, moralflag, val, alllists):
        (puregoodlist, purebadlist, mixedlist) = alllists
        outlist = []
        if moralflag == 'good':
            for j in range(len(purebadlist)):
                if j == testindex:
                    outlist.append([val])
                else:
                    y = []
                    for z in purebadlist[j]:
                        y.append(z)
                    for z in mixedlist[j]:
                        y.append(z)
                    for z in puregoodlist[j]:
                        y.append(z)
                    outlist.append(y)
        if moralflag == 'bad':
            input_dict = {}
            for j in range(len(puregoodlist)):
                if j == testindex:
                    outlist.append([val])
                    input_dict[self.my_inputs[j]] = [val]
                else:
                    y = []
                    for z in puregoodlist[j]:
                        y.append(z)
                    for z in mixedlist[j]:
                        y.append(z)
                    for z in purebadlist[j]:
                        y.append(z)
                    outlist.append(y)
                    input_dict[self.my_inputs[j]] = y
        experiments = []
        costs = []
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
                self.expers.append(x)
                experiments.append(x)
                costs.append(compute_score(x, self.my_inputs, self.pv_goodness, moralflag))
        # Executing experiments in ascending order of costs
        allrets = []
        indices = [t[0] for t in sorted(enumerate(costs), key=lambda x: x[1])]
        if len(indices) > self.k: indices = indices[:self.k]
        if self.workflow:
            requests = set()
            for i in indices:
                if (len(self.allexperiments) + len(requests)) < self.max_iter:
                    e = experiments[i]
                    self.workflow(e)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False
                    requests.add(tuple(e))

            while len(requests) > 0:
                if len(requests) > self.max_instances:
                    self.max_instances = len(requests)
                socks = dict(self.poller.poll(1000))
                if socks:
                    if socks.get(self.receiver) == zmq.POLLIN:
                        msg = self.receiver.recv_string(zmq.NOBLOCK)
                        exp = ast.literal_eval(msg)
                        self.allexperiments.append(exp)
                        requests.discard(tuple(exp[:-1]))
                        x = copy.deepcopy(exp)
                        x[-1] = eval(x[-1])
                        allrets.append(x[-1])
                        self.allresults.append(x)
                else:
                    for tup in requests:
                        exp = list(tup)
                        # TODO check if we need to resend experiments
                        # self.workflow(exp)
                        if self.is_poller_not_sync:
                            time.sleep(1)
                            self.is_poller_not_sync = False
        if (1 == len(set(allrets))):
            if (moralflag == 'bad') and (allrets[0] == goodbad[1]):
                self.believeddecisive.append([testindex, 'bad', val])
            if (moralflag == 'good') and (allrets[0] == goodbad[0]):
                self.believeddecisive.append([testindex, 'good', val])
        if (0 == len(set(allrets))):
            self.believeddecisive.append([testindex, moralflag, val])
        return True

    # ----------------------------------------------------------------------------------------------------------------
    def run(self, filename, input_dict, outputs):
        self.my_inputs = input_dict.keys()
        self.my_outputs = outputs
        self.filename = filename
        self.allexperiments, self.allresults, self.pv_goodness = load_runs(self.filename.replace(".vt", ".adb"),
                                                                           self.my_inputs)
        logging.debug("allresults is: " + str(self.allresults))
        requests = set()
        expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        permutations = load_combinatorial(input_dict)
        for d in permutations:
            exp = []
            for param in self.my_inputs:
                value = d[param]
                exp.append(value)
            if [p for p in exp] not in expers and (len(self.allexperiments) + len(requests)) < self.max_iter:
                self.workflow(exp)
                if self.is_poller_not_sync:
                    time.sleep(1)
                    self.is_poller_not_sync = False
                requests.add(tuple(exp))

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

                    requests.discard(tuple(exp[:-1]))
                    x = copy.deepcopy(exp)
                    x[-1] = eval(x[-1])
                    self.allresults.append(x)
            else:
                for tup in requests:
                    exp = list(tup)
                    # TODO check if we need to resend experiments
                    # self.workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

        # logging.debug('allexperiments: '+str(self.allexperiments))

        self.expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        self.rets = [self.allresults[j][-1] for j in range(len(self.allresults))]
        self.myalllists = self.determinepurity(self.expers, self.rets)

        # ordering the indices
        translist = zip(*self.myalllists)
        pairs = [(len(tup[0]) + len(tup[1]) + len(tup[2]), len(tup[2])) for tup in translist]
        tuples = sorted(enumerate(pairs), key=lambda x: x[1])
        indices = [t[0] for t in tuples]
        newindices = indices

        manufacture = True
        while manufacture:
            manufacture = False
            for i in indices:

                x = self.manufacturetests(i, 'bad', self.myalllists)
                logging.debug("after manufacturetests for bad up to index: " + str(x))
                logging.debug("believeddecisive is: " + str(self.believeddecisive))
                logging.debug("length of all experiments is: " + str(len(self.allexperiments)))

                if (self.first_solution and len(self.believeddecisive) > 0) or len(
                    self.allexperiments) >= self.max_iter: break

                if not (i == indices[-1]):
                    self.expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
                    self.rets = [self.allresults[j][-1] for j in range(len(self.allresults))]
                    self.myalllists = self.determinepurity(self.expers, self.rets)

                    # ordering the indices
                    translist = zip(*self.myalllists)
                    pairs = [(len(tup[0]) + len(tup[1]) + len(tup[2]), len(tup[2])) for tup in translist]
                    tuples = sorted(enumerate(pairs), key=lambda x: x[1])
                    newindices = [t[0] for t in tuples]

                if not (newindices == indices):
                    manufacture = True
                    indices = newindices
                    continue

        self.poller.unregister(self.receiver)
        self.receiver.close()
        self.sender.close()
        self.context.term()
        if self.return_max_instances:
            return self.believeddecisive, len(self.allexperiments), self.max_instances
        return self.believeddecisive, len(self.allexperiments)

    def workflow(self, parameter_list):
        message = self.filename
        message += self.separator + str(parameter_list)
        message += self.separator + str(list(self.my_inputs))
        message += self.separator + str(self.my_outputs)
        if self.origin:
            message += self.separator + str(self.origin) + "_minimal_" + str(self.cohort)
        self.sender.send_string(message)

    def __init__(self, first_solution=False, max_iter=1000, return_max_instances=False, k=numtests, use_score=False,
                 origin=None, separator="|"):
        self.filename = None
        self.allexperiments = []
        self.allresults = []
        self.believeddecisive = []
        self.expers = []
        self.myalllists = []
        self.rets = []
        self.my_kwargs = {}
        self.my_inputs = []
        self.pv_goodness = {}
        self.my_outputs = []
        self.context = zmq.Context()
        self.first_solution = first_solution
        self.max_iter = max_iter
        self.return_max_instances = return_max_instances
        self.max_instances = 0
        self.k = k
        self.use_score = use_score
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