MAXTIME = 300                 # maximum time limit for each sorting algorithm for any given dataset (in secs)

from sys import setrecursionlimit, exit
setrecursionlimit(10**8)

import os
import xlsxwriter
report = xlsxwriter.Workbook("REPORT.xlsx")
ws1 = report.add_worksheet("Total Data")
ws2 = report.add_worksheet("Mean Data")

ws1.write(0, 0, "DATASET")
ws2.write(0, 0, "DATASET")

#-------------------------------------------------------------------------------------------

import csv
record_file = "RECORDS.csv"
report_file1 = "DATA_REPORTS/TOTAL_REPORT.csv"
report_file2 = "DATA_REPORTS/MEAN_REPORT.csv"

record_header = ["ALGORITHM", "DATASET", "FILE SIZE (MB)", "ELEMENTS", "STATE", "ERROR", "SORT", "TIME (SECS)"]
report_header = ["#", "DATASET", "TIME"]
with open (record_file, "w", newline="") as f:
   csvf = csv.writer(f)
   csvf.writerow(record_header)

with open (report_file1, "w", newline="") as f:
   csvf = csv.writer(f)
   csvf.writerow(report_header)

with open (report_file2, "w", newline="") as f:
   csvf = csv.writer(f)
   csvf.writerow(report_header)

#---------------------------------------------------------------------------------------------------

from heapsort import *
from bubble_Sort import *
from insertionSort import *
from selectionsort import *
from mergesort_n import *
from mergesort_m import *
from quicksort_n import *
from quicksort_m import *
from countSort import *
from radixsort import *
from timsort import *
from dichotomysort import *
from filetolist import *
from nearlysort import *
from random import shuffle
from timeit import default_timer
import datetime

now = datetime.datetime.now()
print(now.strftime("\n\n\n\nExecution started on %A, %dth %B %Y, %H:%M:%S"))

prog_start = default_timer()

def checkSorted(vals):
    for i in range(len(vals)-1):
        if vals[i] > vals[i+1]:
            return False
    else:
        return True

def sortvarchk(arr):
    chk = sorted(arr)
    c = 0
    for i in range(len(arr)):
        if arr[i] != chk[i]:
            c += 1
    return c

DATASET = [
        #    ("TestRun.txt", "[5, 1, 4, 2, 3]"),
        #    ("TestRun2.txt", ""),
           ("chess.txt", "Standard Dataset 1 (334 KB)"),
           ("mushroom.txt", "Standard Dataset 2 (557 KB)"),
           ("T10I4D100K.txt", "Standard Dataset 3 (3.7 MB)"), 
           ("pumsb_star.txt", "Standard Dataset 5 (10.7 MB)"),
           ("connect.txt", "Standard Dataset 4 (8.8 MB)"),
           ("Test_Dataset1.txt", "0 to <100K step 0.01*pi shuffled (55.1 MB)"),
           ("pumsb.txt", "Standard Dataset 7 (15.9 MB)"),
           ("T40I10D100K.txt", "Standard Dataset 6 (14.6 MB)"), 
           ("fewUnique.txt", "Very few unique elements (54.3 MB)"),
           ("kosarak.txt", "Standard Dataset 8 (30.5 MB)"),
           ("Test_Dataset2.txt", "random ints and floats b/w (-10000000, 10000000) shuffled (144 MB)"),
        #    ("webdocs.txt", "Standard MEGA Dataset (1.37 GB)")
        ]

STATE = [
    "ORIGINAL", 
    "RANDOM 1", 
    "RANDOM 2", 
    "RANDOM 3", 
    "RANDOM 4", 
    "RANDOM 5", 
    "NEARLY SORTED 1", 
    "NEARLY SORTED 2", 
    "NEARLY SORTED 3", 
    "NEARLY SORTED 4", 
    "NEARLY SORTED 5", 
    "SORTED", 
    "REVERSE SORTED",
    ]

SORTS = [
         ("COUNT SORT", countSort), 
         ("RADIX SORT", radixSort), 
         ("DICHOTOMY SORT (NEW ALGO)", dichotomySort),
         ("HEAP SORT", heapSort),
         ("TIM SORT", timSort),
         ("MERGE SORT (MODIFIED)", mergeSort_m),
         ("MERGE SORT", mergeSort),  
         ("QUICK SORT (MODIFIED)", quicksort_m),
         ("QUICK SORT", quicksort),
         ("INSERTION SORT", insertionsort),
         ("SELECTION SORT", selectionSort),
         ("BUBBLE SORT (MODIFIED)", bubbleSort),
         ]


