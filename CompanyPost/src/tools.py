# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/21.
"""
import math
import random
from ctypes import *

import numpy as npy
import scipy.special

def is_chinese(str):
    return all(u'\u4e00' <= char <= u'\u9fff' for char in str)

def is_english(str):
    return all('a'<= c<= 'z' or  'A'<= c<= 'Z'for c in str)

def random_sampling_for_multinomial(p, n):
    """random sampling for Multi(p), and return the index.
    This method is faster than npy.random.multinomial when len(p) is small.
    """
    p /= sum(p)
    v = random.random()
    if v < p[0]:
        return 0
    for i in range(1, n):
        p[i] += p[i - 1] # cumulative sum of p[:]
        if v < p[i]:
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
    x0 = x[npy.where(x!=0)]
    f = npy.sum(scipy.special.gammaln(x0)) - math.lgamma(npy.sum(x0))
    return f


mytools = cdll.LoadLibrary("F:/changbiao/research/c/DynamicLinkLibrary/bin/Debug/DynamicLinkLibrary.dll")
mytools.getFullConditionalForX.argtypes = [c_int,
                                           c_long,
                                           c_long,
                                           c_int,
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"),
                                           npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS")
                                           ]
mytools.getFullConditionalForX.restype = c_int
mytools.MultinomialSampling.argtypes=[npy.ctypeslib.ndpointer(dtype=npy.float64, ndim=1, flags="C_CONTIGUOUS"), c_int, c_int, c_double]
mytools.MultinomialSampling.restype = c_int

def sampling_x(n, v, tid, delta, gui, beta, hkv, gamma, ev, _lambda, suv):
    """sampling x according to the full conditional distribution, implemented by C"""
    return mytools.getFullConditionalForX(n, v, tid, random.randint(0,10000), delta, gui, beta, hkv, gamma, ev, _lambda, suv)

def multinomial_sampling(p, n):
    return mytools.MultinomialSampling(p,n,1,random.random())