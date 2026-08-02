from timeit import default_timer

def merge(arr, l, m, r, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    n1 = m - l + 1
    n2 = r - m
    L = [0] * (n1)
    R = [0] * (n2)

    for i in range(0, n1):
        if default_timer() - start > maxtime:
            raise SystemError
        
        L[i] = arr[l + i]

    for j in range(0, n2):
        if default_timer() - start > maxtime:
            raise SystemError
        
        R[j] = arr[m + 1 + j]

    i = 0    
    j = 0     
    k = l     

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

    while i < n1:
        if default_timer() - start > maxtime:
            raise SystemError
        
        arr[k] = L[i]
        i += 1
        k += 1
    
    while j < n2:
        if default_timer() - start > maxtime:
            raise SystemError
       
        arr[k] = R[j]
        j += 1
        k += 1
 
def mergeSort(arr, l, r, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    if l < r:
        m = l+(r-l)//2
        mergeSort(arr, l, m, start, maxtime)
        mergeSort(arr, m+1, r, start, maxtime)
        merge(arr, l, m, r, start, maxtime)