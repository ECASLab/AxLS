# AxLS

#### **An Open-Source Framework for Netlist Transformation Approximate Logic Synthesis**



## Requirements

To use AxLS, Python, Yosys, and Icarus Verilog are required, at least in the following versions:

| name           | version | -    |
| -------------- | ------- | ---- |
| Icarus Verilog | 10.3    |      |
| Yosys          | 0.9+932 |      |
| Python         | 3.6.8   |      |



### Installing Yosys

```bash
sudo apt-get install build-essential clang bison flex \
	libreadline-dev gawk tcl-dev libffi-dev git \
	graphviz xdot pkg-config python3 libboost-system-dev \
	libboost-python-dev libboost-filesystem-dev zlib1g-dev

git clone https://github.com/cliffordwolf/yosys.git
cd yosys/
make config-clang
make config-gcc
make
make test #optional
sudo make install
```



### Installing Icarus Verilog

```bash
wget ftp://ftp.icarus.com/pub/eda/verilog/v10/verilog-10.3.tar.gz
tar -zxvf verilog-10.3.tar.gz
cd verilog-10.3/
./configure
make
sudo make install 
```



## Using AxLS

### Parsing a netlist

1. First, import the `Circuit` class:

```python
from circuit import Circuit
```

2. Some constants are required to define files and their corresponding path:

```python
# verilog file of the circuit we want to approximate
RTL='circuits/brent.kung.16b/UBBKA_15_0_15_0.v'

# testbench file for the circuit we want to approximate
TB='circuits/brent.kung.16b/UBBKA_15_0_15_0_tb.v'

# [optional] a saif for the circuit we want to approximate
SAIF='circuits/brent.kung.16b/UBBKA_15_0_15_0.saif'
```

3. When creating a `Circuit` object, the library parse every file and builds an XML tree with all the relevant information related with the circuit

```python
# Circuit creates a representation of the circuit using python objects
our_circuit = Circuit(RTL, "NanGate15nm", SAIF)
```

4. You can print the circuit from the XML file, by calling the `get_circuit_xml()` function:

```python
print(our_circuit.get_circuit_xml())
```

You should see something like this:

```xml-dtd
<!-- complete file at circuits/brent.kung.16b/UBBKA_15_0_15_0.xml -->
```

5. Or you can also print the circuit as an graph with `show()`

```python
our_circuit.show()
```

6. From `our_circuit`, you can also obtain the circuit inputs/outputs

```python
print("Circuit inputs...")
print(our_circuit.inputs)
print("Circuit outputs...")
print(our_circuit.outputs)
```

That will return something like:

```
Circuit inputs...
['X[0]', 'X[1]', 'X[2]', 'X[3]', 'X[4]', 'X[5]', 'X[6]', 'X[7]', 'X[8]', 'X[9]', 'X[10]', 'X[11]', 'X[12]', 'X[13]', 'X[14]', 'X[15]', 'Y[0]', 'Y[1]', 'Y[2]', 'Y[3]', 'Y[4]', 'Y[5]', 'Y[6]', 'Y[7]', 'Y[8]', 'Y[9]', 'Y[10]', 'Y[11]', 'Y[12]', 'Y[13]', 'Y[14]', 'Y[15]']
Circuit outputs...
['S[0]', 'S[1]', 'S[2]', 'S[3]', 'S[4]', 'S[5]', 'S[6]', 'S[7]', 'S[8]', 'S[9]', 'S[10]', 'S[11]', 'S[12]', 'S[13]', 'S[14]', 'S[15]', 'S[16]']
```

7. Remember, the circuit is represented as an XML (ElementTree) so if you want to iterate over the XML just get the root of the tree:

```python
print(our_circuit.netl_root)
```

```
[<Element 'node' at 0xb587de14>, <Element 'node' at 0xb581057c>]
```

Using this node you can implement your own pruning algorithms. Because ElementTree allows you to search XML nodes based on their attributes using xpath syntax. 

> Don't Reinvent the Wheel!



## Deleting a node

