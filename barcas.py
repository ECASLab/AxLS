
from copy import deepcopy
import threading
from circuit import Circuit
from pruning_algorithms.axls import GetInputs, GetOutputs

BASE    =   "circuits/ripple.carry.4b/"
TOP     =   "RCA_3_0"
MET     =   "wce"

RTL     =   f"{BASE}{TOP}.v"
TB      =   f"{BASE}{TOP}_tb.v"
SAIF    =   f"{BASE}{TOP}.saif"
ORIG    =   f"{BASE}output0.txt"
APPR    =   f"{BASE}output.txt"

def log (msg):
    with open(f"{BASE}log.txt", "a+") as f:
        f.write(msg)
    print(msg)

def barcas(circuit, max_error):

    log(f"Pruning circuit for Max Error of: {max_error}\n")

    actual_error = 0

    last_stable_circuit = deepcopy(circuit)
    modified_circuit = deepcopy(circuit)

    for bit in range (0, 4):

        for type in ["i","o"]:

            if type == "i":
                inputs = [f"in1[{bit}]",f"in2[{bit}]"]
                nodes = GetInputs(modified_circuit.netl_root, inputs)
            else:
                outputs = [f"out[{bit}]"]
                nodes = GetOutputs(modified_circuit.netl_root, outputs)

            #print(nodes)

            for node in nodes:
                modified_circuit.delete(node.attrib["var"])

                obtained_error = modified_circuit.simulate(TB, MET, ORIG, APPR)

                nvar = node.attrib["var"];

                msg = f"Node Deleted: {nvar}, error({MET}): {obtained_error}\n"

                log(msg);

                if obtained_error <= max_error:
                    last_stable_circuit.delete(node.attrib["var"])
                    actual_error = obtained_error
                else:
                    modified_circuit.undodelete(node.attrib["var"])


        if (actual_error == max_error):
            break

    final_error = last_stable_circuit.simulate(TB, MET, ORIG, APPR, clean=False)

    last_stable_circuit.show(show_deletes=True)
    input("Press enter...")

    msg = f"[FINAL] Expected: {max_error}, Obtained: {final_error}\n"
    log(msg)

our_circuit = Circuit(RTL, "NanGate15nm")

for error in [8]: #range (10, 101, 10):

    our_circuit.exact_output(TB)
    barcas(our_circuit, error)
    '''
    x = threading.Thread(target=barcas, args=(our_circuit, error,))
    x.start()
    '''
