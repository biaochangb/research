__author__ = 'ustc'

import scipy.spatial

from dataset import *


def myprint(ss):
    global gc
    gc = ss
    print 'test', ss


gY_D = []
gsimilarty_y_d = []
gdelta = []
grow_sum_w = []
gw = []
gx = []
gm = 0
gc = 0


def calculateGradient(d):
    global gY_D, gsimilarty_y_d, gc, gdelta, gm, grow_sum_w, gw, gx
    Y_D = gY_D
    similarty_y_d = gsimilarty_y_d
    c = gc
    delta = gdelta
    m = gm
    row_sum_w = grow_sum_w
    w = gw
    x = gx

    column = x[:, d].reshape(m, 1)
    kernel = scipy.spatial.distance.cdist(column, column, 'sqeuclidean')
    wij_d = w * kernel / (delta[d] ** 3)
    row_sum_wij_d = wij_d.sum(axis=1)
    smoothness = wij_d * similarty_y_d  # multiply element-by-element
    loss_d = smoothness.sum()
    # print loss_d[d]
    # print threading.currentThread().getName(),'\t',time.time()
    for i in range(m):
        for j in range(m):
            t = 0
            for k in range(c):
                # print 'dddd',Y_D[i][k],Y_D[j][k]
                t += (Y_D[i][k] - Y_D[j][k]) * (
                    -Y_D[i][k] / row_sum_w[i] * row_sum_wij_d[i] + Y_D[j][k] / row_sum_w[j] * row_sum_wij_d[j])
            loss_d += w[i][j] * t
            # print loss_d[d]
    del kernel, wij_d, smoothness
    return loss_d


def calculateGradient2(Y_D, similarty_y_d, c, delta, m, row_sum_w, w, x, d):
    column = x[:, d].reshape(m, 1)
    kernel = scipy.spatial.distance.cdist(column, column, 'sqeuclidean')
    wij_d = w * kernel / (delta[d] ** 3)
    row_sum_wij_d = wij_d.sum(axis=1)
    loss_d = (wij_d * similarty_y_d).sum()  # # multiply element-by-element and then sum
    for k in range(c):
        column = Y_D[:, k].reshape(m, 1)
        y_d_k_distance = scipy.spatial.distance.cdist(column, column, lambda u, v: (u - v).sum())
        column = (Y_D[:, k] * row_sum_wij_d / row_sum_w).reshape(m, 1)
        y_d_k_distance_normalized = scipy.spatial.distance.cdist(column, column, lambda u, v: (-u + v).sum())
        loss_d += (y_d_k_distance * y_d_k_distance_normalized).sum()
    del kernel, wij_d
    return loss_d


def calculateGradient3(d):
    global gY_D, gsimilarty_y_d, gc, gdelta, gm, grow_sum_w, gw, gx
    Y_D = gY_D
    similarty_y_d = gsimilarty_y_d
    c = gc
    delta = gdelta
    m = gm
    row_sum_w = grow_sum_w
    w = gw
    x = gx

    column = x[:, d].reshape(m, 1)
    kernel = scipy.spatial.distance.cdist(column, column, 'sqeuclidean')
    wij_d = w * kernel / (delta[d] ** 3)
    row_sum_wij_d = wij_d.sum(axis=1)
    loss_d = (wij_d * similarty_y_d).sum()  # # multiply element-by-element and then sum
    for k in range(c):
        column = Y_D[:, k].reshape(m, 1)
        y_d_k_distance = scipy.spatial.distance.cdist(column, column, lambda u, v: (u - v).sum())
        column = column * row_sum_wij_d.reshape(m, 1) / row_sum_w.reshape(m, 1)
        y_d_k_distance_normalized = scipy.spatial.distance.cdist(column, column, lambda u, v: (-u + v).sum())
        loss_d += (y_d_k_distance * y_d_k_distance_normalized).sum()
    del kernel, wij_d
    return loss_d


def calculateGradient4(Y_D, similarty_y_d, c, delta, m, row_sum_w, w, x, d):
    column = x[:, d].reshape(m, 1)
    kernel = scipy.spatial.distance.cdist(column, column, 'sqeuclidean')
    wij_d = w * kernel / (delta[d] ** 3)
    row_sum_wij_d = wij_d.sum(axis=1)
    smoothness = wij_d * similarty_y_d  # multiply element-by-element
    loss_d = smoothness.sum()
    # print loss_d[d]
    # print threading.currentThread().getName(),'\t',time.time()
    for i in range(m):
        for j in range(m):
            t = 0
            for k in range(c):
                # print 'dddd',Y_D[i][k],Y_D[j][k]
                t += (Y_D[i][k] - Y_D[j][k]) * (
                    -Y_D[i][k] / row_sum_w[i] * row_sum_wij_d[i] + Y_D[j][k] / row_sum_w[j] * row_sum_wij_d[j])
            loss_d += w[i][j] * t
            # print loss_d[d]
    del kernel, wij_d, smoothness
    return loss_d


def calculateGradient5(Y_D, similarty_y_d, c, delta, m, row_sum_w, w, x, d):
    column = x[:, d].reshape(m, 1)
    kernel = scipy.spatial.distance.cdist(column, column, 'sqeuclidean')
    wij_d = w * kernel / (delta[d] ** 3)
    row_sum_wij_d = wij_d.sum(axis=1)
    smoothness = wij_d * similarty_y_d  # multiply element-by-element
    loss_d = smoothness.sum()
    # print loss_d[d]
    # print threading.currentThread().getName(),'\t',time.time()
    for i in range(m):
        for j in range(m):
            t = 0
            row1 = Y_D[i] - Y_D[j]
            row2 = -Y_D[i] * row_sum_wij_d[i] / row_sum_w[j] - Y_D[j] * row_sum_wij_d[j] / row_sum_w[j]
            loss_d += (row1 * row2).sum()
            # for k in range(c):
            #     #print 'dddd',Y_D[i][k],Y_D[j][k]
            #     t += (Y_D[i][k] - Y_D[j][k]) * (
            #         -Y_D[i][k] / row_sum_w[i] * row_sum_wij_d[i] + Y_D[j][k] / row_sum_w[j] * row_sum_wij_d[j])
            # loss_d += w[i][j] * t
            # print loss_d[d]
    del kernel, wij_d, smoothness
    return loss_d
