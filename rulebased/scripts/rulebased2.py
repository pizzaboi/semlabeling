#! /usr/bin/python
#-*- coding: utf-8 -*-

__LABEL_ver2_1__ = ('判断','否定','疑問','推量-不確実','推量-高確実性',
'否定推量','意志','願望','当為','不可避','依頼','勧誘','勧め','許可','不許可',
'不必要','無意味','可能','不可能','困難','容易','自然発生','自発','無意志',
'試行','伝聞','回想','継続','着継続','発継続','最中','傾向','事前','完了',
'事後','結果状態','習慣','反復','経歴','方向','授与','受益','受身','使役',
'付帯-続行','付帯-並行','同時性','継起','終点','相関','対比','添加','比較',
'場合','順接仮定','順接確定','逆接仮定','逆接確定','理由','目的','並立',
'例示','様態','比況','程度','強調','感嘆','態度','内容','名詞化','話題')

class Morph:
    def __init__(self, line):
        self.__tag     = None
        self.__surface = None
        self.__feature = None
        self.set_line(line)

        self.__ttjsurface  = []
        self.__defined_tag = None
        self.__candidates  = []

    def set_line(self, line):
        line = line.split("\t")
        self.__tag     = line[0]
        self.__surface = line[1]
        self.__feature = line[2]

    def tag(self):
        return self.__tag

    def surface(self):
        return self.__surface

    def feature(self):
        return self.__feature

    def candidates(self):
        return self.__candidates

    def ttjsurface(self):
        return self.__ttjsurface

    def defined_tag(self):
        return self.__defined_tag

    def is_fe(self):
        return bool(self.__tag.startswith(("B", "I")))

    def add_candidate(self, cand):
        self.__candidates.append(cand)

    def is_tagged(self):
        return bool(self.__defined_tag)

    def set_ttjsurface(self, ttjsurface):
        self.__ttjsurface = ttjsurface

    def define_as_begin(self, sem):
        self.__defined_tag = "B-{}".format(sem)

    def define_as_inner(self, sem):
        self.__defined_tag = "I-{}".format(sem)

    def define_as_multi(self, sem):
        self.__defined_tag += "," + sem

    def __str__(self):
        return '%s\t%s\t' % (self.tag, self.surface)

    def __repr__(self):
        res = self.__defined_tag if self.__defined_tag else "O"
        #return self.__surface +"\t" + self.__tag + "\t" + res + "\t" + "/".join([x[0] for x in self.__candidates])
        return self.__tag + "\t" + res

