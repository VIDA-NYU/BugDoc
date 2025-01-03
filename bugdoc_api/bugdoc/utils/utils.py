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

from __future__ import division
from __future__ import print_function

import copy
import json
import logging
import os
import sys
import traceback

from builtins import str
from builtins import range
from bugdoc.utils.combinatorial_design import generate_tuples

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

goodbad = [True, False]
numtests = 30



def compute_score(experiment, input_parameters, pv_goodness, moralflag):
    score = 0
    for i in range(len(input_parameters)):
        key = input_parameters[i]
        v = experiment[i]
        score += float(pv_goodness[key][v][moralflag]) / float(pv_goodness[key][v]['good'] + pv_goodness[key][v]['bad'])
    return score


def load_runs(filename, input_keys, lims=None):
    if os.path.isfile(filename):
        fileicareabout = open(filename, "r")
    else:
        fileicareabout = open(filename, "w+")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    allexperiments = []
    allresults = []  # experiments and their results
    pv_goodness = {}  # number of good and bad instances by parameter-value

    if lims is None:
        lims = [0, len(alllines)]
    for e in alllines[lims[0]:lims[1]]:
        try:
            exp = []
            exp_dict = json.loads(e[:-1])
            
            result_value = exp_dict['result']

            for key in input_keys:
                if key not in pv_goodness:
                    pv_goodness[key] = {}

                v = exp_dict[key]
                exp.append(v)

                if v not in pv_goodness[key]:
                    pv_goodness[key][v] = {'good': 0, 'bad': 0}

                if eval(result_value):
                    pv_goodness[key][v]['good'] += 1
                else:
                    pv_goodness[key][v]['bad'] += 1
            exp.append(result_value)
            allexperiments.append(exp)
        except:
            traceback.print_exc(file=sys.stdout)

    for e in allexperiments:
        x = copy.deepcopy(e)
        x[-1] = eval(x[-1])
        allresults.append(x)
    return [allexperiments, allresults, pv_goodness]


def load_dataxray(filename, input_keys, lims=None):
    if os.path.isfile(filename):
        fileicareabout = open(filename, "r")
    else:
        fileicareabout = open(filename, "w+")
    alllines = fileicareabout.readlines()
    fileicareabout.close()

    feature_vector = ""
    for _ in input_keys:
        feature_vector += 'a:'
    feature_vector += "\t" + feature_vector.replace('a',
                                                    '1') + ';rate;cost;false;' + feature_vector + ';' + feature_vector.replace(
        'a', '0') + ';' + str(len(alllines)) + ';0;'
    count = 0
    count_error = 0
    if lims is None:
        lims = [0, len(alllines)]
    print(('limits', str(lims)))
    for e in alllines[lims[0]:lims[1]]:
        try:
            exp_dict = json.loads(e[:-1])
            result = exp_dict['result']
            feature_vector += str(count) + '%' + str(result) + '%'
            if not result:
                count_error += 1
            for key in input_keys:
                if type(exp_dict[key]) == str:
                    v = exp_dict[key].encode("utf-8")
                else:
                    v = exp_dict[key]
                feature_vector += 'a_' + key + '#' + str(v) + ':'
            count += 1
            feature_vector += '='
        except:
            pass
    # TODO learn how to compute cost
    return feature_vector.replace('rate', str(0 if count == 0 else count_error / float(count))).replace('cost', '99.99')


def load_combinatorial(input_dict):
    return generate_tuples(input_dict)


def _iterate_over_keys(permutations, current_permutation, input_dict):
    key = list(current_permutation.keys())[-1]
    if key == list(input_dict.keys())[-1]:
        for value in input_dict[key]:
            current_permutation[key] = value
            permutation = copy.deepcopy(current_permutation)
            permutations.append(permutation)
    else:
        current_permutation[list(input_dict.keys())[len(list(current_permutation.keys()))]] = None
        for value in input_dict[key]:
            current_permutation[key] = value
            permutation = copy.deepcopy(current_permutation)
            _iterate_over_keys(permutations, permutation, input_dict)


def load_permutations(input_dict):
    permutations = []
    current_permutation = {list(input_dict.keys())[0]: None}
    _iterate_over_keys(permutations, current_permutation, input_dict)
    return permutations


def record_python_run(paramDict, vistrail_name, origin=None):
    if origin:
        paramDict["origin"] = origin
    file_name = vistrail_name.replace('.vt', '.adb')
    f = open(file_name, "a")
    f.write(json.dumps(paramDict) + '\n')
    f.close()


def record_pipeline_run(filename,values,parameters,result, origin=None):
    """

    :param filename:
    :param values:
    :param parameters:
    :param result:
    :param origin:
    :return:
    """
    paramDict = {
        parameters[i] : values[i]
        for i in range(len(parameters))
    }
    paramDict['result'] = str(result)

    if origin:
        paramDict["origin"] = origin

    logging.debug('Filename: ' + filename)
    logging.debug('New configuration: ' + str(paramDict))
    
    f = open(filename, "a")
    f.write(json.dumps(paramDict) + '\n')
    f.close()

