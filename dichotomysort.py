from timeit import default_timer

def average(vals, lmark, rmark, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    s = sum(vals[lmark:rmark+1])
    c = len(vals[lmark:rmark+1])
    return s/c


def swap(vals, lmark, rmark, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    vals[lmark], vals[rmark] = vals[rmark], vals[lmark]


def chkSorted(vals, lmark, rmark, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    for i in range(lmark, rmark):
        if default_timer() - start > maxtime:
            raise SystemError
        
        if vals[i] > vals[i+1]:
            return False
    else:
        return True
    
    
def dichotomizer(vals, lmark, rmark, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    threshold = average(vals, lmark, rmark, start, maxtime)
    while lmark <= rmark:
        if default_timer() - start > maxtime:
            raise SystemError
        
        if vals[lmark] <= threshold:
            lmark += 1
        elif vals[rmark] >= threshold:
            rmark -= 1
        else:
            swap(vals, lmark, rmark, start, maxtime)
            lmark += 1
            rmark -= 1
    else:
        return rmark


def dichotomySort(vals, lmark, rmark, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    if not chkSorted(vals, lmark, rmark, start, maxtime):
        splitIndex = dichotomizer(vals, lmark, rmark, start, maxtime)
        dichotomySort(vals, lmark, splitIndex, start, maxtime)
        dichotomySort(vals, splitIndex+1, rmark, start, maxtime)
        


