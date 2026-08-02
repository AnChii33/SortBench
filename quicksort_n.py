from timeit import default_timer

def partition(array, low, high, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    pivot = array[high]
    i = low - 1
    for j in range(low, high):
        if default_timer() - start > maxtime:
            raise SystemError
        
        if array[j] <= pivot:
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])

    (array[i + 1], array[high]) = (array[high], array[i + 1])
    return i + 1


def quicksort(array, low, high, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    if low < high:
        pi = partition(array, low, high, start, maxtime)
        quicksort(array, low, pi - 1, start, maxtime)
        quicksort(array, pi + 1, high, start, maxtime)
