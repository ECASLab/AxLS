from circuit import Circuit
from pruning_algorithms.inouts import GetInputs, GetOutputs
from pruning_algorithms.probprun import GetOneNode

# name of the circuit we want to parse
RTL = "ALS-benchmark-circuits/BK_16b/BK_16b.v"
SAIF = "ALS-benchmark-circuits/BK_16b/NanGate15nm/BK_16b.saif"

# Testbench and dataset files to generate
TB = "ALS-benchmark-circuits/BK_16b/BK_16b_tb.v"
DATASET = "ALS-benchmark-circuits/BK_16b/dataset"
SAMPLES = 100_000

# benchmark result files
EXACT_RESULT = "ALS-benchmark-circuits/BK_16b/output_exact.txt"
APPROX_RESULT = "ALS-benchmark-circuits/BK_16b/output_approx.txt"

# the demo creates images of the circuit change this constants to avoid
# creating or just opening them
CREATE_IMAGE = True  # Set to false to avoid creating image
VIEW_IMAGE = True  # Set to false to avoid opening the images

# Circuit creates a representation of the circuit using python objects
our_circuit = Circuit(RTL, "NanGate15nm", SAIF)

# Generate the dataset and testbench
our_circuit.generate_dataset(DATASET, SAMPLES)
our_circuit.write_tb(TB, DATASET, iterations=SAMPLES)

our_circuit.exact_output(TB, EXACT_RESULT)

# if you want to see the circuit xml
print("\nShowing circuit XML\n---------------------")
print(our_circuit.get_circuit_xml())
print("---------------------")
input("Press any key to continue...")

# if you want to see the circuit as a graph
if CREATE_IMAGE:
    print("\nShowing circuit as a graph")

    our_circuit.show("demo_circuit", view=VIEW_IMAGE, format="png")
    input("Press any key to continue...")

# if you need the circuit inputs / outputs
print("Circuit inputs...")
print(our_circuit.inputs)
print("Circuit outputs...")
print(our_circuit.outputs)

# the root of the xml tree is at:
print("Root of XML tree: ", our_circuit.netl_root)

# lets delete a node for example the _101_
our_circuit.delete("_101_")

# lets plot the circuit showing the nodes to be deleted
if CREATE_IMAGE:
    print("\nShowing circuit with node _101_ to be deleted")
    our_circuit.show(
        "demo_circuit_with_deletion", show_deletes=True, view=VIEW_IMAGE, format="png"
    )
    input("Press any key to continue...")

# lets write the new netlist without the deleted node
our_circuit.write_to_disk(filename="netlist_without_101.v")

# Lets start with our pruning algorithms

# Extracts the nodes that can be deleted if inputs of bit 0 are constants
inputs = ["X[0]", "Y[0]"]
depricable_nodes = GetInputs(our_circuit.netl_root, inputs)
print(depricable_nodes)
print("Nodes to delete if input 0 is constant")
print([n.attrib["var"] for n in depricable_nodes])

# Extracts the nodes that can be deleted if inputs of bit 3 are constants
inputs = ["X[0]", "Y[0]", "X[1]", "Y[1]", "X[2]", "Y[2]", "X[3]", "Y[3]"]
depricable_nodes = GetInputs(our_circuit.netl_root, inputs)
print("Nodes to delete if input 3 is constant")
print([n.attrib["var"] for n in depricable_nodes])


# Extracts the nodes that can be deleted if output of bit 0 is constant
outputs = ["S[0]"]
depricable_nodes = GetOutputs(our_circuit.netl_root, outputs)
print(depricable_nodes)
print("Nodes to delete if output 0 is constant")
print([n.attrib["var"] for n in depricable_nodes])

# Extracts the nodes that can be deleted if outputs of bit 3 is constant
outputs = ["S[5]"]
depricable_nodes = GetOutputs(our_circuit.netl_root, outputs)
print("Nodes to delete if output 5 is constant")
print([n.attrib["var"] for n in depricable_nodes])

# Lets try another method: pseudo probprub.
# Every time we call the function it returns the recommended node to delete
# because it was all the time in 1 or 0

pseudo_probprun = GetOneNode(our_circuit.netl_root)

node, output, time = next(pseudo_probprun)

print(
    f"ProbPrun suggest delete the node {node} because is {output} {time}% of the time"
)

# so lets take out the 10 most useless nodes

for x in range(10):
    node, output, time = next(pseudo_probprun)
    print(f"{node} is {output} {time}% of the time")


print("Simulating...")
error = our_circuit.simulate_and_compute_error(TB, EXACT_RESULT, APPROX_RESULT, "med")
print("Simulation finished...")
print(error)
