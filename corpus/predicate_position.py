#! /usr/bin/python
# -*- coding: utf-8 -*-

# 述語の位置を調べる
# アノテーションデータと拡張モダリティタグでどれだけずれがあるか
# ・数を調べる
# ・ブラウザで状況を確認する
# ・不一致だけを表示する

header = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"/>
    <title>Position of Predicates</title>
    <style>
        body {
            padding: 20px;
            font-size: 14px}
        table {
            border-left: 1px solid #dddddd;
            border-right: 1px solid #dddddd;
            border-bottom: 1px solid #dddddd;
            border-collapse: collapse;
            }

        th, td {
            padding: 5px;
            text-align: left;
            border-bottom: 1px solid #dddddd;
        }
        th {
            border-top: 1px solid #dddddd;
        }

        table tr:nth-child(even) {
            background-color: #eee;
        }
        table tr:nth-child(odd) {
            background-color: #fff;
        }
        .oe {background: linear-gradient(transparent 50%, #FF0081 50%);}
        .ae {background: linear-gradient(#ff0 50%, transparent 50%);}
        .label {
            position: fixed !important;
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 10px;
            background-color: rgba(255,255,255,0.5);
            border: 2px #000 solid;
        }
    </style>
</head>
<body>
    <div class="label">
        <span class="oe">　　</span>　拡張モダリティの事象 <br/>
        <span class="ae">　　</span>　アノテーションされた事象
    </div>
    <table>
        <tr>
            <th>sentence id</th>
            <th>content</th>
        </tr>
"""

footer = """
</body>
</html>"""

import os

class Morph:
    def __init__(self, line):
        fields = line.split('\t')
        self.sem = fields[0]
        self.morph = fields[1]

    def __str__(self):
        return '\t'.join((self.sem, self.morph))

class Sentence:
    def __init__(self):
        self.morphs = []
        self.oe = [] # original event
        self.ae = [] # annotated event

    def get_annotated_event(self):
        for i, morph in enumerate(self.morphs):
            if morph.sem == 'C':
                self.ae.append(i)

    def underline(self, str):
        return '<u>' + str + '</u>'

    def mark(self, str):
        return '<mark>' + str + '</mark>'

    def italic(self, str):
        return '<i>' + str + '</i>'

    def isoe(self, str):
        return '<span class="oe">' + str + '</span>'

    def isae(self, str):
        return '<span class="ae">' + str + '</span>'

    def decorate(self):
        for i in self.oe:
            self.morphs[i].morph = self.isoe(self.morphs[i].morph)
        for j in self.ae:
            self.morphs[j].morph = self.isae(self.morphs[j].morph)
        for i, morph in enumerate(self.morphs):
            if morph.sem.startswith(('B','I')):
                self.morphs[i].morph = self.italic(self.morphs[i].morph)


    def event_mismatch(self):
        self.get_annotated_event()
        if self.oe == self.ae:
            return False
        else:
            self.decorate()
            return True

    def __str__(self):
        return ''.join([x.morph for x in self.morphs])


def main():
    print header
    for file in os.listdir('data/JFEcorpus_ver2.1/'):
        S = Sentence()
        for line in open('data/JFEcorpus_ver2.1/' + file):
            line = line.strip('\n')
            if line.startswith('#'):
                event_id = int(line.split('\t')[1])
                S.oe.append(event_id)
            elif line.startswith(('*', 'EOS')):
                continue
            else:
                S.morphs.append(Morph(line))
        if S.event_mismatch():
            print '<tr><td>%s</td><td>%s</td></tr>' % (file, str(S))
    print footer

if __name__ == '__main__':
    main()
