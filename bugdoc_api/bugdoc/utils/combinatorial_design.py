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

import itertools
import random

def create_rows(n,m,keys):
	rows = []
	for i in range(n*m):
		rows.append(dict.fromkeys(keys))
	return rows


def fit(v0,v1,pair,rows,keys):
	if any((d[pair[0]] == v0 and d[pair[1]] == v1) for d in rows): return
	for d in rows:
		if d[pair[0]] == v0 and d[pair[1]] == None:
			d[pair[1]] = v1 
			return
		if d[pair[0]] == None and d[pair[1]] == v1:
			d[pair[0]] = v0 
			return
		if d[pair[0]] == None and d[pair[1]] == None:
			d[pair[0]] = v0
			d[pair[1]] = v1
			return
	rows.append(dict.fromkeys(keys))
	rows[-1][pair[0]] = v0
	rows[-1][pair[1]] = v1


def all_disjoint_pairs(lst):
    if len(lst) < 2:
        yield lst
        return
    a = lst[0]
    for i in range(1,len(lst)):
        pair = (a,lst[i])
        for rest in all_disjoint_pairs(lst[1:i]+lst[i+1:]):
            yield [pair] + rest



def get_disjoint_pairs_with_max(keys,max0,max1):
	for disjoint_pairs in all_disjoint_pairs(keys):
		if ((max0,max1) in disjoint_pairs) or ((max1,max0) in disjoint_pairs):
			return  disjoint_pairs




def generate_tuples(parameters):
	if (len(parameters.keys()) % 2 != 0):
		parameters['dummy'] = []
	keys = list(parameters.keys())
	max0 = keys[0]
	max1 = keys[1]
	for key in keys[1:]:
		if len(parameters[key]) >= len(parameters[max0]):
			max1 = max0
			max0 = key
		elif len(parameters[key]) > len(parameters[max1]):
			max1 = key

	
	handled_pairs = get_disjoint_pairs_with_max(keys,max0,max1)
	rows = create_rows(len(parameters[max0]),len(parameters[max1]),keys)
	for pair in handled_pairs:
		row_index = 0
		for v0 in parameters[pair[0]]: 
			for v1 in parameters[pair[1]]:
				rows[row_index][pair[0]] = v0
				rows[row_index][pair[1]] = v1
				row_index += 1

	pairs = list(itertools.combinations(keys, 2))
	for pair in pairs:
		if pair not in handled_pairs:
			for v0 in parameters[pair[0]]: 
				for v1 in parameters[pair[1]]:
					fit(v0,v1,pair,rows,keys)			
			handled_pairs.append(pair)
	parameters.pop('dummy', None)
	for row in rows:
		row.pop('dummy', None)
		for key in parameters.keys():
			if (row[key] == None):
				row[key] = random.choice(list(parameters[key]))
	return rows

