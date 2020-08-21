
from circuit import Circuit
from pruning_algorithms.axls import GetInputs, GetOutputs
from pruning_algorithms.probprun import GetOneNode

# name of the circuit we want to parse
RTL='circuits/brent.kung.16b/UBBKA_15_0_15_0.v'
TB='circuits/brent.kung.16b/UBBKA_15_0_15_0_tb.v'
SAIF='circuits/brent.kung.16b/UBBKA_15_0_15_0.saif'

# Circuit creates a representation of the circuit using python objects
our_circuit = Circuit(RTL, "NanGate15nm", SAIF)

# For example:

# if you want to see the circuit xml
print(our_circuit.get_circuit_xml())

# if you want to see the circuit as a graph
##### our_circuit.show()

# if you need the circuit inputs / outputs
print("Circuit inputs...")
print(our_circuit.inputs)
print("Circuit outputs...")
print(our_circuit.outputs)

# the root of the xml tree is at:
print(our_circuit.netl_root)


# lets delete a node for example the _101_
node101 = our_circuit.netl_root.find("./node[@var='_101_']")
node101.set("delete", "yes")

# or
our_circuit.delete("_101_")

# lets plot the circuit showing the nodes to be deleted
##### our_circuit.show(show_deletes=True)

# lets write the new netlist without the deleted node
our_circuit.write_to_disk(filename="netlist_without_101.v")

# Lets start with our pruning algorithms

# Extracts the nodes that can be deleted if inputs of bit 0 are constants
inputs = ["X[0]","Y[0]"]
depricable_nodes = GetInputs(our_circuit.netl_root, inputs)
print(depricable_nodes)
print("Nodes to delete if input 0 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])

# Extracts the nodes that can be deleted if inputs of bit 3 are constants
inputs = ["X[0]","Y[0]","X[1]","Y[1]","X[2]","Y[2]","X[3]","Y[3]"]
depricable_nodes = GetInputs(our_circuit.netl_root, inputs)
print("Nodes to delete if input 3 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])


# Extracts the nodes that can be deleted if output of bit 0 is constant
outputs = ["S[0]"]
depricable_nodes = GetOutputs(our_circuit.netl_root, outputs)
print(depricable_nodes)
print("Nodes to delete if output 0 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])

# Extracts the nodes that can be deleted if outputs of bit 3 is constant
outputs = ["S[5]"]
depricable_nodes = GetOutputs(our_circuit.netl_root, outputs)
print("Nodes to delete if output 5 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])

# Lets try another method: pseudo probprub.
# Every time we call the function it returns the recommended node to delete
# because it was all the time in 1 or 0

pseudo_probprun = GetOneNode(our_circuit.netl_root)

node, output, time = next(pseudo_probprun)

print(f"ProbPrun suggest delete the node {node} because is {output} {time}% of the time")

# so lets take out the 10 most useless nodes

for x in range (30):
    node, output, time = next(pseudo_probprun)
    print(f"{node} is {output} {time}% of the time")


# how to simulate the circuit tree and obtain the error
# you need to know how your results files are going to be names
# for example
# original exact results are called output0.txt
# outputs obtained from the test bench are calld output.txt

ORIGINAL='circuits/brent.kung.16b/output0.txt'
APPROX='circuits/brent.kung.16b/output.txt'

error = our_circuit.simulate(TB, "med", ORIGINAL, APPROX)
print(error)

