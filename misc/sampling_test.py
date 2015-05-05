#! /usr/bin/python
# -*- coding: utf-8 -*-

import random

def sampling(U, N):
    "sampling N instances from U"
    for i in xrange(N):
        index = random.randint(N, len(U)-1)
        U[i], U[index] = U[index], U[i]
    return sorted(U[:N])

if __name__ == '__main__':
    print sampling(range(20), 10)
