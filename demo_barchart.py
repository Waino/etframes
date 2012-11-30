#!/usr/bin/python

import matplotlib.pyplot as plt
from numpy.random import *

import etframes


data = uniform(0, 100, 10)

etframes.bar_chart(data, [25, 50, 75])
plt.xticks(range(len(data)))

plt.show()

