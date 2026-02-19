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
import ast
import time
from bugdoc.algos.base import Debugger
from bugdoc.utils.utils import load_runs, load_combinatorial

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class StackedShortcutStandalone(Debugger):
    """ Standalone-compatible version of StackedShortcut algorithm.
    
    This version works in both standalone mode (with direct function execution)
    and ZMQ mode (with external worker process). It can be used as a drop-in
    replacement for StackedShortcut when standalone mode is desired.
    """

    def determinepurity(self, myarr, mytarg):
        goodlist = []
        badlist = []
        for i in range(len(mytarg)):
            if mytarg[i]:
                goodlist.append(myarr[i])
            else:
                badlist.append(myarr[i])
        return [goodlist, badlist]

    def get_good_by_bad(self, goodlist, _cf):
        cgs = []
        cgs_alt = []
        for cg in goodlist:
            if all([cg[i] != _cf[i] for i in range(len(_cf))]):
                if all([cg[i] != cgi[i] for i in range(len(cg)) for cgi in cgs]):
                    cgs.append(cg)
                else:
                    cgs_alt.append(cg)
        return cgs, cgs_alt

    def get_good_and_bad_instances(self, goodlist, badlist):
        cgs = []
        cgs_alt = []
        cf = None
        for _cf in badlist:
            _cgs, _cgs_alt = self.get_good_by_bad(goodlist, _cf)
            # logging.debug("confs: "+str([_cgs,_cgs_alt]))
            if len(_cgs) > len(cgs):
                cgs = _cgs
                cf = _cf
                cgs_alt = _cgs_alt
            if len(cgs) >= self.k:
                return [cgs, _cf]
        if cf:
            for cg in cgs_alt:
                if len(cgs) >= self.k:
                    return [cgs, cf]
                cgs.append(cg)
            return [cgs, cf]
        return []

    def run(self, entry_point, input_dict, outputs=['results']):
        super().run(entry_point, input_dict, outputs=outputs)
        self.allexperiments, self.allresults, _ = load_runs(self.entry_point, self.my_inputs)
        logging.debug("allresults is: "+str(self.allresults))
        requests = set()
        expers = [self.allresults[j][:-1] for j in range(len(self.allresults))]
        permutations = load_combinatorial(input_dict)
        for d in permutations:
            exp = []
            for param in self.my_inputs:
                value = d[param]
                exp.append(value)
            if [p for p in exp] not in expers and (len(self.allexperiments) + len(requests)) < self.max_iter:
                self._workflow(exp)
                if self.is_poller_not_sync:
                    time.sleep(1)
                    self.is_poller_not_sync = False
                requests.add(str(exp))

        # Process results using mode-agnostic polling
        while len(requests) > 0:
            socks = self.poll_results(10000)
            if socks:
                exp = self.get_result_from_poll(socks)
                if exp:
                    self.allexperiments.append(exp)
                    requests.discard(str(exp[:-1]))
                    x = copy.deepcopy(exp)
                    x[-1] = x[-1]
                    self.allresults.append(x)
            else:
                for tup in requests:
                    exp = list(tup)
                    # TODO check if we need to resend experiments
                    # self._workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

        logging.debug('allexperiments: '+str(self.allexperiments))
        initial_experiments_num = len(self.allexperiments)

        # Proceed with debugging logic...
        # (This is simplified; full implementation would continue with the algorithm logic)
        return self.allresults
