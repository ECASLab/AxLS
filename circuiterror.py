import numpy as np
import collections


def extract_numbers(filename):
    '''
    Reads a txt file and returns the list of numbers inside the file

    Parameters
    ----------
    filename : string
        name of the text file to read

    Returns
    -------
    array
        list of numbers of each row of the file
    '''
    result = []
    file = open(filename, 'r')
    rows = file.read().split('\n')
    for row in rows:
        row = row.replace(' ','')
        if row.isdigit():
            result.append(int(row))
    file.close()
    return result


def compute_error(metric, original, approximate):
    '''
    Computes the error between two different testbench output files

    Parameters
    ----------
    metric : string
        equation to measure the error
        options med, wce, wcre,mred, msed
    original : string
        path to the original results text file
    approximate : string
        path to the approximate results text file
    '''

    # Read original output content
    original_output = extract_numbers(original)

    # Read modified output content
    approximate_output = extract_numbers(approximate)

    # compute the error distance ED := |a - a'|
    error_distance = [abs(original_output[x] - approximate_output[x])
        for x in range(0,len(original_output))]

    square_error_distance = [ error_distance[x]**2 for x in range(0,len(error_distance))]

    # compute the relative error distance RED := ED / a
    relative_error_distance = [
        0 if original_output[x] == 0 else error_distance[x]/original_output[x]
        for x in range(0,len(original_output))]


    counter = collections.Counter(error_distance)

    total = sum(counter.values())
    keys = list(counter.keys())
    values = list(counter.values())

    pon_avg = 0
    for x in range (0,len(counter.keys())):
        per = round(values[x]/total,6)
        pon_avg += (int(keys[x]) * per)

    # Error Rate:
    if (metric == "er"):
        return round(sum((error>0 for error in error_distance))/total,3)

    # Mean Hamming Distance see: https://stackoverflow.com/questions/40875282/fastest-way-to-get-hamming-distance-for-integer-array
    if (metric == "hd"):
        hamming_distance=np.bitwise_xor(original_output,approximate_output)
        hamming_distance=[f'{hd:b}'.count('1') for hd in hamming_distance]
        return round(np.mean(hamming_distance),3)

    # Normalized Error Distance MED := sum { ED(bj,b) * pj }
    if (metric == "med"):
        return round(pon_avg,3)

    # Worst Case Error
    elif (metric == "wce"):
        return max(keys)

    # Normalized Mean Error Distance
    elif (metric == "wcre"):
        return round(pon_avg/me,3)

    # Mean Relative Error Distance
    elif (metric == "mred"):
        mred = sum(relative_error_distance)/len(relative_error_distance)
        return round(mred,3)

    # Mean Square Error Distance
    elif (metric == "msed"):
        msed = sum(square_error_distance)/len(square_error_distance)
        return round(msed,3)
