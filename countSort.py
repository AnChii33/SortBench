from timeit import default_timer

def countSort(input_array, lm, rm, start, maxtime):
    M = max(input_array)
    count_array = [0] * (M + 1)
    for num in input_array:
        if default_timer() - start > maxtime:
            raise SystemError
        count_array[num] += 1

    for i in range(1, M + 1):
        if default_timer() - start > maxtime:
            raise SystemError
        count_array[i] += count_array[i - 1]

    output_array = [0] * len(input_array)
    for i in range(len(input_array) - 1, -1, -1):
        if default_timer() - start > maxtime:
            raise SystemError
        output_array[count_array[input_array[i]] - 1] = input_array[i]
        count_array[input_array[i]] -= 1

    for i in range(len(input_array)):
        if default_timer() - start > maxtime:
            raise SystemError
        input_array[i] = output_array[i]



    

