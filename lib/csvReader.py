#! /usr/bin/python
# -*- coding: utf-8 -*-

""""csv reader for annotated file.

This module reads annotated csv file via csv module. For line in the csv, reader
tries to decode line from sjis to unicode, and yields surface, annotated tags of
morphemes. If null line, reader yields [0,0,0].
"""

__author__ = "Yudai Kamioka <yudai.k@ecei.tohoku.ac.jp>"
__date__ = "22 July, 2014"

import csv

def read_csv(csv_file):
    """Read csv_file labeling predicates 'O', and yield them in list."""
    reader = csv.reader(open(csv_file, 'U'), delimiter=',')
    current_tag = ''
    try:
        for row in reader:
            row = [unicode(item, 'sjis') for item in row]
            if row[2] == 'B':
                current_tag = row[3]
            elif row[2] == 'I' and row[3] == '':
                row[3] = current_tag
            else:
                current_tag = ''
                row[2] = 'O'
                row[3] = ''

            if row[0] == '':
                yield ['','','','']
            else:
                #print '\t'.join(row[1:4])
                yield row[0:4]
    except csv.Error, e:
        sys.exit('FILE {}, line {}: {}'.format(csv_file, reader, e))

def read_csv_cbio(csv_file):
    """Read csv_file labeling predicates 'C', and yield them in list."""
    reader = csv.reader(open(csv_file, 'U'), delimiter=',')
    current_tag = ''
    try:
        for row in reader:
            row = [unicode(item, 'sjis') for item in row]
            if row[2] == 'B':
                current_tag = row[3]
            elif row[2] == 'I' and row[3] == '':
                row[3] = current_tag
            elif row[2] == 'C':
                current_tag = ''
                row[2] = 'C'
                row[3] = ''
            else:
                current_tag = ''
                row[2] = 'O'
                row[3] = ''

            if row[0] == '':
                yield ['','','','']
            else:
                #print '\t'.join(row[1:4])
                yield row[0:4]
    except csv.Error, e:
        sys.exit('FILE {}, line {}: {}'.format(csv_file, reader, e))
