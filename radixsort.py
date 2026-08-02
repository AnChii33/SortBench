from timeit import default_timer

def countingSort(arr, exp1, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError

    n = len(arr)
    output = [0] * (n)
    count = [0] * (10)

    for i in range(0, n):
        if default_timer() - start > maxtime:
            raise SystemError
        
        index = arr[i] // exp1
        count[index % 10] += 1

    for i in range(1, 10):
        if default_timer() - start > maxtime:
            raise SystemError
        
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        if default_timer() - start > maxtime:
            raise SystemError
        
        index = arr[i] // exp1
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1
        i -= 1

    i = 0
    for i in range(0, len(arr)):
        if default_timer() - start > maxtime:
            raise SystemError
        
        arr[i] = output[i]


def radixSort(arr, lm, rm, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError

    max1 = max(arr)
    exp = 1
    while max1 / exp >= 1:
        if default_timer() - start > maxtime:
            raise SystemError
        
        countingSort(arr, exp, start, maxtime)
        exp *= 10



