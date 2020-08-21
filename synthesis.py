
import os

def synthesis (rtl, tech, topmodule, tool="yosys"):
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

    file = open("templates/synth.ys","r")
    file_text = file.read()
    file.close()

    netlist_path = os.path.dirname(rtl) + "/netlist.v"

    file_text = file_text.replace("[[RTLFILENAME]]", rtl)
    file_text = file_text.replace("[[TOPMODULE]]", topmodule)
    file_text = file_text.replace("[[NETLIST]]", netlist_path)
    file_text = file_text.replace("[[LIBRARY]]", f"templates/{tech}.lib")
    file_text = file_text.replace("[[LIBRARYABC]]", f"templates/{tech}.lib")

    file = open('synth.ys',"w")
    file.write(file_text)
    file.close()

    # - - - - - - - - - - - - - - - Execute yosys - - - - - - - - - - - - - -

    result = os.system ("yosys synth.ys;")

    # - - - - - - - - - - - - - Delete temporal Files - - - - - - - - - - - -

    os.remove ("synth.ys")

    return netlist_path
