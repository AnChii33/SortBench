from timeit import default_timer
MIN_MERGE = 32
  
def calcMinRun(n, start, maxtime): 
    if default_timer() - start > maxtime:
        raise SystemError
    
    r = 0

    while n >= MIN_MERGE: 
        if default_timer() - start > maxtime:
            raise SystemError
        
        r |= n & 1
        n >>= 1

    return n + r 
  
  
def insertionSort(arr, left, right, start, maxtime): 
    if default_timer() - start > maxtime:
        raise SystemError
    
    for i in range(left + 1, right + 1): 
        if default_timer() - start > maxtime:
            raise SystemError
        
        j = i 

        while j > left and arr[j] < arr[j - 1]: 
            if default_timer() - start > maxtime:
                raise SystemError
        
            arr[j], arr[j - 1] = arr[j - 1], arr[j] 
            j -= 1
  

def merge(arr, l, m, r, start, maxtime): 
    if default_timer() - start > maxtime:
        raise SystemError

    len1, len2 = m - l + 1, r - m 
    left, right = [], [] 

    for i in range(0, len1): 
        if default_timer() - start > maxtime:
            raise SystemError
        
        left.append(arr[l + i]) 

    for i in range(0, len2): 
        if default_timer() - start > maxtime:
            raise SystemError
        
        right.append(arr[m + 1 + i]) 
  
    i, j, k = 0, 0, l 

    while i < len1 and j < len2: 
        if default_timer() - start > maxtime:
            raise SystemError
        
        if left[i] <= right[j]: 
            arr[k] = left[i] 
            i += 1
        else: 
            arr[k] = right[j] 
            j += 1
        k += 1

    while i < len1: 
        if default_timer() - start > maxtime:
            raise SystemError
        
        arr[k] = left[i] 
        k += 1
        i += 1

    while j < len2: 
        if default_timer() - start > maxtime:
            raise SystemError
        
        arr[k] = right[j] 
        k += 1
        j += 1
  

def timSort(arr, lm, rm, start, maxtime): 
    if default_timer() - start > maxtime:
        raise SystemError
    
    n = len(arr) 
    minRun = calcMinRun(n, start, maxtime) 

    for Start in range(0, n, minRun): 
        if default_timer() - start > maxtime:
            raise SystemError
        
        end = min(Start + minRun - 1, n - 1) 
        insertionSort(arr, Start, end, start, maxtime) 

    size = minRun 

    while size < n: 
        for left in range(0, n, 2 * size): 
            if default_timer() - start > maxtime:
                raise SystemError

            mid = min(n - 1, left + size - 1) 
            right = min((left + 2 * size - 1), (n - 1)) 

            if mid < right: 
                merge(arr, left, mid, right, start, maxtime) 
  
        size = 2 * size 