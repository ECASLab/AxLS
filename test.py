
import unittest

from circuit import Circuit
from pruning_algorithms.axls import GetInputs, GetOutputs
from pruning_algorithms.probprun import GetOneNode

RTL='circuits/brent.kung.16b/UBBKA_15_0_15_0.v'
SAIF='circuits/brent.kung.16b/UBBKA_15_0_15_0.saif' 

CIRCUIT_INPUTS = ['X[0]', 'X[1]', 'X[2]', 'X[3]', 'X[4]', 'X[5]', 'X[6]', 'X[7]', 'X[8]', 'X[9]', 'X[10]', 'X[11]', 'X[12]', 'X[13]', 'X[14]', 'X[15]', 'Y[0]', 'Y[1]', 'Y[2]', 'Y[3]', 'Y[4]', 'Y[5]', 'Y[6]', 'Y[7]', 'Y[8]', 'Y[9]', 'Y[10]', 'Y[11]', 'Y[12]', 'Y[13]', 'Y[14]', 'Y[15]']
CIRCUIT_OUTPUTS = ['S[0]', 'S[1]', 'S[2]', 'S[3]', 'S[4]', 'S[5]', 'S[6]', 'S[7]', 'S[8]', 'S[9]', 'S[10]', 'S[11]', 'S[12]', 'S[13]', 'S[14]', 'S[15]', 'S[16]']

class PoisonoakTest(unittest.TestCase):

    def test_circuit_inputs(self):
        self.assertEqual(
            self.our_circuit.inputs,
            CIRCUIT_INPUTS,
            f"Should be {CIRCUIT_INPUTS}"
        )
        
    def test_circuit_outputs(self):
        self.assertEqual(
            self.our_circuit.outputs,
            CIRCUIT_OUTPUTS,
            f"Should be {CIRCUIT_OUTPUTS}"
        )

    def setUp(self):
        self.our_circuit = Circuit(RTL, "NanGate15nm", SAIF)
        # print(our_circuit.get_circuit_xml())
        # our_circuit.show()    

if __name__ == '__main__':
    unittest.main()
    

'''
# the root of the xml tree is at:
print(our_circuit.netl_root)


# lets delete a node for example the _101_
node101 = our_circuit.netl_root.find("./node[@var='_101_']")
node101.set("delete", "yes")

# or
our_circuit.delete("_101_")

# lets plot the circuit showing the nodes to be deleted
our_circuit.show(show_deletes=True)

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

for x in range (10):
    node, output, time = next(pseudo_probprun)
    print(f"{node} is {output} {time}% of the time")    
'''

