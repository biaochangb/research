from numpy import *
import dataset as data
# import semi_supervised as ss
#
# dt = data.Dataset()
# #dt.saveKernel()
# model = ss.Algorithm()
#model.sigma(3)
m =2
import scipy.spatial
w = random.rand(m,m)
kernel = random.rand(m,m)
delta = [1,2]
column = w[:,1].reshape(m,1)
print w,column,'w=[0]'
print scipy.spatial.distance.cdist(column, column, lambda u, v: (u-v).sum())
# row_sum_w = w.sum(axis=1)
# print row_sum_w
# print w/row_sum_w
# print scipy.spatial.distance.cdist(w, w, lambda u, v: exp(((u-v)**2).sum()))
# print w.sum()
# print w,kernel,w*kernel
print scipy.spatial.distance.cdist(column,column,'sqeuclidean'), 'scipy.spatial.distance.cdist(w[:][0],w[:][0]'
print scipy.spatial.distance.cdist(w,w,'seuclidean',array([1,2]))
print (scipy.spatial.distance.cdist(w,w)*w).sum(),'sum'

print w
row_sum_w = w.sum(axis=1)   # sum of each row
print row_sum_w,'row_sum_w',column/row_sum_w.reshape(m,1)
for i in range(m):
    row_sum_w[i] = math.pow(row_sum_w[i],-0.5)
print row_sum_w
D = diag(row_sum_w)
print D
S = dot(dot(D, w), D)
print S
print 'sdf'

w = w.__truediv__(D)    # normalize by rows
print w

print '222222222222'
rdm =  mat(random.rand(3,3))
print rdm.I
print rdm.shape

x = array([2,2,3])
y = mat(tile(x,(4,1))).getT()
y = y.sum(axis=1)
print tile(y,(1,4))

z = array([[2,3,1],[3,2,4],[1,4,3],[1,2,4]])
y = ((tile(x,(4,1))-z)**2)
print y
print y.__truediv__(z)

from collections import Counter
cnt = Counter([8.0, 4.0, 4.0, 4.0, 11.0,8.0,2,3,1,3,2,3,4])
print cnt

print random.randint(2,3)

x = mat([[1,2],[2,3]])
y = mat([[2.0,2],[2,3]])
x.I
print x/y
print argsort(-x)

if 4 not in x:
    print 'sdfasdfsdf'

print identity(3)