
import os

def delete_node (netl_root, node):
    node = netl_root.find("./node[@var='" + node + "']")
    node.set("delete", "yes")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Iterates backwards over the netlist in order to find all the posibe paths
between a node and an input
'''
def get_output_path_aux (netl_root, node, path):

    node_output = node.findall("output")[0].attrib["wire"]
    children = netl_root.findall(
        "./node/input[@wire='" + node_output + "']/..")
    children_to_delete = netl_root.findall(
        "./node[@delete='yes']/input[@wire='" + node_output + "']/..")

    if (len(children) == len(children_to_delete)):
        node.set ("delete", "yes")
        path.append(node.attrib["var"])

        # keep going back
        for input in node.findall("input"):
            xpath = "./node/output[@wire='" + input.attrib["wire"] + "']/.."
            parents = netl_root.findall(xpath)
            for parent in parents:
                get_output_path_aux (netl_root, parent, path)


def get_output_path (netl_root, bit):

    path = []

    outputs = netl_root.findall("./circuitoutputs/output")
    output_wires = [o.attrib["var"] for o in outputs]

    output_nodes = [w for w in output_wires if f"[{bit}]" in w]

    for output in output_nodes:
        node = netl_root.find(f"./node/output[@wire='{output}']/..")
        get_output_path_aux(netl_root, node, path)

    return path

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def pruning_input_aux(netl_root, node, constants):
    '''
    Iterates recursively the circuit tree from top to bottom deleting the inputs

    Parameters
    ----------
    netl_root : ElementTree.Element
        Root node of the circuit tree
    node : ElementTree.Element
        Current node we are deleting
    constants : array
        List of wires with a constant value of 0 or 1 (deprecable)
    '''

    node_inputs = node.findall("input")
    node_inputs = [i for i in node_inputs if not i.attrib["wire"] in constants]
    if (len(node_inputs) == 0):
        print("delete ", node.attrib["var"])
        node.set ("delete", "yes")

        for output in node.findall("output"):
            o = output.attrib["wire"]
            if (not o in constants):
                constants.append(o)
            children = netl_root.findall(f"./node/input[@wire='{o}']/..")
            for child in children:
                pruning_input_aux(netl_root, child, constants)


def pruning_input (netl_root, bit):
    '''
    Iterates the circuit tree from top to bottom deleting the inputs

    Parameters
    ----------
    netl_root : ElementTree.Element
        Root node of the circuit tree
    bit : int
        Bit until where the circuit is going to be approximated
    '''

    inputs = netl_root.findall("./circuitinputs/input")
    input_wires = [i.attrib["var"] for i in inputs]
    constants = []

    # get the input constants
    for b in range(0,bit+1):
        constant_wires = [w for w in input_wires if f"[{str(b)}]" in w]
        constants += constant_wires

    for c in constants:
        children = netl_root.findall(f"./node/input[@wire='{c}']/..")
        for c in children:
            pruning_input_aux(netl_root, c, constants)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from copy import deepcopy

from circuit import Circuit
from simulation import simulation, compute_error

RTL='../samples/brent.kung.16b/UBBKA_15_0_15_0.v'
TESTBENCH='../samples/brent.kung.16b/UBBKA_15_0_15_0_tb.v'
OUT0='../samples/brent.kung.16b/output0.txt'
OUT='../samples/brent.kung.16b/output.txt'
METRIC='wce'

our_circuit = Circuit(RTL, "NanGate15nm")

#circuit_tree.show()

def simulate_and_compute(modified_circuit, metric, expected_error, final=False):
    new_netl_file = modified_circuit.write_to_disk()

    simulation(
        rtl=new_netl_file,
        testbench=TESTBENCH,
        tech='NanGate15nm',
        topmodule=modified_circuit.topmodule)

    error = compute_error(
        metric,
        OUT0,
        OUT
        )

    print ("Expected error: ", expected_error, " obtained error: ", error)

    if not final:
        os.remove(new_netl_file)

    return expected_error >= error

def pruning(circuit, expected_error):

    print("pruning... expected error ", expected_error)

    last_stable_circuit = deepcopy(circuit)
    modified_circuit = deepcopy(circuit)

    circuit_outputs = len(circuit.netl_root.findall("./circuitoutputs/output"))

    for bit in range (0,circuit_outputs):

        nodes = get_output_path (modified_circuit.netl_root, bit)


        print(f"First, lets prune the complete path of bit {bit}")
        for node in nodes:
            delete_node(modified_circuit.netl_root, node)

        if simulate_and_compute(modified_circuit, METRIC, error):
            last_stable_circuit = deepcopy(modified_circuit)
        else:
            modified_circuit = deepcopy(last_stable_circuit)
            for node in nodes:
                delete_node(modified_circuit.netl_root, node)
                if simulate_and_compute(modified_circuit, METRIC, error):
                    last_stable_circuit = deepcopy(modified_circuit)
                else:
                    modified_circuit = deepcopy(last_stable_circuit)

    print("FINAL RESULT")
    simulate_and_compute(modified_circuit, METRIC, error, final=True)



for error in range(10, 101, 10):
    pruning(our_circuit, error)
