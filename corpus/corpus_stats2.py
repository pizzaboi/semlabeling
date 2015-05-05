#! /usr/bin/python
# -*- coding: utf-8 -*-

#usage: corpus_stats.py [-h] [-l LABEL] [-a AMBIGUOUS] [-s] corpus
#
#positional arguments:
#  corpus
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -l LABEL, --label LABEL
#                        Show top n type of Labels.
#  -a AMBIGUOUS, --ambiguous AMBIGUOUS
#                        Count and show top n ambiguous Functional Expressions.
#  -s, --fe-size         Count FE word size.

import argparse
from collections import defaultdict
import os
import lib.csvReader as csvReader

BLUE = '\033[38;5;33m'
NORMAL = '\033[0m'

class FunctionalExpression:
    def __init__(self):
        self.surface = ''
        self.component = []
        self.sem = ''

    def get_surface(self):
        self.surface = '.'.join(self.component)

class CorpusExplorer:
    def __init__(self):
        self.num_of_sentences = 0
        self.num_of_predicates = 0
        self.d1 = defaultdict(lambda : defaultdict(int))
        self.d2 = defaultdict(int)

    def count_fe(self, fe):
        fe.get_surface()
        self.d1[fe.surface][fe.sem] += 1
        self.d2[fe.sem] += 1

    def counter_new(self, corpus, t):
        # patterns
        # otherwise -> fe: increment # of predicates, create new fe
        # otherwise -> otherwise: none
        # otherwise -> EOS: none
        # fe -> otherwise: append fe into subseq, subsequence into sequence
        # fe -> fe: append subsequence, create new fe
        # fe -> EOS: append fe into subsequence, subsequence into sequence
        for src in [f for f in os.listdir(corpus) if not f.startswith('.DS_Store')]:
            sequence = []
            sub_sequence = []
            self.num_of_sentences += 1

            fe = FunctionalExpression()
            for line in open(corpus + src):
                #fe -> fe, otherwise -> fe
                if line.startswith('B'):
                    if fe.component:
                        #fe -> fe
                        sub_sequence.append(fe)
                    else:
                        #otherwise -> fe
                        #Counting predicates depending on label C cause
                        #incorrect number of predicates because some C don't
                        #have any functional expressions.
                        self.num_of_predicates += 1

                    fe = FunctionalExpression()
                    fe.sem = line.split('\t')[0].split('-',1)[1]
                    fe.component = [line.split('\t')[1]]

                elif line.startswith('I'):
                    fe.component.append(line.split('\t')[1])

                #fe -> otherwise
                elif line.startswith('O') and fe.component:
                    sub_sequence.append(fe)
                    sequence.append(sub_sequence)
                    sub_sequence = []
                    fe = FunctionalExpression()

                #fe -> EOS
                elif line.startswith('EOS') and fe.component:
                    sub_sequence.append(fe)
                    sequence.append(sub_sequence)

            if t and sequence:
                for fe in sequence[-1]:
                    self.count_fe(fe)
            else:
                for subsequence in sequence:
                    for fe in subsequence:
                        self.count_fe(fe)

    def print_colored(self, description, num, color=BLUE):
        print '%s%s: %3d%s' % (color, description, num, NORMAL)

    def show_labels(self, max_label):
        if max_label == 0:
            return
        print 'label\tfreq.\t%' #header
        for e in sorted(self.d2.iteritems(), key=lambda x:x[1], reverse=True):
            if max_label <= 0:
                break
            percent = float(e[1]) / float(sum(self.d2.values())) * 100
            print '%s\t%4d\t%2.1f%%' % (e[0], e[1], percent)
            max_label += -1

    def show_ambiguous(self, min_amb):
        num_of_ambigious = 0
        if min_amb == 0:
            return
        print 'FE\tfreq.\tdeg.' # header
        for e in sorted(self.d1.iteritems(),key=lambda x:len(x[1]), reverse=True):
            if len(e[1]) < min_amb:
                break
            num_of_ambigious += 1
            print '%s\t%d\t%d' % (
                e[0].replace('.',''), sum(self.d1[e[0]].values()), len(e[1]))
        self.print_colored('num_of_ambigious', num_of_ambigious)

    def show_numbers(self):
        d1, d2 = self.d1, self.d2
        self.print_colored('num_of_sentences', self.num_of_sentences)
        self.print_colored('num_of_functional_expressions', sum(d2.values()))
        self.print_colored('type_of_funtional_expresisons', len(d1))
        self.print_colored('num_of_predicates', self.num_of_predicates)
        self.print_colored('type_of_labels', len(d2))

        comp_count = 0
        comp_type = 0
        comp_max_len = 0
        for k in d1.keys():
            if len(k.split('.')) > 1:
                comp_type += 1
                comp_count += sum(d1[k].values())
                comp_max_len = max(comp_max_len, len(k.split('.')))
        self.print_colored('num_of_compounds', comp_count)
        self.print_colored('type_of_compounds', comp_type)
        self.print_colored('compounds_max_len', comp_max_len)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--corpus', type=str, default='data/JFEcorpus_ver2.1/')
    parser.add_argument('-l', '--label', type=int, default=0, help="Show top n type of Labels.")
    parser.add_argument('-a', '--ambiguous', type=int, default=0, help="Count and show top n ambiguous Functional Expressions.")
    parser.add_argument('-hc', '--head', action="store_true")
    args = parser.parse_args()
    return args

if __name__ ==  '__main__':
    args = parse_args()
    ce = CorpusExplorer()
    ce.counter_new(args.corpus, args.head)
    ce.show_numbers()
    ce.show_labels(args.label)
    ce.show_ambiguous(args.ambiguous)
