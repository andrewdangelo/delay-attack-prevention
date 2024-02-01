import math
from math import gcd as gcd
from math import lcm as lcm
import numpy as np
import matplotlib.pyplot as plt
#%%
# print minimum w and argmin y0
x, y = 40, 110 # keep-alive interval
gran = 0.1 # granularity
end = math.lcm(x, y) # the end of a cycle
lx = list(np.arange(0, end + gran, x)) # keepalives of x (x always starts at 0)

y0 = -1 # the start time of y
w = -1 # attack window w
for yi in list(np.arange(0, x, gran)): # the start time of y ranges from [0, x)
    ly = list(np.arange(yi, end + gran, y)) 
    l = list(set(lx + ly))
    l.sort()
    temp = 0 # count the attack window
    for i in range(len(l) - 1):
        temp += (l[i + 1] - l[i]) ** 2
    temp /= 2 * end
    # print(temp)
    if w == -1 or w > temp:
        w = temp
        y0 = yi

ly = list(np.arange(y0, end + 0.1, y))
print(w, y0)
# plt.plot(lx, [1] * len(lx), 'bo')
# plt.plot(ly, [0] * len(ly), 'go')
# plt.show()

#%%
# calculate E[w]
x, y = 120, 30 # keep-alive interval
y0 = 45 # the start time of y
gran = 0.1 # granularity
end = math.lcm(x, y) # the end of a cycle
lx = list(np.arange(0, end + gran, x)) # keepalives of x (x always starts at 0)
ly = list(np.arange(y0, end + gran, y))
l = list(set(lx + ly))
l.sort()
w = 0 # expected attack window
w1 = 0 # average 
for i in range(len(l) - 1):
    w += (l[i + 1] - l[i]) ** 2
    w1 += l[i + 1] - l[i]
w /= 2 * end
w1 /= len(l) - 1
print(w, w1)

#%%
# *find all w of every y0 in [0, x), draw w-y0
x, y = 30, 62 # keep-alive interval
gran = 0.1 # granularity
end = math.lcm(x, y) # the end of a cycle
lx = list(np.arange(0, end + gran, x)) # x always starts at 0

y0 = np.arange(0, x + gran, gran) # the start time of y
w = [] # attack window w
for yi in y0: # the start time of y ranges from [0, x)
    ly = list(np.arange(yi, end + gran, y)) 
    l = list(set(lx + ly))
    l.sort()
    temp = 0 # count the attack window
    for i in range(len(l) - 1):
        temp += (l[i + 1] - l[i]) ** 2
    temp /= 2 * end
    w.append(temp)

print(max(w)-min(w))

idx = np.where(y0 == math.gcd(x, y))[0][0]
fw = np.polyfit(y0[0:idx], w[0:idx], 2)

# plt.plot(y0, w, 'go')
# plt.plot(y0[0:idx], np.polyval(fw, y0[0:idx]))
# plt.show()

#%%
# print minimum w and argmin (y0, z0)
x, y, z = 3, 4, 5
gran = 0.1
end = math.lcm(x, y, z)
lx = list(np.arange(0, end + gran, x))

# l0 = np.arange(0, x, gran)
# y0s = z0s = l0
y0s = np.arange(0, math.gcd(x, y), gran)
z0s = np.arange(0, math.gcd(x, z), gran)

y0 = -1
z0 = -1
w = -1
for yi in y0s:
    for zi in z0s:  
        # if abs(zi - yi) % math.gcd(y, z) == 0 or yi == zi:
        #     continue
        ly = list(np.arange(yi, end + gran, y)) 
        lz = list(np.arange(zi, end + gran, z)) 
        l = list(set(lx + ly + lz))
        l.sort()
        temp = 0
        for i in range(len(l) - 1):
            temp += (l[i + 1] - l[i]) ** 2
        temp /= 2 * end
        if w == -1 or w > temp:
            w = temp
            y0 = yi
            z0 = zi

print(x, y, z)
print(w, y0, z0)
#%%
# *find all w of every (y0, z0) in [0, x), draw w-(y0, z0)
x, y, z = 30, 62, 120
gran = 0.1
end = math.lcm(x, y, z)
lx = list(np.arange(0, end + gran, x))

