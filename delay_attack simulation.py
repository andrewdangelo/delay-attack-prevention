import math, random
import numpy as np
import matplotlib.pyplot as plt
#%% orchestrate1
# print {delta: avg[w]}, fixed attack time
t0, t1 = 40, 110
delta_num = 5 # including delta0
atk_num = 50

def cal_w(t0, t1, delta_num, atk_num):
    g = math.gcd(t0, t1)
    l = math.lcm(t0, t1)
    gran = 0.1
    atk = list(np.random.uniform(0, l, atk_num)) # [0, l)
    d = {}
    
    # deltas = [g/2] + random.sample(sorted(set(np.arange(0, t0, gran)) - set(np.arange(g/2, t0, g))), delta_num)
    # deltas = [int(g/2)] + random.sample(sorted(set(range(t0)) - set(range(int(g/2), t0, int(g)))), delta_num) # int    
    # deltas = [g/2] + random.sample(list(np.arange(0, g/2, gran)), delta_num) # select from 0-g/2
    deltas = [int(g/2)] + random.sample(list(range(int(g/2))), delta_num) # select int from 0-g/2
    
    for delta in deltas:
        T0 = list(np.arange(0, l+gran, t0))
        T1 = list(np.arange(delta, l+gran, t1))
        T = list(set(T0 + T1))
        T.sort()
        w = 0
        # atk = list(np.random.uniform(0, l, atk_num)) # [0, l)
        for t in atk:
            wt = 0
            for i, ti in enumerate(T):
                if ti < t:
                    continue
                elif ti == t:
                    wt = T[i+1] - t
                    break
                else:
                    wt = ti - t
                    break
            w += wt
        w /= atk_num
        d[round(delta, 2)] = round(w, 2)
        # d[delta] = round(w, 2) # int
    return d

print(cal_w(t0, t1, delta_num, atk_num))

#%% orchestrate2
# print {delta: w of each attack, avg[w]}, fixed attack time
t0, t1 = 40, 110
delta_num = 5 # including delta0
atk_num = 10

def cal_w(t0, t1, delta_num, atk_num):
    g = math.gcd(t0, t1)
    l = math.lcm(t0, t1)
    gran = 0.1
    atk = list(np.random.uniform(0, l, atk_num)) # [0, l)
    d = {}
    
    # deltas = [g/2] + random.sample(sorted(set(np.arange(0, t0, gran)) - set(np.arange(g/2, t0, g))), delta_num)
    # deltas = [int(g/2)] + random.sample(sorted(set(range(t0)) - set(range(int(g/2), t0, int(g)))), delta_num) # int    
    # deltas = [g/2] + random.sample(list(np.arange(0, g/2, gran)), delta_num) # select from 0-g/2
    deltas = [int(g/2)] + random.sample(list(range(g)), delta_num) # select int from 0-g/2
    
    for delta in deltas:
        T0 = list(np.arange(0, l+gran, t0))
        T1 = list(np.arange(delta, l+gran, t1))
        T = list(set(T0 + T1))
        T.sort()
        d[round(delta, 2)] = []
        # atk = list(np.random.uniform(0, l, atk_num)) # [0, l)
        for t in atk:
            wt = 0
            for i, ti in enumerate(T):
                if ti < t:
                    continue
                elif ti == t:
                    wt = T[i+1] - t
                    break
                else:
                    wt = ti - t
                    break
            d[delta].append(round(wt, 2))
        d[delta].append(round(np.mean(d[delta]), 2))
    return d

print(cal_w(t0, t1, delta_num, atk_num))

#%% orchestrate3
# plot delta-avg[w]
t0, t1 = 60, 120
atk_num = 1000
gran = 0.1

