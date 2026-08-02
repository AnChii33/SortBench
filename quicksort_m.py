# Python program for implementation of Quicksort Sort
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
    
# Function to find the partition position
def partition(array, low, high, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    # choose the rightmost element as pivot
    pivot = array[high]

    # pointer for greater element
    i = low - 1

    # traverse through all elements
    # compare each element with pivot
    
    for j in range(low, high):
        if default_timer() - start > maxtime:
            raise SystemError
        
        if array[j] <= pivot:

            # If element smaller than pivot is found
            # swap it with the greater element pointed by i
            i = i + 1

            # Swapping element at i with element at j
            (array[i], array[j]) = (array[j], array[i])
            
            # print()
            # print(array, end="\n\n")
    
    # Swap the pivot element with the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    
    # print()
    # print(array, end="\n\n")
    # Return the position from where partition is done
    return i + 1

# function to perform quicksort


def quicksort_m(array, low, high, start, maxtime):
    if default_timer() - start > maxtime:
        raise SystemError
    
    if not chkSorted(array, low, high, start, maxtime):

        # Find pivot element such that
        # element smaller than pivot are on the left
        # element greater than pivot are on the right
        pi = partition(array, low, high, start, maxtime)

        # Recursive call on the left of pivot
        quicksort_m(array, low, pi - 1, start, maxtime)

        # Recursive call on the right of pivot
        quicksort_m(array, pi + 1, high, start, maxtime)




