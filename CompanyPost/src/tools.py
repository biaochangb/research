# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/21.
"""
import math

import numpy as npy


def random_sampling_for_multinomial(p):
    """random sampling for Multi(p), and return the index."""
    r = npy.random.multinomial(1, p / npy.sum(p))
    for i in range(len(r)):
        if r[i] == 1:
            break
    return i


def delta_function(x):
    """get the value of delta function at x, which is calculated by f = \prod_i{Gamma(x[i])}/Gamma(sum(x))
    """
    f = 1.0 / math.gamma(npy.sum(x))
    for i in range(0, len(x)):
        f *= math.gamma(x[i])
    return f


def log_delta_function(x):
    """get the log-value of delta function at x, which is calculated by f = \sum_i{log_Gamma(x[i])}-log_Gamma(sum(x))
    """
    f = -math.lgamma(npy.sum(x))
    for i in range(0, len(x)):
        f += math.lgamma(x[i])
    return f
