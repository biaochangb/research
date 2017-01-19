__author__ = 'bchang'
from numpy import *


def divideDataset(x, n, k_fold):
    m, d = shape(x)
    start = m * (k_fold - 1) / n
    end = start + m / n
    training_matrix = delete(x, range(start, end), 0)
    test_matrix = x[start:end, :]
    return training_matrix, test_matrix


def RMSE(predicted, target):
    rmse = sqrt(linalg.norm(predicted - target) ** 2 / len(target))  # root mean square error
    return rmse
