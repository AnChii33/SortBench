from timeit import default_timer

def bubbleSort(arr, lm, rm, start, maxtime):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if default_timer() - start > maxtime:
                raise SystemError
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if (swapped == False):
            break

