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
import random
from bugdoc.algos.base import Debugger
from bugdoc.utils.utils import load_runs, numtests, load_combinatorial

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class Shortcut(Debugger):

    def determinepurity(self, myarr, mytarg):
        goodlist = []
        badlist = []
        for i in range(len(mytarg)):
            if mytarg[i]:
                goodlist.append(myarr[i])
            else:
                badlist.append(myarr[i])
        return [goodlist, badlist]

    def get_good_and_bad_instances(self, goodlist, badlist):
        for cg in goodlist:
            for cf in badlist:
                if (all([cg[i] != cf[i] for i in range(len(cf))])):
                    return [cg, cf]
        return [random.choice(goodlist), random.choice(badlist)]

    def run(self, entry_point, input_dict, outputs=['results']):
        super().run(entry_point, input_dict, outputs=outputs)
        self.allexperiments, self.allresults, _ = load_runs(self.entry_point + ".adb", self.my_inputs)
        # logging.debug("allresults is: "+str(self.allresults))
        requests = set()
        expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        permutations = load_combinatorial(input_dict)
        for d in permutations:
            exp = []
            for param in self.my_inputs:
                value = d[param]
                exp.append(value)
            if exp not in expers and (len(self.allexperiments) + len(requests)) < self.max_iter:
                self._workflow(exp)
                if self.is_poller_not_sync:
                    time.sleep(1)
                    self.is_poller_not_sync = False
                requests.add(str(exp))

        while len(requests) > 0:
            socks = dict(self.poller.poll(10000))
            if socks:
                if socks.get(self.receiver) == zmq.POLLIN:
                    msg = self.receiver.recv_string(zmq.NOBLOCK)
                    exp = ast.literal_eval(msg)
                    self.allexperiments.append(exp)
                    requests.discard(str(exp[:-1]))
                    x = copy.deepcopy(exp)
                    #x[-1] = eval(x[-1])
                    result = x[-1]
                    # We could run the experiment
                    if result is not None:
                        self.allresults.append(x)
            else:
                for tup in requests:
                    exp = list(tup)
                    # TODO check if we need to resend experiments
                    # self._workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

        # logging.debug('allexperiments: '+str(self.allexperiments))

        self.expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        self.rets = [self.allresults[j][-1] for j in range(len(self.allresults))]
        goodlist, badlist = self.determinepurity(self.expers, self.rets)
        logging.debug("goodlist: " + str(goodlist))

        if len(goodlist) > 0 and len(badlist) > 0:
            cg, cf = self.get_good_and_bad_instances(goodlist, badlist)
            logging.debug("Retrieving cf and cg: " + str(cf) + " , " + str(cg))
            cf_orig = copy.deepcopy(cf)

            for p in range(len(cf)):
                cf_aux = copy.deepcopy(cf)
                cf_aux[p] = cg[p]
                result = False
                if cf_aux not in self.expers:

                    self._workflow(cf_aux)

                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

                    requests.add(str(cf_aux))

                    while len(requests) > 0:
                        socks = dict(self.poller.poll(10000))
                        if socks:
                            if socks.get(self.receiver) == zmq.POLLIN:
                                msg = self.receiver.recv_string(zmq.NOBLOCK)
                                exp = ast.literal_eval(msg)
                                self.allexperiments.append(exp)
                                requests.discard(str(exp[:-1]))
                                x = copy.deepcopy(exp)
                                #x[-1] = eval(x[-1])
                                result = x[-1]
                                # We could run the experiment
                                if result is not None:
                                    self.allresults.append(x)
                        else:
                            for tup in requests:
                                exp = list(tup)
                                # TODO check if we need to resend experiments
                                # self._workflow(exp)
                                if self.is_poller_not_sync:
                                    time.sleep(1)
                                    self.is_poller_not_sync = False
                else:
                    index = self.expers.index(cf_aux)
                    result = self.rets[index]
                # We could not run the experiment
                if result is None:
                    break
                if not result:
                    badlist.append(cf_aux)
                    cf = copy.deepcopy(cf_aux)
                else:
                    goodlist.append(cf_aux)

            believeddecisive = []
            for i in range(len(cf)):
                if cf_orig[i] == cf[i]:
                    believeddecisive.append([i, cf_orig[i]])
            logging.debug("believeddecisive: " + str(believeddecisive))
            logging.debug("goodlist: " + str(goodlist))
            for good_instance in goodlist:
                if all([good_instance[i] == v for i, v in believeddecisive]):
                    logging.debug("good_instance: " + str(good_instance))
                    believeddecisive = []
                    break
            self.believeddecisive = believeddecisive

        self.poller.unregister(self.receiver)
        self.receiver.close()
        self.sender.close()
        self.context.term()

        return self.believeddecisive, len(self.allexperiments)


    def __init__(self, max_iter=1000, origin=None, separator="|", send="5557", receive="5558"):
        super(Shortcut, self).__init__(max_iter=max_iter,
                                       origin=origin,
                                       separator=separator,
                                       send=send,
                                       receive=receive
                                       )

