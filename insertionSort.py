from timeit import default_timer

def insertionsort(arr, lm, rm, start, maxtime):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            if default_timer() - start > maxtime:
                raise SystemError
        
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


