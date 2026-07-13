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


def create_rows(n, m, keys):
    rows = []
    for _ in range(n * m):
        rows.append(dict.fromkeys(keys))
    return rows


def fit(v0, v1, pair, rows, keys):
    if any((d[pair[0]] == v0 and d[pair[1]] == v1) for d in rows):
        return
    for d in rows:
        if d[pair[0]] == v0 and d[pair[1]] is None:
            d[pair[1]] = v1
            return
        if d[pair[0]] is None and d[pair[1]] == v1:
            d[pair[0]] = v0
            return
        if d[pair[0]] is None and d[pair[1]] is None:
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
    for i in range(1, len(lst)):
        pair = (a, lst[i])
        for rest in all_disjoint_pairs(lst[1:i] + lst[i + 1:]):
            yield [pair] + rest


def get_disjoint_pairs_with_max(keys, max0, max1):
    for disjoint_pairs in all_disjoint_pairs(keys):
        if ((max0, max1) in disjoint_pairs) or ((max1, max0) in disjoint_pairs):
            return disjoint_pairs
    return []


def generate_tuples(parameters):
    if not parameters:
        return []

    normalized = {}
    for key, values in parameters.items():
        if isinstance(values, (list, tuple, set)):
            normalized[key] = list(values)
        else:
            normalized[key] = [values]

    if len(normalized) % 2 != 0:
        normalized['dummy'] = ['dummy']

    keys = list(normalized.keys())
    pair_keys = list(itertools.combinations(keys, 2))
    covered_pairs = {pair: set() for pair in pair_keys}

    def pair_lookup(left, right):
        return tuple(sorted((left, right)))

    def can_place(row, pair, value0, value1):
        if row[pair[0]] is not None and row[pair[0]] != value0:
            return False
        if row[pair[1]] is not None and row[pair[1]] != value1:
            return False
        return True

    def gain_for(row, pair, value0, value1):
        if not can_place(row, pair, value0, value1):
            return None

        candidate = dict(row)
        candidate[pair[0]] = value0
        candidate[pair[1]] = value1
        assigned = {key: candidate[key] for key in keys if candidate[key] is not None}

        gain = 0
        for left_key, right_key in itertools.combinations(assigned.keys(), 2):
            pair_key = pair_lookup(left_key, right_key)
            if pair_key not in covered_pairs:
                continue
            value_pair = (assigned[left_key], assigned[right_key])
            if value_pair not in covered_pairs[pair_key]:
                gain += 1
        return gain

    rows = []
    for pair in pair_keys:
        values0 = normalized[pair[0]]
        values1 = normalized[pair[1]]
        for value0 in values0:
            for value1 in values1:
                if (value0, value1) in covered_pairs[pair]:
                    continue

                best_index = None
                best_gain = None
                for index, row in enumerate(rows):
                    row_gain = gain_for(row, pair, value0, value1)
                    if row_gain is None:
                        continue
                    if best_gain is None or row_gain > best_gain or (
                        row_gain == best_gain and (best_index is None or index < best_index)
                    ):
                        best_index = index
                        best_gain = row_gain

                if best_index is None:
                    row = {key: None for key in keys}
                    row[pair[0]] = value0
                    row[pair[1]] = value1
                    rows.append(row)
                    best_index = len(rows) - 1
                else:
                    row = rows[best_index]
                    row[pair[0]] = value0
                    row[pair[1]] = value1

                assigned = {key: rows[best_index][key] for key in keys if rows[best_index][key] is not None}
                for left_key, right_key in itertools.combinations(assigned.keys(), 2):
                    pair_key = pair_lookup(left_key, right_key)
                    if pair_key in covered_pairs:
                        covered_pairs[pair_key].add((assigned[left_key], assigned[right_key]))

                covered_pairs[pair].add((value0, value1))

    normalized.pop('dummy', None)
    value_indices = {key: 0 for key in normalized}
    for row in rows:
        row.pop('dummy', None)
        for key in normalized.keys():
            if row[key] is None:
                values = normalized[key]
                index = value_indices[key] % len(values)
                row[key] = values[index]
                value_indices[key] += 1

    return rows