# READ INPUT FROM FILE
print("\nLOADING DATASET FILES...")

full_dataset = []
try:
    for i in range(len(DATASET)):
        j = 0
        values = []
        vals = []

        print("\nLOADING %s... (%d/%d)" % (DATASET[i][0], i+1, len(DATASET)))
        readtolist(vals, "DATASETS/"+DATASET[i][0])
        print("\nGENERATING STATE %s..."%STATE[j])
        print("TOTAL ELEMENTS:", len(vals))
        print("UNSORTED ELEMENTS:", sortvarchk(vals))
        j += 1
        values.append(vals)
        for _ in range(5):
            print("\nGENERATING STATE %s..."%STATE[j])
            j += 1
            x = vals.copy()
            shuffle(x)
            print("TOTAL ELEMENTS:", len(x))
            print("UNSORTED ELEMENTS:", sortvarchk(x))
            values.append(x)

        for _ in range(5):
            print("\nGENERATING STATE %s..."%STATE[j])
            j += 1
            x = vals.copy()
            nearlySort(x)
            print("TOTAL ELEMENTS:", len(x))
            print("UNSORTED ELEMENTS:", sortvarchk(x))
            values.append(x)

        print("\nGENERATING STATE %s..."%STATE[j])
        j += 1
        x = sorted(vals.copy())
        print("TOTAL ELEMENTS:", len(x))
        print("UNSORTED ELEMENTS:", sortvarchk(x))
        values.append(x)

        print("\nGENERATING STATE %s..."%STATE[j])
        j += 1
        x = sorted(vals.copy(), reverse=True)
        print("TOTAL ELEMENTS:", len(x))
        print("UNSORTED ELEMENTS:", sortvarchk(x))
        values.append(x)
        full_dataset.append(values)
        print("\n\n%s LOADED SUCCESSFULLY!..."%DATASET[i][0])
        print("---------------------------------------------------\n")
        
except KeyboardInterrupt:
    print("\n\tKEYBOARD INTERRUPT !!!!\n")
    print("\n\tLAST STATE: READING DATASET\n")
    exit("\nEXECUTION ABORTED!\n\n")
except MemoryError:
    print("\n\tCouldn't read file !!\n")  
    
readEnd = datetime.datetime.now()
print(readEnd.strftime("\n\nALL DATASETS LOADED SUCCESSFULLY!!... %dth %B %Y, %H:%M:%S\n"))
    

dswr = True


ws1c = 1
ws2c = 1


print("\n\n------------------------- BENCHMARKING SORTING ALGORITHMS -------------------------\n\n")

