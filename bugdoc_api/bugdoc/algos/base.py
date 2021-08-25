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
from builtins import object
import zmq

class Debugger(object):
    """ Creates pipeline instances to be run based on execution history and finds root causes of failing.

    This is the base interface for all debugging algorithms in BugDoc library. It takes an entry point of
    a pipeline and a description of the parameter space to generate new instances and return root cayses.
    """

    def __init__(self, max_iter=1000, origin=None, separator="|", send="5557", receive="5558"):
        """ Build a new debugging algorithm object.

        Parameters
        ----------
        max_iter: int
            Maximum number of instances to be created.
        origin: None or str
            Additional provenance information to be added to the history of pipeline instances.
        separator: str
            Character to be used as separator between data fields that are sent as string to debugger worker.
        send: str
            Socket port used to send messages to worker.
        receive: str
            Socket port used to receive messages from worker.
        """
        self.entry_point = None
        self.allexperiments = []
        self.allresults = []
        self.believeddecisive = []
        self.expers = []
        self.rets = []
        self.my_inputs = []
        self.my_outputs = []

        self.max_iter = max_iter

        self.context = zmq.Context()

        # Socket to send messages on
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:%s" % send)

        # Socket with direct access to the sink: used to syncronize start of batch
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:%s" % receive)

        self.poller = zmq.Poller()
        self.poller.register(self.receiver, zmq.POLLIN)
        self.is_poller_not_sync = True
        self.origin = origin
        self.cohort = 0
        self.separator = separator

    def run(self, entry_point, input_dict, outputs=['results']):
        self.my_inputs = list(input_dict.keys())
        self.my_outputs = outputs
        self.entry_point = entry_point

    def _workflow(self, parameter_list):
        message = self.entry_point
        message += self.separator + str(parameter_list)
        message += self.separator + str(list(self.my_inputs))
        message += self.separator + str(self.my_outputs)
        if self.origin:
            message += self.separator + str(self.origin) + "_" + str(self.cohort)
        self.sender.send_string(message)