l0 = np.arange(0, x + gran, gran)
# y0 = np.arange(0, math.gcd(x, y), gran)
# z0 = np.arange(0, math.gcd(x, z), gran)
y0 = l0
z0 = l0
w = np.zeros((len(y0), len(z0)))

for i in range(len(y0)):
    yi = y0[i]
    ly = list(np.arange(yi, end + gran, y)) 
    for j in range(len(z0)):  
        zi = z0[j]       
        lz = list(np.arange(zi, end + gran, z)) 
        l = list(set(lx + ly + lz))
        l.sort()
        temp = 0
        for k in range(len(l) - 1):
            temp += (l[k + 1] - l[k]) ** 2
        temp /= 2 * end
        w[i, j] = temp

print((np.max(w)-np.min(w))/np.max(w))

w0 = np.min(w)
idx = np.where(w == w0)
dy = y0[idx[0]] # optimal y0
dz = z0[idx[1]] # optimal z0

# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# Y0, Z0 = np.meshgrid(y0, z0)
# ax.plot_surface(Y0, Z0, w, color = 'lightblue')
# ax.contour(Y0, Z0, w)

# ax = fig.add_subplot()
# ax = fig.add_subplot(211)
# for i in range(len(z0)):
#     ax.plot(y0, w[:, i])
#     ax.set_xlabel('$\delta_1$')

# ax = fig.add_subplot(212)
# for i in range(len(y0)):
#     ax.plot(z0, w[i, :])
#     ax.set_xlabel('$\delta_2$')

# plt.show()

#%%
# prove: bi * y % x = k * g
x, y = 12, 26
g = math.gcd(x, y)
b = list(range(0, int(x/g)))
R = [bi * y % x for bi in b]
print(g)
print(R)

#%%
# test theorem 2
x, y, z = 4, 6, 7
l = math.lcm(x, y, z)
lx = list(np.arange(0, l + x, x))
ly = list(np.arange(0, l + y, y))
lz = list(np.arange(0, l + z, z))
plt.plot(lx, [0] * len(lx), 'ro')
plt.plot(ly, [1] * len(ly), 'bo')
plt.plot(lz, [2] * len(lz), 'go')
plt.xticks(lx)
plt.grid()
plt.show()

#%%
# test theorem 2
t0, t1, t2 = 12,15,30
l = math.lcm(t0, t1, t2)
T1 = list(range(0, l, t1))
R1 = [x % t0 for x in T1]
E1 = [x // t0 for x in T1]
T2 = list(range(0, l, t2))
R2 = [x % t0 for x in T2]
E2 = [x // t0 for x in T2]

l12 = []
for i in set(E1) & set(E2):
    r1 = R1[E1.index(i)]
    r2 = R2[E2.index(i)]
    l12.append((r1, r2))
print('t1, t2: ', l12)

l1 = []
for i in set(E1) - (set(E1) & set(E2)):
    r1 = R1[E1.index(i)]
    l1.append(r1)
print('t1: ', l1)

l2 = []
for i in set(E2) - (set(E1) & set(E2)):
    r2 = R2[E2.index(i)]
    l2.append(r2)
print('t2: ', l2)

#%%
t0, t1, t2 = 6,8,16
g1 = g(t0, t1)
g2 = g(t0, t2)
l1 = l(t0, t1)
l2 = l(t0, t2)
l = l(t0, t1, t2)

p1 = t0 / g1
q1 = l / l1
p2 = t0 / g2
q2 = l / l2

dt1, dt2 = 1, 5

(2*p1*q1 - p1*p2) * dt1 + (2*p2*q2 - p1*p2) * dt2 \
+ (p1*q1 + p2*q2 - 2*q1 - 2*q2 - p1*p2 + p1 + p2) * t0

#%%
t0, t1 = 6, 19
l = math.lcm(t0, t1)
T1 = list(range(0, l, t1))
R1 = [x % t0 for x in T1]
E1 = [x // t0 for x in T1]
