#!/usr/bin/env python
# encoding: utf-8
"""
This is a mini demo of how to use numpy arrays and plot data.
NOTE: the operators + - * / are element wise operation. If you want
matrix multiplication use ‘‘dot‘‘ or ‘‘mdot‘‘!
"""
import numpy as np
from numpy import dot
from numpy.linalg import inv
import matplotlib.pyplot as plt
import functools
import util
from mpl_toolkits.mplot3d.axes3d import Axes3D


# 3D plotting
###############################################################################
# Helper functions
def mdot(*args):
    """Multi argument dot function. http://wiki.scipy.org/Cookbook/MultiDot"""
    return functools.reduce(np.dot, args)


def prepend_one(X):
    """prepend a one vector to X."""
    return np.column_stack([np.ones(X.shape[0]), X])


def quad_features(X):
    new_row_vecs = []
    for row_vec in X:
        new_row_vec = row_vec.copy()
        for i, item1 in enumerate(row_vec):
            for item2 in row_vec[i:]:
                new_row_vec = np.append(new_row_vec, item1 * item2)
        new_row_vecs.append(new_row_vec)
    return np.asarray(new_row_vecs)


def grid2d(start, end, num=50):
    """Create an 2D array where each row is a 2D coordinate.
    np.meshgrid is pretty annoying!
    """
    dom = np.linspace(start, end, num)
    X0, X1 = np.meshgrid(dom, dom)
    return np.column_stack([X0.flatten(), X1.flatten()])


def split_set(k, X, y):
    test_sets = []
    test_values = []
    training_sets = []
    training_values = []
    set_size = int(len(X) / k)
    for i in range(k):
        X_temp = list(X)
        y_temp = list(y)
        test_sets.append(X_temp[i * set_size:(i + 1) * set_size])
        test_values.append(y_temp[i * set_size:(i + 1) * set_size])
        for j in range(i * set_size, (i + 1) * set_size):
            X_temp.pop(i * set_size)
            y_temp.pop(i * set_size)
        training_sets.append(X_temp)
        training_values.append(y_temp)
    return training_sets, training_values, test_sets, test_values


def cross_validation(k, data, values, lambda_):
    training_sets, training_values, test_sets, test_value = split_set(
        k, data, values)
    dim = data.shape[1]
    squared_error = 0
    for i, xlist in enumerate(training_sets):
        X = np.asarray(xlist)
        beta_ = mdot(
            inv(dot(X.T, X) + lambda_ * np.identity(dim)), X.T,
            training_values[i])
        for j, vec in enumerate(test_sets[i]):
            squared_error += (dot(vec, beta_) - test_value[i][j])**2
    return squared_error / k


###############################################################################
# load the data
# a)
# data = np.loadtxt("dataLinReg2D.txt")
# b)
# data = np.loadtxt("dataQuadReg2D.txt")
# c)
data = np.loadtxt("data.csv", delimiter=",")

print("data.shape:", data.shape)
# np.savetxt("tmp.txt", data)  # save data if you want to
# split into features and labels
X, y = data[:, :4], data[:, 4]
print("X.shape:", X.shape)
print("y.shape:", y.shape)

# b)
X = quad_features(X)
X = prepend_one(X)
dim = X.shape[1]

# cross_validation(5, X, y, lambda_)
print("X.shape:", X.shape)
# Fit model/compute optimal parameters beta

# a)
lambda_ = 0.1

# c)
h = np.linspace(-10, 10, 801)
squared_error_cv = []
squared_training_error = []
optimal_lambda = h[0]
opt_error = float('inf')
for j in h:
    lambda_ = 10**j
    beta_ = mdot(inv(dot(X.T, X) + lambda_*np.identity(dim) ), X.T, y)
    # training error on all data
    squared_training_error.append(sum([ ( y[i] - dot(X[i], beta_) )**2 for i in range(X.shape[0])]))
    # mean squared error from cross-validation
    squared_error_cv.append(cross_validation(5, X, y, lambda_))
    if squared_error_cv[-1] < opt_error:
        optimal_lambda = lambda_
        opt_error = squared_error_cv[-1]
# plt.plot(h, squared_training_error, label="training error on full data")
plt.plot(h, squared_error_cv, label="mean CV error")
plt.legend()
plt.show()
print(X)
print("Squared Error: ", squared_error_cv)
print ("optimal lambda:", optimal_lambda)
print ("best error:", opt_error)
lambda_ = optimal_lambda

beta_ = mdot(inv(dot(X.T, X) + lambda_*np.identity(dim) ), X.T, y)
print("Optimal beta:", beta_)

#prediction
X = util.read_csv("pred.csv")
preds = []
for row in X:
    x = row[1:]
    x = np.array(x)
    x = x.astype(float)
    x = quad_features([x]).flatten()
    x = np.insert(x, 0, 1.0)
    pred = np.dot(beta_, x)
    preds.append([row[0], pred])
sorted_preds= sorted(preds, key=lambda x: x[1])
print(sorted_preds)