1. The first example method we provide to delete nodes is quite simple, just delete a node based on its name. You can do it in two different ways:

```python
# Using ElementTree xpath syntax
node101 = our_circuit.netl_root.find("./node[@var='_101_']")
node101.set("delete", "yes")
```

Or

```python
# Using the built-in functionality
our_circuit.delete("_101_")
```

When you set the attribute `delete` of a node to `yes`, it means that this node will be deleted the next time our circuit is saved in the filesystem. **The node will remain in the xml tree!** (just in case we need to revert a deletion).

## Pruning Algorithms

This framework currently provides two approaches, as examples, in order to suggest which nodes you should delete:

* InOuts: suggest which nodes to delete if the inputs or the outputs are constants. 
* Pseudo-Probabilistic Pruning: suggest nodes to delete based on the toggling time a specific node keep a constant value (1 or 0) in their output. Similar as presented in J. Schlachter, V. Camus, K. V. Palem and C. Enz, "Design and Applications of Approximate Circuits by Gate-Level Pruning," in IEEE Transactions on Very Large Scale Integration (VLSI) Systems, vol. 25, no. 5, pp. 1694-1702, May 2017, doi: 10.1109/TVLSI.2017.2657799.

### InOuts

1. Lets start with InOuts methods. Import both `GetInputs` and `GetOutputs` 

```python
from pruning_algorithms.inouts import GetInputs, GetOutputs
```

2. `GetInputs` will give you a list of nodes that can be deleted if the inputs specified are constants:

```python
# Extracts the nodes that can be deleted if inputs of bit 0 are constants
inputs = ["X[0]","Y[0]"]
depricable_nodes = GetInputs(our_circuit.netl_root, inputs)
print(depricable_nodes)
print("Nodes to delete if input 0 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])
```

Shows:

```
Nodes to delete if input 0 is constant
['_069_', '_147_']
```

Other example:

```python
# Extracts the nodes that can be deleted if inputs of bit 3 are constants
inputs = ["X[0]","Y[0]","X[1]","Y[1]","X[2]","Y[2]","X[3]","Y[3]"]
depricable_nodes = GetInputs(our_circuit.netl_root, inputs)
print("Nodes to delete if input 3 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])
```

Shows:

```
Nodes to delete if input 3 is constant
['_069_', '_147_', '_066_', '_067_', '_075_', '_068_', '_070_', '_071_', '_072_', '_073_', '_074_', '_076_', '_080_', '_077_', '_078_', '_086_', '_079_', '_081_']
```

3. `GetOutputs` will give you a list of nodes that can be deleted if the outputs specified are constants:

```python
# Extracts the nodes that can be deleted if output of bit 0 is constant
outputs = ["S[0]"]
depricable_nodes = GetOutputs(our_circuit.netl_root, outputs)
print(depricable_nodes)
print("Nodes to delete if output 0 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])
```

Shows:

```
Nodes to delete if output 0 is constant
['_147_']
```

Other example:

```python
# Extracts the nodes that can be deleted if outputs of bit 3 is constant
outputs = ["S[5]"]
depricable_nodes = GetOutputs(our_circuit.netl_root, outputs)
print("Nodes to delete if output 5 is constant")
print([ n.attrib["var"] for n in depricable_nodes ])
```

Shows:

```
Nodes to delete if output 5 is constant
['_091_']
```



### ProbPun

1. In order to use ProbPrun methods **make sure you specified a SAIF file when you created the Circuit object**. First lets import the method:

```python
from pruning_algorithms.probprun import GetOneNode
```

2. `GetOneMethod` is a generator, so it will return one node every time you call it, so lets first create it:

```python
pseudo_probprun = GetOneNode(our_circuit.netl_root)
```

3. Now we can call it, every time it retrieves the node to delete, the logic value it has most of the time, and how much time it keeps that value:

```python
node, output, time = next(pseudo_probprun)
print(f"ProbPrun suggest delete the node {node} because is {output} {time}% of the time")
```

This should show:

```
ProbPrun suggest delete the node _114_ because is 0 100% of the time
```

4. As any generator, you can use it in for loops:

