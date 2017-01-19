from numpy import *

w = ones([3, 4])
print w[0, 1:3]

for i in w:
    print i

a = mat([[1, 2, 3], [3, 2, 1]])
b = mat([[4, 5, 6], [4, 5, 6]])
print hstack([a, b])
print
p = 1
q = 111
print max([p, q])

instance = zeros([1, p + 1])[0, :]  # t-p,...,t-2,t-1,t
cc = instance
cc[0] = 112
print instance, cc

print identity(3)