for k in SORTS:
    rp1_row = 1             # row count of report_file1 (TOTAL_REPORT.csv)
    rp2_row = 1             # row count of report_file2 (MEAN_REPORT.csv)
    ws1r = 1
    ws2r = 1
    sort = k[0]
    ws1.write(0, ws1c, sort)
    ws2.write(0, ws2c, sort)
    print("\n>>  %s" % k[0])
    print("------------------------------------------------------------------\n")
    
    for i in range(len(DATASET)):
        timeset = []
        dataset_path = DATASET[i][0]
        dataset = DATASET[i][0].removesuffix(".txt").upper()
        remark = DATASET[i][1]
        size = round((os.path.getsize("DATASETS/"+dataset_path))/1048576, 3)
        print("\nDATASET:", dataset, "(%s)"%remark)
        print("----------------------------------------------------\n")
        
        for j in range(len(STATE)):
            state = STATE[j]
            error = False
            
            vals = full_dataset[i][j].copy()
            n = len(vals)
            unsorted = sortvarchk(vals)
            ds = ", ".join([dataset, str(n), state])
            if dswr:
                ws1.write(ws1r, 0, ds)

            print("\nSTATE:", state)
            print("--------------------------------------\n")
            
            print("\tELEMENTS:", n)
            print("\n\tUNSORTED ELEMENTS:", unsorted)
            try:

                # print("\nInput:", vals)
                # CORE PROGRAM
                sort_start = datetime.datetime.now()
                print(sort_start.strftime("\n\tSTART: %dth %B %Y, %H:%M:%S"))
                print("\n\tNow running %s on %s (STATE: %s) ....." % (sort, dataset, state))
                start = default_timer()     # START TIMER
                k[1](vals, 0, n-1, start, MAXTIME)
                stop = default_timer() - start      # STOP TIMER
                sort_end = datetime.datetime.now()
                print(sort_end.strftime("\n\tEND: %dth %B %Y, %H:%M:%S"))
                # END CORE PROGRAM
                # print("Output:", vals)

                print("\n\tTime:", stop, "secs") 

                sortchk = checkSorted(vals)
                if sortchk:
                    ws1.write(ws1r, ws1c, stop)                          # log time in wksheet 1
                    with open(report_file1, "a+", newline="") as f:                             # log data in report_file1
                        csvf = csv.writer(f)
                        csvf.writerow([rp1_row, ds, stop])
                    timeset.append(stop)
                else:
                    with open(report_file1, "a+", newline="") as f:
                        csvf = csv.writer(f)
                        csvf.writerow([rp1_row, ds, "", ""])
                rp1_row += 1                             # increment row counter for report_file1
                print("\n\tSORTED:", sortchk)
                
                # WRITE OUTPUT TO FILE
                if size <= 10:
                    output_file = "OUTPUTS/" + "_".join([dataset, 
                                                            "_".join(state.title().split()), 
                                                            "_".join(sort.title().split()), 
                                                            "OUTPUT"
                                                            ]) + ".txt"
                    writetotext(vals, output_file)
                else:
                    output_file = "NA (Content > 10 MB)"
                print("\n\tOUTPUT PATH:", output_file)
                print()
            except KeyboardInterrupt:
                print("\n\tKEYBOARD INTERRUPT !!!!\n")
                print("\n\tLAST STATE: SORTING DATASET\n")
                exit("\nEXECUTION ABORTED!\n\n")
            except Exception as e:
                f = str(e)
                if type(e) == SystemError:
                    f = "Time limit exceeded, (Limit: %d secs)" % MAXTIME
                stop = default_timer() - start
                error = True
                output_file = "NA"
                sortchk = "NA"
                sort_end = datetime.datetime.now()
                print(sort_end.strftime("\n\tEND: %dth %B %Y, %H:%M:%S"))
                print("\n\t!! SORTING FAILED !!")
                print("\n\tException:", type(e), f)
                print("\n")
                with open(report_file1, "a+", newline="") as f:
                        csvf = csv.writer(f)
                        csvf.writerow([rp1_row, ds, "", ""])
                rp1_row += 1  
                

            with open(record_file, "a+", newline="") as f:
                csvf = csv.writer(f)
                csvf.writerow([sort, dataset, size, len(vals), state, error, sortchk, stop])
            
            ws1r += 1                            # increment row ptr in wksheet 1
        
        
        print("\n\t------------------X-------------X-------------X------------------\n\n")

        if dswr:
            ws2.write(ws2r, 0, ", ".join([dataset, str(n)]))

        avgTime = sum(timeset)/len(STATE) if len(STATE) == len(timeset) else ""   # log log(avg dataset time) in wksheet 2
        ws2.write(ws2r, ws2c, avgTime)                                                  # increment row ptr wksheet 2
        ws2r += 1

        with open(report_file2, "a+", newline="") as f:         # log data in report_file2
            csvf = csv.writer(f)
            csvf.writerow([rp2_row, ", ".join([dataset, str(n)]), avgTime])

        rp2_row += 1                        # increment row counter of report_file2

    ws1c += 1             # increment column ptr wksheet 2
    ws2c += 1             # increment column ptr wksheet 2
    dswr = False          # set write dataset as True

    with open(report_file1, "a+", newline="") as f:
        csvf = csv.writer(f)
        csvf.writerow(["", "", "", ""])

    with open(report_file2, "a+", newline="") as f:
        csvf = csv.writer(f)
        csvf.writerow(["", "", "", ""])

    with open(record_file, "a+", newline="") as f:
        csvf = csv.writer(f)
        csvf.writerow([""]*8)


    print("\n ---------------------------------------------------------------------------------")
    print(" ---------------------------------------------------------------------------------\n\n\n")    
    

print("\n----------------------- BENCHMARKING COMPLETED SUCCESSFULLY -----------------------\n")

now = datetime.datetime.now()
print(now.strftime("Execution ended on %A, %dth %B %Y, %H:%M:%S\n\n"))
print("TOTAL EXECUTION TIME:", default_timer() - prog_start, "secs\n\n")
report.close()
print("DATA LOG: >> D:\chatt\Documents\My Coding Haven\Algo Project Report\REPORT.xlsx\n\n\n")
