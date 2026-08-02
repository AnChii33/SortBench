import random

def random_pair(start, end, max_diff):
  while True: 
    x = random.randint(start, end-max_diff-1) 
    y = random.randint(x + 2, end) 
    if 2 < y - x <= max_diff: 
        return (x, y) 

def allNotSame(arr):
    if len(set(arr)) > 1:
       return True
    return False
        

def nearlySort(vals):
    n = len(vals)
    vals.sort()
    if n <= 2:
        return vals
    elif n <= 10:
        id1 = random.randint(0, n-2)
        id2 = random.randint(id1+1, n-1)
        vals[id1], vals[id2] = vals[id2], vals[id1]
        return vals
    trace = []
    max_reps = random.randint(3, 5)
    reps = 0
    while reps <= max_reps:
        t = random_pair(0, n-1, n//2)
        if t not in trace:
            trace.append(t)
            x, y = t
            temp = vals[x:y+1]
            if allNotSame(temp):
                random.shuffle(temp)
                vals[x:y+1] = temp
                reps += 1
    return vals

def sortvarchk(arr):
    chk = sorted(arr)
    c = 0
    for i in range(len(arr)):
        if arr[i] != chk[i]:
            c += 1
    return c




