
from copy import deepcopy
import threading
from circuit import Circuit
from pruning_algorithms.axls import GetInputs, GetOutputs

BASE    =   "circuits/carry.skip.16b/"
TOP     =   "CSkipA_16b"
MET     =   "med"

RTL     =   f"{BASE}{TOP}.v"
TB      =   f"{BASE}{TOP}_tb.v"
SAIF    =   f"{BASE}{TOP}.saif"
ORIG    =   f"{BASE}output0.txt"
APPR    =   f"{BASE}output.txt"

def log (msg):
    with open("log.txt", "a+") as f:
        f.write(msg)

def barcas(circuit, max_error):

    actual_error = 0

    for bit in range (0, 8):

        last_stable_circuit = deepcopy(circuit)
        modified_circuit = deepcopy(circuit)

        for type in ["i","o"]:

            if type == "i":
                inputs = [f"a[{bit}]",f"b[{bit}]"]
                nodes = GetInputs(modified_circuit.netl_root, inputs)
            else:
                outputs = [f"sum[{bit}]"]
                nodes = GetOutputs(modified_circuit.netl_root, outputs)

            #print(nodes)

            for node in nodes:
                modified_circuit.delete(node.attrib["var"])

                obtained_error = modified_circuit.simulate(TB, MET, ORIG, APPR)

                nvar = node.attrib["var"];
                log(f"Deleted: {nvar} -> error ({MET}): {obtained_error}\n");


                if obtained_error < max_error:
                    last_stable_circuit = deepcopy(modified_circuit)
                    actual_error = obtained_error
                else:
                    modified_circuit = deepcopy(last_stable_circuit)


        if (actual_error == max_error):
            break

    final_error = last_stable_circuit.simulate(TB, MET, ORIG, APPR, clean=False)

    msg = f"[FINAL] Expected: {max_error}, Obtained: {final_error}\n"
    log(msg)
    print(msg)

our_circuit = Circuit(RTL, "NanGate15nm")

for error in range (10, 101, 10):
    barcas(our_circuit, error)
    '''
    x = threading.Thread(target=barcas, args=(our_circuit, error,))
    x.start()
    '''
