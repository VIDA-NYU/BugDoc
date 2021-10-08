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
import queue
import numpy
class Pipeline(object):
    def __init__(self):
        self.id = 1
        self.origin = ""
        self.parameters = []
        self.modules = []
        self.connections = []
        self.end_modules = []



class PipelineModule(object):
    def __init__(self):
        self.pipeline = None
        self.id = 1
        self.connections_from = []
        self.connections_to = []


class PipelineConnection(object):
    def __init__(self):
        self.pipeline = None
        self.from_module = []
        self.to_module = []


class PipelineParameter(object):
    def __init__(self):
        self.pipeline = None
        self.module = None
        self.name = ""
        self.values = []



def nodes_to(node, nodes_to_node=set()):

    for c in node.connections_to:
        nodes_to_node.add(c.module_from.id)
        nodes_to(c.module_from, nodes_to_node)

    return nodes_to_node

def params(node, pipeline):
    return set([p.id for p in pipeline.parameters if p.module.id == node.id])

def params_to(node, pipeline):
    params_to_node = set()
    for n in nodes_to(node):
        params_to_node.union(params(n,pipeline))
    return params_to_node

def paths(origin_node, end_node):
    q = queue.Queue()
    q.put((origin_node, []))
    end_paths = []
    while (not q.empty()):
        current = q.get()
        if current[0] == end_node:
            end_paths.append(current[1]+[end_node])
        else:
            for node in current[0].modules_to:
                if node in nodes_to(end_node):
                    q.put((node, current[1] + [current[0]]))
    return end_paths

def exclusive_to(node, pipeline):
    param_to_node = params_to(node,pipeline)
    exclusive_to_node = set()
    for p in param_to_node:
        if all([node in path for e in pipeline.end_modules for path in paths(p.module,e)]):
            exclusive_to_node.append(p)
    return exclusive_to_node

def cross_size(parameters):
    return numpy.prod([len(p.values) for p in parameters])

def node_to_instrument(pipeline):
    min_node_val = None
    min_node = None

    for node in pipeline.modules - pipeline.end_modules:
        node_val = max([
            cross_size(exclusive_to(node,pipeline)),
            cross_size(pipeline.parameters - exclusive_to(node,pipeline))
        ])
        if not min_node:
            min_node_val = node_val
            min_node = node
        elif node_val < min_node_val:
            min_node_val = node_val
            min_node = node

    return min_node


