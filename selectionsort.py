from timeit import default_timer

def selectionSort(array, low, high, start, maxtime):
    high += 1
    for step in range(high):
        if default_timer() - start > maxtime: 
            raise SystemError
        
        min_idx = step
        
        for i in range(step + 1, high):
            if default_timer() - start > maxtime: 
                raise SystemError

            if array[i] < array[min_idx]:
                min_idx = i
         
        (array[step], array[min_idx]) = (array[min_idx], array[step])