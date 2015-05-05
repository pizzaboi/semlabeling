#! /usr/bin/python
# -*- coding: utf-8 -*-

import csv
from collections import defaultdict

class Kappa:
    """述語のKappa値を計算する"""
    def __init__(self, matrix):
        #self.predicate_matrix = defaultdict(lambda : defaultdict(int))
        #self.chunk_matrix = defaultdict(lambda : defaultdict(int))
        #self.sem_matrix = defaultdict(lambda : defaultdict(int))
        self.instance_matrix = matrix
        self.keys = set()
        self.instance = 0

    def get_key(self, m):
        """keyを取得する"""
        for k1, v in m.iteritems():
            self.keys.add(k1)
            for k2 in v.keys():
                self.keys.add(k2)

    def count_instance(self, m):
        """instance数を数える"""
        for k, v in m.iteritems():
            self.instance += sum(v.values())

    def pa(self, m):
        observed_agreement = 0
        for k in self.keys:
            observed_agreement += m[k][k]
        return 1.0 * observed_agreement / self.instance

    def pe(self, m, k):
        worker1 = 1.0 * sum(m[k].values()) / self.instance
        worker2 = 0
        for k2 in self.keys:
            worker2 += m[k2][k]
        worker2 = 1.0 * worker2 / self.instance
        return worker1 * worker2

    def show_matrix(self, m):
        print ' '*5 + ' '.join(['%4s' % k1 for k1 in self.keys])
        for k1 in self.keys:
            print '%4s' % k1,
            print ' '.join(['%4s' % str(m[k1][k2]) for k2 in self.keys])

    def calc(self):
        #self.load_data(src)

        #m = self.predicate_matrix
        #m = self.chunk_matrix
        #m = self.sem_matrix
        #m = csv2dict()
        m = self.instance_matrix

        self.get_key(m)
        self.count_instance(m)
        self.show_matrix(m)
        print 'インスタンス数：%d' % (self.instance)

        pa = self.pa(m)
        print '見かけの一致率；%f' % pa

        pe = 0
        for k in self.keys:
            e = self.pe(m, k)
            pe += e
            print 'ラベル%sの偶然の一致率：%f' % (k, e)
        print '全体の偶然の一致率：%f' % pe

        kappa = (pa - pe) / (1 - pe)
        print 'Kappa = %f' % kappa

def csv2dict(csv_file):
    import csv
    instance_matrix = defaultdict(lambda: defaultdict(int))
    reader = csv.reader(open(csv_file, 'U'), delimiter=',')
    try:
        count = -1
        predicate_match = False
        for row in reader:
            if row[0].startswith('OC'):
                # predicate
                worker1 = row[2] if row[2] == 'C' else 'O'
                worker2 = row[4] if row[4] == 'C' else 'O'
                instance_matrix[worker1][worker2] += 1

                # chunking
#                worker1 = row[2] if row[2] else 'O'
#                worker2 = row[4] if row[4] else 'O'
#                if worker1 == 'C' and worker2 == 'C':
#                    predicate_match = True
#                elif worker1 == 'O' and worker2 == 'O' \
#                    or worker1 == 'C' and worker2 != 'C' \
#                    or worker1 != 'C' and worker2 == 'C':
#                    predicate_match = False
#                elif worker1 in ('B','I','O') and worker2 in ('B','I','O') \
#                    and predicate_match:
#                    instance_matrix[worker1][worker2] += 1
#
#                # semlabel
#                if worker1 == 'B' and worker2 == 'B':
#                    worker1 = row[3]
#                    worker2 = row[5]
#                    instance_matrix[worker1][worker2] += 1

            elif not row[0]:
                count += 1
            if count == 700:
                break
    except csv.Error, e:
        sys.exit("File {}, line {}: {}".format(src, reader, e))
    return instance_matrix

def write_eval_file(src):
    count = 0
    w1b = ''
    w2b = ''
    reader = csv.reader(open(src, 'U'), delimiter=',')
    for row in reader:
        if row[0].startswith('OC'):
            if row[2] == 'B':
                worker1 = row[2] + '-' + row[3]
                w1b = row[3]
            elif row[2] == 'I':
                worker1 = row[2] + '-' + w1b
            else:
                worker1 = 'O'
                w1b = ''

            if row[4] == 'B':
                worker2 = row[4] + '-' + row[5]
                w2b = row[5]
            elif row[4] == 'I':
                worker2 = row[4] + '-' + w2b
            else:
                worker2 = 'O'
                w2b = ''

            print worker1 + '\t' + worker2

        elif row[0] == '':
            count += 1
            w1b = ''
            w2b = ''
            if count >= 701:
                break
            print

if __name__ == '__main__':
    #k = Kappa()
    #k.calc('../worker1and2.utf8.csv')
    #write_eval_file('worker1and2.utf8.csv')

    csv_file = '../worker1and2.utf8.csv'
    matrix = csv2dict(csv_file)
    k = Kappa(matrix)
    k.calc()

    #k.calc('../worker1and2.utf8.csv')
