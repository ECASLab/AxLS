

import os
import collections

def simulation (rtl, testbench, tech, topmodule, tool="icarus"):
    '''
    Creates an executable using icarus, end then execute it to obtain the

    '''
    # - - - - - - - - - - - - - - - Execute icarus - - - - - - - - - - - - - -

    netlist_path = os.path.dirname(rtl)

    print("iverilog " +
        "-l ./templates/" + tech + ".v " +
        "-o " + netlist_path + "/" + topmodule +
        " "  + testbench + " " + rtl)

    # iverilog -l tech.v -o executable testbench.v netlist.v
    result = os.system ("iverilog " +
        "-l ./templates/" + tech + ".v " +
        "-o " + netlist_path + "/" + topmodule +
        " "  + testbench + " " + rtl)

    if ()

    # - - - - - - - - - - - - - Execute the testbench  - - - - - - - - - - - -

    result = os.system(
        "cd " + os.path.dirname(rtl) + "; " +
        "./" + topmodule
    )

    return netlist_path + "/" + topmodule


'''
Reads a txt file and returns the list of numbers of the files
@param filename name of the text file
@return a list of numbers of each row of the file
'''
def extract_numbers(filename):
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

    # Read original output content
    original_output = extract_numbers(original)

    # Read modified output content
    approximate_output = extract_numbers(approximate)

    # compute the error distance ED := |a - a'|
    error_distance = [abs(original_output[x] - approximate_output[x])
        for x in range(0,len(original_output))]

    square_error_distance = [ error_distance[x]**2 for x in error_distance]

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
