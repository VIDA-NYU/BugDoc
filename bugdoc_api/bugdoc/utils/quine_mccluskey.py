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

'''
Originally Written By JongHewk Park in June 2, 2015
Modified by Raoni Lourenco in January, 2018

Here is the algorithm
1. Find the prime implicants
2. Make Prime implicant chart
3. Find essential prime implicants
4. Use GA for set cover problem

'''


import itertools
import numpy as np
import Queue



#compare two binary strings, check where there is one difference
def compBinary(s1,s2):
    found_one = False
    pos = None
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            if found_one:
                return False, None
            else:
                pos = i
                found_one = True
    return found_one, pos


#compare if the number is same as implicant term
#s1 should be the term
def compBinarySame(term,number):
    for i in range(len(term)):
        if term[i] != '-':
            if term[i] != number[i]:
                return False

    return True


#combine pairs and make new group
def combinePairs(group, unchecked):
    #define length
    keys = group.keys()
    l = len(keys) - 1

    #create next group
    next_group = {}

    #go through the groups
    for i in range(l):
        #first selected group
        for elem1 in group[keys[i]]:
            #next selected group
            for elem2 in group[keys[i+1]]:
                b, pos = compBinary(elem1, elem2)
                if b == True:
                    if keys[i] not in next_group:
                        next_group[keys[i]] = set()
                    unchecked -= {elem1}
                    unchecked -= {elem2}
                    #replace the different bit with '-'
                    new_elem = list(elem1)
                    new_elem[pos] = '-'
                    new_elem = "".join(new_elem)
                    next_group[keys[i]].add(new_elem)
                    unchecked.add(new_elem)
    return next_group, unchecked


#remove redundant lists in 2d list
def remove_redundant(group):
    new_group = []
    for j in group:
        new=[]
        for i in j:
            if i not in new:
                new.append(i)
        new_group.append(new)
    return new_group


#remove redundant in 1d list
def remove_redundant_list(list):
    new_list = []
    for i in list:
        if i not in new_list:
            new_list.append(i)
    return new_list


#return True if empty
def check_empty(group):
    return len(group) == 0


#find essential prime implicants ( col num of ones = 1)
def find_prime(Chart):
    prime = []
    for col in range(len(Chart[0])):
        count = 0
        pos = 0
        for row in range(len(Chart)):
            #find essential
            if Chart[row][col] == 1:
                count += 1
                pos = row

        if count == 1:
            prime.append(pos)

    return prime

def check_all_zero(Chart):
    return np.sum(Chart) == 0

#find max value in list
def find_max(l):
    return np.argmax(l)

#multiply two terms (ex. (p1 + p2)(p1+p4+p5) )..it returns the product
def multiplication(list1, list2):
    list_result = []
    #if empty
    if len(list1) == 0 and len(list2)== 0:
        return list_result
    #if one is empty
    elif len(list1)==0:
        return list2
    #if another is empty
    elif len(list2)==0:
        return list1

    #both not empty
    else:
        for i in list1:
            for j in list2:
                #if two term same
                if i == j:
                    #list_result.append(sorted(i))
                    list_result.append(i)
                else:
                    #list_result.append(sorted(list(set(i+j))))
                    list_result.append(list(set(i+j)))

        #sort and remove redundant lists and return this list
        list_result.sort()
        return list(list_result for list_result,_ in itertools.groupby(list_result))

#petrick's method
def petrick_method(Chart):
    #initial P
    P = []
    for col in range(len(Chart[0])):
        p =[]
        for row in range(len(Chart)):
            if Chart[row][col] == 1:
                p.append([row])
        P.append(p)
    #do multiplication
    for l in range(len(P)-1):
        P[l+1] = multiplication(P[l],P[l+1])

    P = sorted(P[len(P)-1],key=len)
    final = []
    #find the terms with min length = this is the one with lowest cost (optimized result)
    min=len(P[0])
    for i in P:
        if len(i) == min:
            final.append(i)
        else:
            break
    #final is the result of petrick's method
    return final

def ga(Chart):
    alpha = {}
    beta = {}
    S = set()
    U = set(range(len(Chart)))
    w = {}
    #initialization
    for col in range(len(Chart[0])):
        if col not in beta:
            beta[col] = set()
        for row in range(len(Chart)):
            if row not in alpha:
                alpha[row]=set()
                w[row] = 0
            if Chart[row][col] == 1:
                beta[col].add(row)
                alpha[row].add(col)
                S.add(col)
                w[row] += 1
                U -= {row}
    for row in list(U):
        first = True
        minimization = None
        min_j = None
        for j in list(alpha[row]):
            ratio = (1.0) / len(U & beta[j])
            if first:
                minimization = ratio
                min_j = j
                first = False
            elif ratio < minimization:
                min_j = j
                break

        if min_j:
            S.add(min_j)
            for i in list(beta[min_j]):
                w[i] +=1
            U -= beta[min_j]
    slist = list(S)
    slist.sort(key=None,reverse=True)
    for j in slist:
        for i in beta[j]:
            if w[i] > 2:
                S -= {j}
                w[i] -= 1
    return list(S)