## Class for rulebased tagger.
class RulebasedTagger:
    def __init__(self, S):
        self.sentence = S

    ## surround_match() is True <=> all tokes in seq matches in surface.
    ## param i   : current index in sentence 
    ## param seq : surrounding
    def surround_match(self, i, seq):
        for token in seq:
            if not token:
                break
            offset = int(token.split(':')[0])
            if not (i + offset) < len(self.sentence):
                return False
            elif self.sentence[i + offset].surface() != token.split(':')[1]:
                return False
        return True

    ## comp_rule(r1, r2) is True <=> r1 > r2.
    ## param r1 : connect rule
    ## param r2 : connect rule
    def comp_rule(self, r1, r2):
        r1 = r1.split(',')
        r2 = r2.split(',')
        for i in xrange(len(r1) - 2):
            if r1[i] != '*' and r1[i] != r2[i]:
                return False
        return True

    ## connect_match() is True <=> ttj satisfies connect rule.
    ## param i   : current index in sentence
    ## param ttj :
    def connect_match(self, i, ttj):
        ttj_id, ttj_surface = ttj.split(':')
        ttj_id = ttj_id.replace('.', '')
        connect_rules = CR.get(ttj_id)
        if not connect_rules:
            return True
        for rule in connect_rules.split(';'):
            if self.comp_rule(rule, self.sentence[i-1].feature()):
                return True
        #print connect_rules
        return False

    ## Extract semantics label.
    def sem_filter_01(self, sec):
        data = sec.split(':')
        if data[0].startswith('I1'): return '推量-不確実'
        elif data[0].startswith('I2'): return '推量-高確実性'
        elif data[0].startswith('I3'): return '完了' #'反実'
        elif data[0].startswith('J1'): return '進行-習慣'
        elif data[0].startswith('J2'): return '進行-慣習'
        elif data[1] == '無視': return '想外'
        elif data[0].startswith('v1'): return '付帯-続行'
        elif data[0].startswith('v2'): return '付帯-並行'
        elif data[0].startswith('w3'): return '疑問' #'感嘆-確認'
        elif data[0].startswith('x3'): return '疑問' #'疑問-確認'
        elif data[0].startswith('K3'): return '依頼'
        else: return data[1]

    def sem_filter_02(self, sec):
        if sec == '限定':
            return '程度'
        elif sec in __LABEL_ver2_1__:
            return sec
        else:
            return False

    def set_candidates(self):
        s = self.sentence
        for i in xrange(len(s)):

            # 機能表現の位置を教えるかどうか
            if not s[i].is_fe():
                continue

            entries = FE.get(s[i].surface())

            if not entries:
                continue

            for entry in entries.split('/'):
                seq = entry.split(',')
                sec = seq.pop(0)
                ttj = seq.pop(0)

                # Check surroud
                if not self.surround_match(i, seq):
                    continue
                #print 'Sequence Matched: %s' % entry

                # Sem Label Filter
                sec = self.sem_filter_01(sec)
                sec = self.sem_filter_02(sec)
                if not sec:
                    continue

                # Check connection
                if not self.connect_match(i, ttj):
                    #print 'Connection Mismatched: %s' % entry
                    continue

                # Add candidate, if surround AND connectoin matched
                
                s[i].add_candidate((ttj.split(':')[1], sec))

    def longest_match(self):
        cur = ''
        S = self.sentence
        for i, morph in enumerate(S):
            if not morph.is_tagged(): # タグが未付与のとき
                max_len = 0
                for field in morph.candidates():
                    
                    ttj = field[0].split('.')
                    if len(ttj) >= max_len: # さらに長い表現のとき
                        morph.set_ttjsurface(ttj)

                        if not FQ.has_key(field[0]):
                            morph.define_as_begin(field[1])
                        else:
                            morph.define_as_begin(FQ[field[0]])

                        max_len = len(ttj) # 最長更新
                        cur = morph.defined_tag().split('-', 1)[1]

                        ## 2語以上のとき、続く表現も更新する
                        if max_len >= 2:
                            for k, v in enumerate(morph.ttjsurface()):
                                if k != 0:
                                    S[i + k].define_as_inner(field[1])
            else:
                morph.define_as_inner(cur)

    def longest_match_multi(self):
        cur = ''
        S = self.sentence
        for i, morph in enumerate(S):
            if not morph.is_tagged():
                max_len = 0
                for field in set(morph.candidates()):
                    ttj = field[0].split('.')

                    if len(ttj) >= max_len:
                        morph.set_ttjsurface(ttj)
                        if len(ttj) > max_len:
                            morph.define_as_begin(field[1])
                            if len(ttj) >= 2:
                                for k, v in enumerate(morph.ttjsurface()):
                                    if k != 0:
                                        S[i + k].define_as_inner(field[1])
                            max_len = len(ttj)
                        elif len(ttj) == max_len:
                            morph.define_as_multi(field[1])
                            if max_len >= 2:
                                for k, v in enumerate(morph.ttjsurface()):
                                    if k != 0:
                                        S[i + k].define_as_multi(field[1])
                    cur = morph.defined_tag().split("-", 1)[1]
            else:
                morph.define_as_inner(cur)

    ## Run tagger.
    def tagger(self, multi=False):
        self.set_candidates()
        if multi:
            self.longest_match_multi()
        else:
            self.longest_match()
        return self.sentence

## Convert cabocha format to morph sequence.
def encode_sentence(src):
    S = []
    for line in open(src):
        line = line.strip('\n')
        if not line.startswith(('#', '*', 'EOS')):
            S.append(Morph(line))
    return S

def test():
    import os
    #srcs = [f for f in os.listdir(args.corpus) if f != '.DS_Store']
    src='data/JFEcorpus_ver2.1/OC15_00907m_004.depmod'
    S = encode_sentence(src)
    rt = RulebasedTagger(S)
    for morph in rt.tagger(True):
        print repr(morph)
    #rt.print_label()

def main():
    import os
    corpus = 'data/JFEcorpus_ver2.1/'
    #corpus = '700/tmp/'
    for src in [f for f in os.listdir(corpus) if f != '.DS_Store']:
        S = encode_sentence(corpus  + src)
        rt = RulebasedTagger(S)
        res = rt.tagger()
        for morph in res:
            print repr(morph)
        print

if __name__ == '__main__':
    import Mostfreq
    import Kyotocabinet
    FE = Kyotocabinet.read_db('rulebased/fe_dict.kch')
    #FE = Kyotocabinet.read_db('../ttj_dict.kch')
    CR = Kyotocabinet.read_db('rulebased/cr_dict.kch')
    #CR = Kyotocabinet.read_db('../cr_dict_for_multi.kch')

    import freq
    counter = freq.CorpusCounter()
    FQ = counter.frequent_tags("data/JFEcorpus_ver2.1/")

    #test()
    main()