def cal_w(t0, t1, atk_num):
    g = math.gcd(t0, t1)
    l = math.lcm(t0, t1)
    gran = 0.1
    atk = list(np.random.uniform(0, l, atk_num)) # [0, l)
    deltas = list(np.arange(0, 2*g, gran))
    ws = []
    
    for delta in deltas:
        T0 = list(np.arange(0, l+gran, t0))
        T1 = list(np.arange(delta, l+gran, t1))
        T = list(set(T0 + T1))
        T.sort()
        w = 0
        # atk = list(np.random.uniform(0, l, atk_num)) # [0, l)
        for t in atk:
            wt = 0
            for i, ti in enumerate(T):
                if ti < t:
                    continue
                elif ti == t:
                    wt = T[i+1] - t
                    break
                else:
                    wt = ti - t
                    break
            w += wt
        w /= atk_num
        ws.append(w)
    return deltas, ws, g, l

deltas, ws, g, l = cal_w(t0, t1, atk_num)

fig, ax = plt.subplots()
ax.plot(deltas, ws)
ax.set(xlabel='$\delta$', ylabel='w (s)')
ax.set_xticks(np.arange(0, 2*g + gran, g/2))
ax.grid(True)
plt.show()

#%% tunnel1
t0, t1 = 40, 110 # t0 minimum
atk_num = 50
atk_times = 4
gran = 0.1

delta1 = np.random.random() * t0 # t0 + delta1 = t1
l = math.lcm(t0, t1)
T0 = list(np.arange(0, l+gran, t0))
T1 = list(np.arange(delta1, l+gran, t1))
T = list(set(T0 + T1))
T.sort()

ws = []
for i in range(atk_times):    
    w = 0
    atk = list(np.random.uniform(0, l, atk_num))
    for t in atk:
        wt = 0
        for i, ti in enumerate(T):
            if ti < t:
                continue
            elif ti == t:
                wt = T[i+1] - t
                break
            else:
                wt = ti - t
                break
        w += wt
    w /= atk_num
    ws.append(w)

print(ws)

#%% tunnel2
t0, t1, t2, t3, t4, t5 = 31, 40, 90, 105, 110, 242 # 31, 105 on-idle; others fixed; same device: 31/242, 90/105
delta5 = 1 # t0 + delta5 = t5
delta23 = 11 # t2 + delta23 = t3

atk_num = 1000
gran = 0.1

delta1 = np.random.random() * t0
delta2 = np.random.random() * t0
delta3 = delta2 + delta23
delta4 = np.random.random() * t0

# l = math.lcm(t0, t1, t2, t3, t4, t5)
l = 10000
T0 = list(np.arange(0, l+gran, t0))
T1 = list(np.arange(delta1, l+gran, t1))
T2 = list(np.arange(delta2, l+gran, t2))
T3 = list(np.arange(delta3, l+gran, t3))
T4 = list(np.arange(delta4, l+gran, t4))
T5 = list(np.arange(delta5, l+gran, t5))
T = list(set(T0 + T1 + T2 + T3 + T4 + T5))
T.sort()

w_fixed = []
for i in range(4):    
    w = 0
    atk = list(np.random.uniform(0, l, atk_num))
    for t in atk:
        wt = 0
        for i, ti in enumerate(T):
            if ti < t:
                continue
            elif ti == t:
                wt = T[i+1] - t
                break
            else:
                wt = ti - t
                break
        w += wt
    w /= atk_num
    w_fixed.append(w)
    
w_idle_t0 = []
for i in range(2):    
    w = 0
    atk = list(np.random.uniform(0, l, atk_num))
    for t in atk:
        wt = 0
        for i, ti in enumerate(T):
            if not ti in T0:
                if ti < t:
                    continue
                elif ti == t:
                    wt = T[i+1] - t
                    break
                else:
                    wt = ti - t
                    break
        w += min(wt, t0)
    w /= atk_num
    w_idle_t0.append(w)

w_idle_t3 = []
for i in range(2):    
    w = 0
    atk = list(np.random.uniform(0, l, atk_num))
    for t in atk:
        wt = 0
        for i, ti in enumerate(T):
            if not ti in T3:
                if ti < t:
                    continue
                elif ti == t:
                    wt = T[i+1] - t
                    break
                else:
                    wt = ti - t
                    break
        w += min(wt, t3)
    w /= atk_num
    w_idle_t3.append(w)

print('fixed: ', w_fixed)
print('idle_t0: ', w_idle_t0)
print('idle_t3: ', w_idle_t3)