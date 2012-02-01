from __future__ import division
from collections import Counter

import random


class MarkovChain(object):
    def __init__(self):
        self._state_tables = []
        self._lengths = None

    def set_state_table(self, tbl, index):
        if len(self._state_tables) <= index:
            for _ in range(len(self._state_tables)-1, index):
                self._state_tables.append([])
        self._state_tables[index] = tbl

    def set_lengths(self, l):
        self._lengths = l

    def _generate(self, length):
        def find_elem(list_, val):
            pos = 0
            while pos < len(list_) - 1:
                if list_[pos][0] > val >= list_[pos + 1][0]:
                    return list_[pos][1]
                pos += 1

            return None

        length = length or random.choice(self._lengths)
        res = [None,]
        while len(res) - 1 < length and res.count(None) <= 1:
            entry = self._state_tables[len(res) - 1]
            res.append(find_elem(entry[res[-1]],
                                 random.random()))
        return ''.join([_ for _ in res if _])

    def iterate(self, length=None):
        while True:
            yield self._generate(length)

    def generate(self, length=None, num_entries=1):
        return [self._generate(length) for _ in range(num_entries)]


class PassStats(object):
    def __init__(self):
        self._stats = []
        self._lens = Counter()

    def _add_char_seq(self, pass_chars, freq):
        pos = 0
        for pair in pass_chars:
            if pos >= len(self._stats):
                self._stats.append(dict())

            if pair[0] not in self._stats[pos].keys():
                self._stats[pos][pair[0]] = Counter()

            self._stats[pos][pair[0]].update({pair[1]: freq})
            pos += 1

    def add_password(self, new_pass, freq=1):
        pass_chars = [None,] + [_ for _ in new_pass] + [None,]
        self._add_char_seq(zip(pass_chars, pass_chars[1:]), freq)
        self._lens.update({len(new_pass): freq})

    def markov_generator(self, flatten=False):
        def to_cumul(counter):
            total = sum(counter.values())
            res = []
            cumul = 0
            for k, v in counter.items():
                cumul += v
                res.append( (cumul/total, k) )
            return [_ for _ in reversed(res)] + [(0, ''),]

        res = MarkovChain()
        pos = 0

        if not flatten:
            for _ in self._stats:
                tmp = dict(_)

                for k in tmp.keys():
                    tmp[k] = to_cumul(tmp[k])

                res.set_state_table(tmp, pos)
                pos += 1
        else:
            raise NotImplemented("TODO")

        res._lengths = [_ for _ in self._lens.elements()]

        return res

    def load_list(self, infile, filetype='list'):
        if filetype not in ('list', 'freq'):
            raise ValueError()
        if filetype == 'list':
            for line in infile:
                self.add_password(line.rstrip('\n\r'))
        else:
            for line in infile:
                self.add_password(line.split(',', 1)[1],
                                  int(line.split(',', 1)[0]))


if __name__ == '__main__':
    import sys
    ps = PassStats()

    #load a file from stdin or the filename given as an argument
    if len(sys.argv) < 2:
        ps.load_list(sys.stdin, 'list')
    else:
        with open(sys.argv[1], 'r') as indata:
            ps.load_list(indata, 'list')

    m = ps.markov_generator()
    #create 10 passwords from the gathered multi-markov chain
    for _ in zip(range(10), m.iterate()):
        print _

