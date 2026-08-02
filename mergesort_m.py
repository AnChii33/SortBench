from timeit import default_timer

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

def merge(arr, l, m, r, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    n1 = m - l + 1
    n2 = r - m
 
    # create temp arrays
    L = [0] * (n1)
    R = [0] * (n2)
 
    # Copy data to temp arrays L[] and R[]

    for i in range(0, n1):
        if default_timer() - start > maxtime:
            raise SystemError

        L[i] = arr[l + i]


    for j in range(0, n2):
        if default_timer() - start > maxtime:
            raise SystemError

        R[j] = arr[m + 1 + j]
 
    # Merge the temp arrays back into arr[l..r]
    i = 0     # Initial index of first subarray
    j = 0     # Initial index of second subarray
    k = l     # Initial index of merged subarray


    while i < n1 and j < n2:
        if default_timer() - start > maxtime:
            raise SystemError
        
        if L[i] <= R[j]:
            
            arr[k] = L[i]
            i += 1
        else:
            
            arr[k] = R[j]
            j += 1
        k += 1
 
    # Copy the remaining elements of L[], if there
    # are any
    
    while i < n1:
        if default_timer() - start > maxtime:
            raise SystemError
        
        arr[k] = L[i]
        i += 1
        k += 1
 
    # Copy the remaining elements of R[], if there
    # are any
    
    while j < n2:
        if default_timer() - start > maxtime:
            raise SystemError
       
        arr[k] = R[j]
        j += 1
        k += 1
 
# l is for left index and r is right index of the
# sub-array of arr to be sorted
 
 
def mergeSort_m(arr, l, r, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    if not chkSorted(arr, l, r, start, maxtime):
 
        # Same as (l+r)//2, but avoids overflow for
        # large l and h
        m = l+(r-l)//2
 
        # Sort first and second halves
        mergeSort_m(arr, l, m, start, maxtime)
        mergeSort_m(arr, m+1, r, start, maxtime)
        merge(arr, l, m, r, start, maxtime)
 
 
