# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 10:31:38 2018

@author: Gimli
"""

import numpy as np

x = np.random.binomial(20, .5, 10000) 
total = len(x)
g15 = [1 if y > 15 else 0 for y in x]
g15 = sum(g15)

print(x)
print(total)
print(g15)

print(g15 / total)

print(np.random.binomial(1000, .5) / 1000)