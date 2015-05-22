# -*- coding: utf-8 -*-

import argparse
import os
import random

## class for FE sequence.
class FESeq:
    def __init__(self, file, fe, sem):
        self.file = file.split('/')[-1]
        self.fe = ''.join(fe)
        self.felen = len(fe)
        self.sem = sem

    def __str__(self):
        return '%s: %s' % (self.file, self.fe)

    ## contains() is True <=> FE sequence contains [pattern].
    def contains(self, patterns):
        for pattern in patterns:
            if pattern in self.fe:
                return True
        return False

    ## contains_sem() is True <=> FE sequence contains [semlabels].
    def contains_sem(self, semlabels):
        for semlabel in semlabels:
            if semlabel in self.sem:
                return True
        return False

## get last FE sequence.
def get_last_fe(file):
    fe = []
    sem = []
    for line in open(file):
        if line.startswith(('#','*')):
            pass
        elif line.startswith('EOS'): ## last one from EOS
            return FESeq(file, fe, sem)
        else:
            fields = line.split('\t')
            if line.startswith('B'):
                fe.append(fields[1])
                sem.append(fields[0].split(':',1)[1])
            elif line.startswith('I'):
                fe.append(fields[1])
            else:
                if fields[2].split(',')[0] != '記号':
                    fe = []
                    sem = []

## sampling N instances from U.
def sampling(U, N):
    for i in xrange(N):
        index = random.randint(N, len(U)-1)
        U[i], U[index] = U[index], U[i]
    return sorted(U[:N])

def parse_args():
    parser = argparse.ArgumentParser()
    
    ## CRF-parsed files. This is not precise but useful for sampling
    parser.add_argument('-d', default="data/OC_by_CRF/")

    parser.add_argument('-l', type=int, default=0) # lower bound
    parser.add_argument('-u', type=int, default=100) # upper bound
    parser.add_argument('-s', type=int, default=100) # # of sampling 
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    ## filter by # of morphemes
    U = []
    for file in os.listdir(args.d):
        target = get_last_fe(args.d + file)
        if args.l <= target.felen < args.u:
            #print target
            U.append(target.file)
    print len(U) ## checker 6362文になるはず

    ## filter out already annotated 1,627 files
    filtered_U = []
    past_set = [f.replace('.depmod', '.txt') for f in os.listdir('data/JFEcorpus_ver2.0_append/')]
    for i, item in enumerate(U):
        if not item in past_set:
            filtered_U.append(item)
        else: # アノテーション済みの処理
            pass
    print len(filtered_U) # 確認用

    ## sampling
    sampling_max = args.s
    if len(filtered_U) <= sampling_max:
       for instance in filtered_U:
            print instance
    else:
        for instance in sampling(filtered_U, sampling_max):
            print instance