```python
for x in range (30):
    node, output, time = next(pseudo_probprun)
    print(f"{node} is {output} {time}% of the time")
```

This will return:

```
ProbPrun suggest delete the node _114_ because is 0 100% of the time
_115_ is 1 100% of the time
_116_ is 0 100% of the time
_117_ is 1 100% of the time
_120_ is 1 100% of the time
_121_ is 1 100% of the time
_122_ is 0 100% of the time
_123_ is 1 100% of the time
_125_ is 0 100% of the time
_126_ is 1 100% of the time
_127_ is 0 100% of the time
_128_ is 1 100% of the time
_129_ is 0 100% of the time
_131_ is 1 100% of the time
_132_ is 1 100% of the time
_133_ is 0 100% of the time
_134_ is 1 100% of the time
_136_ is 0 100% of the time
_137_ is 1 100% of the time
_138_ is 0 100% of the time
_139_ is 1 100% of the time
_140_ is 0 100% of the time
_142_ is 1 100% of the time
_143_ is 1 100% of the time
_144_ is 0 100% of the time
_145_ is 1 100% of the time
_066_ is 1 75% of the time
_071_ is 0 75% of the time
_072_ is 1 75% of the time
_077_ is 1 75% of the time
_082_ is 0 75% of the tim
```

## Simulation and Error Estimation

Simulation stage and error estimation are executed inside one method called `simulate`. In order to execute a simulation you need to provide:

* The exact results
* The name of the approximated results file
* Error metric

1. Lets start defining the names of the original and approximated results files. **ORIGINAL must exists, while APPROX is the name of the file that will be produced by the testbench**.

```python
ORIGINAL='circuits/brent.kung.16b/output0.txt'
APPROX='circuits/brent.kung.16b/output.txt'
```

2. Now we are ready to execute the simulation

```python
error = our_circuit.simulate(TB, "med", ORIGINAL, APPROX)
print(error)
```

This should returns:

```
63.011
```



 # Files and Folders

Files and Folders description:

| Name                | Description                                                  | Used   |
| ------------------- | ------------------------------------------------------------ | ------ |
| circuits            | Contains the rtl and testbench of some sample circuits.      |        |
| prunning_algorithms | Folder containing pruning techniques implementations.        |        |
| `inouts.py`         | Contains the implementation of `GetInputs` and `GetOutputs` example pruning methods. |        |
| `probprun.py`       | Contains the implementation of a pseudo Probabilistic Pruning method. `GetOneNode` is a python generator. It will retrieve one node to delete each time it is called. |        |
| templates           | Folder containing some libraries and scripts used for synthesis. |        |
| `NanGate15nm.lib`   |                                                              |        |
| `NanGate15nm.v`     |                                                              |        |
| `synth.ys`          | Script for synthesize a circuit using yosys.                 |        |
| `__main__.py`       | It executes the tool using the arguments from the command line. **Still in progress**. | **No** |
| `barcas.py`         | Is the Pruning Implementation using the InOuts techniques.   |        |
| `circuit.py`        | Object that represents a circuit as a XML tree. Receives a rtl and a library in order to build the circuit and be able to simulate it. |        |
| `circuiterror.py`   | Compares two outputs and computes different error metrics.   |        |
| `demo.py`           | This file is a complete example of how the library should be used. |        |
| `netlist.py`        | This class parses, extracts and represents the circuit from rtl into an object understandable by python. |        |
| `poisonoak.config`  | This is going to be used along with `__main__.py` in order to execute poisonoak as an app, and not as a library. | **No** |
| `poisonoak.help`    | Contains the menu and tool description of the poison oak app. | **No** |
| `synthesis.py`      | Executes the synthesis script (in our case yosys) and clean the intermediate files generated. At the end returns the path of the netlist. |        |
| `technology.py`     | This class parses, extracts and represents the technology library file into an object understandable by python. |        |
| `test.py`           | This class implements some unit tests for the poison oak library. **Not implemented yet**. | **No** |
| `utils.py`          | Some functions not related with any other class but useful.  |        |