#chart = n*n list
def find_minimum_cost(Chart, unchecked):
    P_final = []
    #essential_prime = list with terms with only one 1 (Essential Prime Implicants)
    essential_prime = find_prime(Chart)
    essential_prime = remove_redundant_list(essential_prime)

    
    #modifiy the chart to exclude the covered terms
    for i in range(len(essential_prime)):
        for col in range(len(Chart[0])):
            if Chart[essential_prime[i]][col] == 1:
                for row in range(len(Chart)):
                    Chart[row][col] = 0

    #if all zero, no need for petrick method
    if check_all_zero(Chart) == True:
        P_final = [essential_prime]
    else:
        P = ga(Chart)
        #Replacing petrick_method by GA
        #TODO reference

        P_final.append(P)

        #append prime implicants to the solution of Petrick's method
        for i in P_final:
            for j in essential_prime:
                if j not in i:
                    i.append(j)


    return P_final

#calculate the number of literals
def cal_efficient(s):
    count = 0
    for i in range(len(s)):
        if s[i] != '-':
            count+=1

    return count


#main function
def reduce(n_var, minterms):
    a = minterms
    #put the numbers in list in int form
    a = map(int, a)

    #make a group list
    group = {}
    unchecked = set()
    for i in range(len(a)):
        #convert to binary
        a[i] = bin(a[i])[2:]
        if len(a[i]) < n_var:
            #add zeros to fill the n-bits
            for j in range(n_var - len(a[i])):
                a[i] = '0'+ a[i]
        #if incorrect input
        elif len(a[i]) > n_var:
            print '\nError : Choose the correct number of variables(bits)\n'
            return
        #count the num of 1
        index = a[i].count('1')
        #group by num of 1 separately
        if index not in group:
            group[index] = set()
        group[index].add(a[i])
        unchecked.add(a[i])

    #combine the pairs in series until nothing new can be combined
    count = 0
    while check_empty(group) == False:
        group, unchecked = combinePairs(group,unchecked)
    #make the prime implicant chart
    #Chart = [[0 for x in range(len(a))] for x in range(len(unchecked))]
    unchecked = list(unchecked)
    Chart = np.zeros((len(unchecked),len(a)),dtype=int)
    for i in range(len(a)):
        for j in range (len(unchecked)):
            #term is same as number
            if compBinarySame(unchecked[j], a[i]):
               Chart[j][i] = 1

    primes = find_minimum_cost(Chart, unchecked)
    primes = remove_redundant(primes)

    s= []
    for prime in primes:
        for i in prime:
            if i in range(len(unchecked)):
                s.append(unchecked[i])
    
    return s


def findallpaths(node):
    q = Queue.Queue()
    q.put((node, []))
    puregoodpaths = []
    purebadpaths = []
    input_dict = {}

    while (not q.empty()):
        current = q.get()
        if current[0].results is None:
            key = current[0].col
            value = current[0].value
            if key in input_dict:
                if value not in input_dict[key]:
                    input_dict[key].append(value)
            else:
                input_dict[key] = [value]

            q.put((current[0].fb, current[1] + [(key, value, False)]))
            q.put((current[0].tb, current[1] + [(key, value, True)]))
        elif (len(current[0].results.items()) > 1):
            continue
        elif (current[0].results.items()[0][0]):
            puregoodpaths.append(current[1])
        elif (not current[0].results.items()[0][0]):
            purebadpaths.append(current[1])
    return [puregoodpaths, purebadpaths, input_dict]


def from_paths_to_binary(paths, input_dict):
    miniterms = []
    flatten = []
    for path in paths:
        bits_dict = {}
        for triple in path:
            bits_dict[(triple[0], triple[1])] = triple[2]
        path_possibilities = []
        for param in input_dict.keys():
            for value in input_dict[param]:
                if (param, value) not in flatten:
                    flatten.append((param, value))
                if (param, value) in bits_dict:
                    path_possibilities.append([str(int(bits_dict[(param, value)]))])
                else:
                    path_possibilities.append(['0', '1'])
        miniterms += list(itertools.product(*path_possibilities))
    return [[int(''.join(term), 2) for term in miniterms], flatten]


def prune_tree(t, keys):
    goodpaths, badpaths, input_dict = findallpaths(t)
    miniterms, flatten = from_paths_to_binary(badpaths, input_dict)
    if len(flatten) <= 10:
        s = reduce(len(flatten), miniterms)
        results = []
        for prime in s:
            result = []
            for i in range(len(prime)):
                if prime[i] == '1':
                    result.append(keys[flatten[i][0]] + '=' + str(flatten[i][1]))
                elif prime[i] == '0':
                    result.append(keys[flatten[i][0]] + '!=' + str(flatten[i][1]))
            results.append(result)
    else:
        results = badpaths
    return results