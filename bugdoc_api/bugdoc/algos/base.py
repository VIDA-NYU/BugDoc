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
import ast

try:
    import zmq
    HAS_ZMQ = True
except ImportError:
    HAS_ZMQ = False


class Debugger(object):
    """ Creates pipeline instances to be run based on execution history and finds root causes of failure.

    This is the base interface for all debugging algorithms in BugDoc library. It takes an entry point of
    a pipeline and a description of the parameter space to generate new instances and return root causes.
    
    Supports two modes:
    - Standalone mode: Pass a callable function directly. No ZMQ dependency required.
    - ZMQ mode: Use traditional ZMQ-based communication with external worker process.
    """

    def __init__(self, max_iter=1000, origin=None, separator="|", send="5557", receive="5558", function=None):
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
            Socket port used to send messages to worker (ZMQ mode only).
        receive: str
            Socket port used to receive messages from worker (ZMQ mode only).
        function: callable or None
            Standalone mode: A callable that takes a parameter dictionary and returns a result.
            If provided, uses direct function execution instead of ZMQ communication.
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
        self.origin = origin
        self.cohort = 0
        self.separator = separator
        
        # Standalone mode configuration
        self.function = function
        self.is_standalone = function is not None
        self._pending_requests = {}  # For standalone mode: track pending requests
        
        # ZMQ mode configuration (only initialize if not in standalone mode)
        if not self.is_standalone:
            if not HAS_ZMQ:
                raise ImportError("ZMQ is required for non-standalone mode. Install with: pip install zmq")
            
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

    def run(self, entry_point, input_dict, outputs=['results']):
        self.my_inputs = list(input_dict.keys())
        self.my_outputs = outputs
        self.entry_point = entry_point

    def _workflow(self, parameter_list):
        """ Execute workflow based on current mode (ZMQ or standalone).
        
        Parameters
        ----------
        parameter_list: list
            List of parameter values in the same order as self.my_inputs
        """
        if self.is_standalone:
            self._workflow_standalone(parameter_list)
        else:
            self._workflow_zmq(parameter_list)

    def _workflow_zmq(self, parameter_list):
        """ ZMQ-based workflow: sends message to external worker process. """
        message = self.entry_point
        message += self.separator + str(parameter_list)
        message += self.separator + str(list(self.my_inputs))
        message += self.separator + str(self.my_outputs)
        if self.origin:
            message += self.separator + str(self.origin) + "_" + str(self.cohort)
        self.sender.send_string(message)

    def _workflow_standalone(self, parameter_list):
        """ Standalone workflow: directly executes the function with parameters. """
        # Build parameter dictionary from parameter list
        param_dict = {}
        for i, param_name in enumerate(self.my_inputs):
            param_dict[param_name] = parameter_list[i]
        
        # Execute the function and collect results
        result = self.function(param_dict)
        
        # Store results in the same format as ZMQ mode for compatibility
        experiment_with_result = list(parameter_list) + [result]
        self.allexperiments.append(experiment_with_result)
        self.allresults.append(experiment_with_result)
        
        # Track this as a pending request (so poller.poll() returns immediately in standalone mode)
        self._pending_requests[str(parameter_list)] = experiment_with_result

    def process_standalone_results(self):
        """ For standalone mode: process pending results. 
        
        Call this method where you would normally handle poller results.
        Returns the next pending result or None.
        """
        if self._pending_requests:
            # Return and remove the first pending result
            key = next(iter(self._pending_requests))
            result = self._pending_requests.pop(key)
            return result
        return None

    def has_pending_results(self):
        """ Check if there are pending results in standalone mode. """
        return len(self._pending_requests) > 0

    def poll_results(self, timeout=10000):
        """ Poll for results in a mode-agnostic way.
        
        In standalone mode, returns pending results immediately.
        In ZMQ mode, uses the ZMQ poller.
        
        Parameters
        ----------
        timeout: int
            Timeout in milliseconds for ZMQ mode. Ignored in standalone mode.
            
        Returns
        -------
        dict or None
            In standalone mode: next pending result as experiment list, or None if no pending
            In ZMQ mode: socket dict from poller, or empty dict on timeout
        """
        if self.is_standalone:
            # In standalone mode, check for pending results
            if self._pending_requests:
                key = next(iter(self._pending_requests))
                result = self._pending_requests.pop(key)
                return {'standalone': result}
            return {}
        else:
            # In ZMQ mode, use the poller
            return dict(self.poller.poll(timeout))

    def get_result_from_poll(self, socks):
        """ Extract result from poll response in a mode-agnostic way.
        
        Parameters
        ----------
        socks: dict
            Result from poll_results()
            
        Returns
        -------
        list or None
            The experiment result [param1, param2, ..., result], or None if no result
        """
        if self.is_standalone:
            if 'standalone' in socks:
                return socks['standalone']
            return None
        else:
            # In ZMQ mode, check if receiver socket has data
            if socks.get(self.receiver):
                import zmq
                msg = self.receiver.recv_string(zmq.NOBLOCK)
                return ast.literal_eval(msg)
            return None
