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
import ast
import copy
import logging
import pandas as pd
import os
import random
import time
import zmq
from bugdoc.utils.utils import load_runs, numtests, load_combinatorial

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class AutoDebug(object):



    def generate_data_interventions(self,bad_dataframe,good_dataframes):

        def compute_score(row,b,g):
            return min(row['score'],abs(row[b]-row[g]))


        columns = good_dataframes[0].columns
        max_diff_columns = {}
        column_dataframes = {}

        for c in columns:
            df = pd.DataFrame()
            df['bad'] = bad_dataframe[c]
            first = True
            for g in range(len(good_dataframes)):
                good = good_dataframes[g]
                df['good_' + str(g)] = good[c]
                if first:
                    col_diff = bad_dataframe[c].sub(good[c], axis=0).abs()
                    df['score'] = col_diff
                    first = False
                else:
                    df['score'] = df.apply(lambda row: compute_score(row, 'bad', 'good_' + str(g)), axis=1)
            max_diff_columns[c] = max(df['score'])
            df.sort_values(by=['score'], inplace=True, ascending=False)
            column_dataframes[c] = df

        column_order = [pair[0] for pair in sorted(max_diff_columns.items(), key=lambda item: item[1], reverse=True)]

        return column_dataframes, column_order


    def execute_intervention(self, dataframe, input_dict):
        result = False
        temp_dataset_file = os.path.join(os.path.dirname(input_dict['dataset']),"temp.csv")
        input_dict['dataset'] = temp_dataset_file
        dataframe.to_csv(temp_dataset_file, index=False)

        requests = set()

        exp = []
        for param in self.my_inputs:
            value = input_dict[param]
            exp.append(value)
        self.workflow(exp)
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
                    requests.discard(str(exp[:-1]))
                    x = copy.deepcopy(exp)
                    x[-1] = eval(x[-1])
                    result = x[-1]
            else:
                for tup in requests:
                    exp = list(tup)
                    # TODO check if we need to resend experiments
                    # self.workflow(exp)
                    if self.is_poller_not_sync:
                        time.sleep(1)
                        self.is_poller_not_sync = False

        return result

    def replace_column(self,column, column_dataframes, bad_dataframe, input_dict):
        bad_col = bad_dataframe[column]
        bad_dataframe[column] = column_dataframes[column]['good_0']
        # Test
        result = self.execute_intervention(bad_dataframe, input_dict)
        #roll back
        bad_dataframe[column] = bad_col
        return result

    def replace_keys(self, column, column_dataframes, bad_dataframe, keys, input_dict):
        bad_col = bad_dataframe[column]
        bad_dataframe[column][keys] = column_dataframes[column]['good_0'][keys]
        # Test
        result = self.execute_intervention(bad_dataframe, input_dict)
        # roll back
        bad_dataframe[column] = bad_col
        return result


    def run(self, filename, input_dict, bad_dataset, good_datasets, outputs):
        bad_dataframe = pd.read_csv(bad_dataset)
        good_dataframes = [pd.read_csv(file).select_dtypes(include='number') for file in good_datasets]
        input_dict['dataset'] = bad_dataset
        self.my_inputs = input_dict.keys()
        self.my_outputs = outputs
        self.filename = filename

        column_dataframes, column_order = self.generate_data_interventions(bad_dataframe,good_dataframes)
        for column in column_order:
            flipped = self.replace_column(column, column_dataframes, bad_dataframe, input_dict)
            if flipped:
                keys = list(column_dataframes[column].index)
                while len(keys) > 1:
                    sub_keys = keys[:len(keys)//2]
                    flipped = self.replace_keys(column, column_dataframes, bad_dataframe, sub_keys, input_dict)
                    if flipped:
                        keys = sub_keys
                    else:
                        break
                self.believeddecisive = [column, keys]
                break


        self.poller.unregister(self.receiver)
        self.receiver.close()
        self.sender.close()
        self.context.term()
        return self.believeddecisive


    def workflow(self, parameter_list):
        message = self.filename
        message += self.separator + str(parameter_list)
        message += self.separator + str(list(self.my_inputs))
        message += self.separator + str(self.my_outputs)
        if self.origin:
            message += self.separator + str(self.origin) + "_shortcut_" + str(self.cohort)
        self.sender.send_string(message)

    def __init__(self, origin=None, separator="|"):
        self.filename = None
        self.believeddecisive = []
        self.my_inputs = []
        self.my_outputs = []

        self.context = zmq.Context()

        # Socket to send messages on
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:5567")

        # Socket with direct access to the sink: used to syncronize start of batch
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:5568")

        self.poller = zmq.Poller()
        self.poller.register(self.receiver, zmq.POLLIN)
        self.is_poller_not_sync = True
        self.origin = origin
        self.cohort = 0
        self.separator = separator
