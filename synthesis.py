
import os
import re

def synthesis (rtl, tech, topmodule):
    '''
    Synthetizes a circuit file and map it to a specific techonolgy

    Parameters
    ----------
    rtl : str
        path of the rtl circuit file
    tech : str
        path of the technology file
    topmodule : str
        name of the circuit we want to sintetize
    tool : str
        name of tool we are going to use to sintetize

    Returns
    -------
    str
        path of the sintetized netlist file

    '''

    # - - - - - - - - - - - - - Copy the synth.ys file - - - - - - - - - - - -
    current_dir=os.path.dirname(__file__)
    file = open(f"{current_dir}/templates/synth.ys","r")
    file_text = file.read()
    file.close()

    netlist_path = os.path.dirname(rtl) + "/netlist.v"

    file_text = file_text.replace("[[RTLFILENAME]]", f'"{rtl}"')
    file_text = file_text.replace("[[TOPMODULE]]", topmodule)
    file_text = file_text.replace("[[NETLIST]]", f'"{netlist_path}"')
    file_text = file_text.replace("[[LIBRARY]]", f'"{current_dir}/templates/{tech}.lib"')
    file_text = file_text.replace("[[LIBRARYABC]]", f'"{current_dir}/templates/{tech}.lib"')

    file = open('synth.ys',"w")
    file.write(file_text)
    file.close()

    # - - - - - - - - - - - - - - - Execute yosys - - - - - - - - - - - - - -

    result = os.system (f'yosys synth.ys;')

    # - - - - - - - - - - - - - Delete temporal Files - - - - - - - - - - - -

    os.remove ("synth.ys")

    return netlist_path

def resynthesis(netlist, tech, topmodule):

    '''

    Pass a synthetized circuit to Yosys, reading the tech source file to repeat the synthesis.

    :param netlist: string
        Synthetized circuit netlist
    :param tech: string
        Name of the technology library
    :param topmodule: string
        Topmodule of the circuit
    :return:
        path-like string
            Path to re-synthetized netlist
    '''


    current_dir=os.path.dirname(__file__)
    file = open(f"{current_dir}/templates/resynth.ys","r")
    file_text = file.read()
    file.close()

    netlist_path = os.path.dirname(netlist) + "/netlist.v"

    file_text = file_text.replace("[[RTLFILENAME]]", netlist)
    file_text = file_text.replace("[[TOPMODULE]]", topmodule)
    file_text = file_text.replace("[[TECHNOLOGY]]", f'{current_dir}/templates/{tech}.v')
    file_text = file_text.replace("[[NETLIST]]", netlist_path)
    file_text = file_text.replace("[[LIBRARY]]", f"{current_dir}/templates/{tech}.lib")
    file_text = file_text.replace("[[LIBRARYABC]]", f"{current_dir}/templates/{tech}.lib")

    file = open('resynth.ys',"w")
    file.write(file_text)
    file.close()

    # - - - - - - - - - - - - - - - Execute yosys - - - - - - - - - - - - - -

    result = os.system ('yosys resynth.ys;')

    # - - - - - - - - - - - - - Delete temporal Files - - - - - - - - - - - -

    os.remove ("resynth.ys")

    return netlist_path

def ys_get_area(netlist, tech, topmodule):

    '''

    Opens the circuit in Yosys and runs stat command to estimate area. Result is parsed
    from a temporary log file generated.

    :param netlist: string
        Synthetized circuit netlist
    :param tech: string
        Name of the technology library
    :param topmodule: string
        Topmodule of the circuit
    :return:
        string
            Area estimation obtained from yosys stat command
    '''

    current_dir=os.path.dirname(__file__)
    file = open(f"{current_dir}/templates/stat.ys","r")
    file_text = file.read()
    file.close()

    yosys_log_path = os.path.dirname(netlist) + "/yosys_log.txt"

    file_text = file_text.replace("[[RTLFILENAME]]", netlist)
    file_text = file_text.replace("[[TOPMODULE]]", topmodule)
    file_text = file_text.replace("[[TECHNOLOGY]]", f'{current_dir}/templates/{tech}.v')
    file_text = file_text.replace("[[LIBRARY]]", f"{current_dir}/templates/{tech}.lib")

    file = open('stat.ys',"w")
    file.write(file_text)
    file.close()

    # - - - - - - - - - - - - - - - Execute yosys - - - - - - - - - - - - - -

    result = os.system (f'yosys stat.ys -l {yosys_log_path};')

    # - - - - - - - - - - - - - - - Parse Area - - - - - - - - - - - - - - -

    with open(yosys_log_path, "r") as read_file:
        text = read_file.read()
        pattern = r'Chip area for module\s\'[\s\S]*\':\s([\d\.]*)'
        area_pattern = re.findall(pattern, text)
        if (area_pattern):
            area = area_pattern[0]
        else:
            area = 0
        read_file.close()

    # - - - - - - - - - - - - - Delete temporal Files - - - - - - - - - - - -

    os.remove ("stat.ys")
    os.remove (yosys_log_path)

    return area
