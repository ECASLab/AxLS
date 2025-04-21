import numpy as np

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

    original_len = len(original_output)
    approx_len = len(approximate_output)

    assert original_len == approx_len, f"The output of the original and the approximate simulations doesn't match: {original_len}!={approx_len}. Make sure both outputs are being generated correctly."

    # compute the error distance ED := |a - a'|
    error_distance = [abs(original_output[x] - approximate_output[x])
        for x in range(0,len(original_output))]

    square_error_distance = [ error_distance[x]**2 for x in range(0,len(error_distance))]

    # compute the relative error distance RED := ED / a
    relative_error_distance = [
        0 if original_output[x] == 0 else error_distance[x]/original_output[x]
        for x in range(0,len(original_output))]

    # Error Rate:
    if (metric == "er"):
        return round(sum((error>0 for error in error_distance))/total,3)

    # Mean Hamming Distance see: https://stackoverflow.com/questions/40875282/fastest-way-to-get-hamming-distance-for-integer-array
    if (metric == "hd"):
        hamming_distance=np.bitwise_xor(original_output,approximate_output)
        hamming_distance=[f'{hd:b}'.count('1') for hd in hamming_distance]
        return round(np.mean(hamming_distance),3)

    # Mean Error Distance MED := sum { ED(bj,b) * pj }
    if (metric == "med"):
        mean_error = sum(error_distance) / len(error_distance)
        return round(mean_error,3)

    # Worst Case Error
    elif (metric == "wce"):
        return max(error_distance)

    # Mean Relative Error Distance
    elif (metric == "mred"):
        mred = sum(relative_error_distance)/len(relative_error_distance)
        return round(mred,3)

    # Mean Square Error Distance
    elif (metric == "msed"):
        msed = sum(square_error_distance)/len(square_error_distance)
        return round(msed,3)
