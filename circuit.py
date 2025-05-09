import os
import re
import datetime

from graphviz import Digraph
from os import path, remove, system, rename
from random import randint
from re import findall
import xml.etree.ElementTree as ET

from circuiterror import compute_error
from netlist import Netlist
from synthesis import synthesis, resynthesis, ys_get_area
from technology import Technology
from utils import get_name, get_random
import numpy as np





class Circuit:
    '''
    Representation of a synthesized rtl circuit

    Attributes
    -----------
    rtl_file : str
        path to the circuit rtl file
    tech_file : str
        name of the technology library used to map the circuit
    topmodule : str
        name of the circuit module that we want to synthesize
    netl_file : str
        path to the synthesized netlist file
    tech_root : ElementTree.Element
        references to the root element of the Technology Library Cells tree
    '''


    def __init__(self, rtl, tech, saif = "", topmodule = None):
        '''
        Parse a rtl circuit into a xml tree using a specific technology library

        Parameters
        ----------
        rtl : string
            path to the rtl file
        tech : string
            path to the technology file
        saif : string
            path to the saif file
        topmodule : string (optional)
            name of the circuit module that we want to synthesize, if not
            provided it will be inferred from the rtl filename
        '''


        self.rtl_file = rtl
        self.tech_file = tech

        if not topmodule:
            topmodule = rtl.split('/')[-1].replace(".v","")

        self.topmodule = topmodule
        self.netl_file = synthesis (rtl, self.tech_file, self.topmodule)
        self.technology = Technology(self.tech_file)
        # extract the usefull attributes of netlist
        netlist = Netlist(self.netl_file, self.technology)
        self.netl_root = netlist.root
        self.inputs = netlist.circuit_inputs
        self.outputs = netlist.circuit_outputs

        self.raw_inputs = netlist.raw_inputs
        self.raw_outputs = netlist.raw_outputs
        self.raw_parameters = netlist.raw_parameters

        if (saif != ""):
            self.saif_parser(saif)

        self.output_folder = path.dirname(path.abspath(rtl))

    def get_circuit_xml(self):
        '''
        Returns the circuit netlist in xml format

        Returns
        -------
        string
            xml string of the circuit tree
        '''
        return ET.tostring(self.netl_root)


    def get_node(self, node_var):
        '''
        Returns the ElementTree object corresponding to the node variable

        Parameters
        ----------
        node_var : string
            name of the node to be searched

        Returns
        -------
        ElementTree.Element
            Node instance we are looking for
        '''
        return self.netl_root.find(f"./node[@var='{node_var}']")


    def delete(self, node_var):
        '''
        Marks a node to be deleted

        Parameters
        ----------
        node_var : string
            name of the node to be deleted
        '''
        node_to_delete = self.netl_root.find(f"./node[@var='{node_var}']")
        if (node_to_delete is not None):
            node_to_delete.set("delete", "yes")
        else:
            print(f"Node {node_var} not found")

    def undodelete(self, node_var):
        '''
        Removes the delete label from a node

        Parameters
        ----------
        node_var : string
            name of the node to be preserved
        '''
        node_to_delete = self.netl_root.find(f"./node[@var='{node_var}']")
        if (node_to_delete is not None):
            node_to_delete.attrib.pop("delete")
        else:
            print(f"Node {node_var} not found")

    # this are some auxiliary functions for write_to_disk

    def is_node_deletable(self, node):
        '''
        Returns true if a node can be deleted, returns false if the node should
        be assigned a constant instead.

        A node can be deleted if all its children nodes will be deleted as
        well. If a node has children nodes or connects directly to an output of
        the circuit, then the funcction will return false and the node should
        be replaced with a constant.

        Parameters
        ----------
        node : ElementTree.Element
            node we want to examine

        Returns
        -------
        boolean
            true if the node can be deleted
        '''

        root = self.netl_root

        node_output = node.findall("output")[0]
        wire = node_output.attrib["wire"]

        # children of node
        re = f"./node/input[@wire='{wire}']/.."
        node_children = root.findall(re)

        # children of node that had to be deleted
        re = f"./node[@delete='yes']/input[@wire='{wire}']/.."
        node_children_to_be_deleted = root.findall(re)

        # If no nodes have this node as an input, it means that this node must
        # connect directly to a circuit output.
        connects_to_output = len(node_children) == 0

        some_children_not_deleted = len(node_children_to_be_deleted) < len(node_children)

        node_has_outputs = connects_to_output or some_children_not_deleted
        node_can_be_deleted = not node_has_outputs

        return node_can_be_deleted


    def node_to_constant(self, node):
        '''
        Returns the constant value for which the node can be replaced

        Parameters
        ----------
        node : ElementTree.Element
            node we want to make constant

        Returns
        -------
        integer
            logic 1 or 0
        '''
        node_output = node.findall("output")[0]
        if "t0" in node_output.attrib:
            t1 = int(node_output.attrib["t1"])
            t0 = int(node_output.attrib["t0"])
            return 1 if t1 > t0 else 0
        else:
            return 0


    def get_circuit_wires(self):
        '''
        Returns an ordered list of every circuit wire

        Returns
        -------
        array
            list of circuit wires names
        '''
        outputs = self.netl_root.findall("./node/output")
        wires = list(set([output.attrib["wire"] for output in outputs]))

        # make sure there are not any inputsoutputs in wires
        wires = [wire for wire in wires if wire not in self.inputs]
        wires = [wire for wire in wires if wire not in self.outputs]
        return wires


    def get_circuit_nodes(self):
        '''
        Returns an ordered list of every circuit node

        Returns
        -------
        array
            list of circuit nodes names
        '''
        nodes = self.netl_root.findall("./node")
        return [node.attrib["var"] for node in nodes]

    def get_nodes_to_delete(self):
        '''
        Returns a list of the nodes variables that will be deleted

        Returns
        -------
        array
            list of nodes variable names
        '''
        nodes_to_delete = self.netl_root.findall("./node[@delete='yes']")
        return [node.attrib["var"] for node in nodes_to_delete]


    def get_wires_to_be_deleted(self):
        '''
        Returns two lists with the wires that will be deleted completely and
        another list with the wires that should be assigned a constant.

        Returns
        -------
        ( array, dictionary )
            list of wires to delete and a dictionary of wires to be grounded
            with their logical value
        '''
        wires_to_be_deleted = [] # {wire1, wire2, ... }
        wires_to_be_assigned = {}   # { wire: value, ... }
        nodes_to_delete = self.netl_root.findall("./node[@delete='yes']")
        for node in nodes_to_delete:
            node_output = node.findall("output")[0]
            if self.is_node_deletable(node):
                # the wire could be DELETED
                wire = node_output.attrib["wire"]
                wires_to_be_deleted.append(wire)
            else:
                # the wire needs to be ASSIGNED
                wire = node_output.attrib["wire"]
                constant = self.node_to_constant(node)
                wires_to_be_assigned[wire] = constant
        return wires_to_be_deleted, wires_to_be_assigned



    def write_to_disk (self, filepath):
        '''
        Write the xml circuit into a netlist file considering the nodes to be
        deleted (marked with an attribute delete='yes')

        Parameters
        ----------
        filepath: string
            Full file path to the generated file.
        '''

        def format_io(node, io):
            ioputs = node.findall(f"{io}put")
            return [f".{x.attrib['name']}({x.attrib['wire']})" for x in ioputs]

        nodes_to_delete = self.get_nodes_to_delete()
        to_be_deleted, to_be_assigned = self.get_wires_to_be_deleted()

        with open(filepath, 'w') as netlist_file:

            def writeln(file, text):
                file.write(text + "\n")

            header = "/* Generated by poisonoak */"
            writeln(netlist_file, header)

            params = self.raw_parameters
            module = f"module {self.topmodule} ({params});"
            writeln(netlist_file, module)

            for wire in self.get_circuit_wires():
                if wire not in to_be_deleted:
                    writeln(netlist_file, f"\twire {wire};")
            used_ports=[]
            for output in self.raw_outputs:
                if output not in used_ports:
                    writeln(netlist_file, "\t" + output)
                    used_ports.append(output)
            for input in self.raw_inputs:
                if input not in used_ports:
                    writeln(netlist_file, "\t" + input)
                    used_ports.append(input)

            for node_var in self.get_circuit_nodes():
                if node_var not in nodes_to_delete:
                    node = self.get_node(node_var)
                    instance = f"\t{node.attrib['name']} {node.attrib['var']}"
                    inputs = format_io(node, "in")
                    outputs = format_io(node, "out")
                    instance += f" ({','.join(outputs)},{','.join(inputs)});"
                    writeln(netlist_file, instance)

            for wire,value in to_be_assigned.items():
                assign = f"\tassign {wire} = 1'b{value};"
                writeln(netlist_file, assign)

            assignments=self.netl_root.findall('./assignments/assign')
            for a in assignments: #support for special assignments
                assign=f"\tassign {a.attrib['var']} = {a.attrib['val']};"
                writeln(netlist_file, assign)

            writeln(netlist_file, "endmodule")


    def show (self, filename=None, show_deletes=False, view=True, format="png"):
        '''
        Renders the circuit as an image of the graph.
        Requires the graphviz python package to be installed.

        Parameters
        ----------
        filename: str (defaults to the circuit's name)
            Name of the png image to render, it shouldn't include the
            extension.
            For example filename="circuit" results in a file "circuit.png"
        show_deletes : boolean (defaults to False)
            nodes to be deleted will be colored in red
        view: boolean (defaults to True)
            if True, opens the image automatically
        format: str (defaults to "png")
            The format to create render the image with
        '''
        root = self.netl_root
        f = Digraph(self.topmodule)

        # we get the circuit inputs and outputs
        inputs = [i.replace('[','_').replace(']','') for i in self.inputs]
        outputs = [o.replace('[','_').replace(']','') for o in self.outputs]

        # inputs will have diamond shape with color
        f.attr('node',style='filled',fillcolor='#5bc0eb',shape='diamond')
        for i in inputs:
            f.node(i)
        # outputs will have doublecircle shape with color
        f.attr('node',style='filled',fillcolor='#9bc53d',shape='doublecircle')
        for o in outputs:
            f.node(o)
        # nodes to be deleted will be in a different color
        if (show_deletes):
            f.attr('node',style='filled',fillcolor='#f17e7e',shape='circle')
            for p in root.findall("./node[@delete='yes']"):
                f.node(p.attrib['var'])
        # the rest of the nodes will be a white circle
        f.attr('node', style='filled', fillcolor='white', shape='circle')

        # draw the edges
        for n in root.findall("node"):
            # iterate every node output to find edges to their children
            for o in n.findall("output"):
                wire = o.attrib["wire"]
                children = root.findall(f".//input[@wire='{wire}']/..")
                # create a new conection between every node and its child
                for c in children:
                    start = n.attrib["var"]
                    end = c.attrib["var"]
                    label = wire
                    f.edge(start, end, label=label)

                # if node has no children, is connected to a circuit output.
                if (len(children) == 0):
                    start = n.attrib["var"]
                    end = wire.replace('[','_').replace(']','')
                    f.edge(start, end)

            # inputs are not represented as nodes, so they have to be connected
            for i in n.findall("input"):
                wire = i.attrib["wire"]
                parents = root.findall(f".//output[@wire='{wire}']/..")

                # if node has no parents, is connected to a circuit input
                if (len(parents) == 0):
                    start = wire.replace('[','_').replace(']','')
                    end = n.attrib["var"]
                    f.edge(start, end)

        return(f.render(filename=filename, format=format, view=view, cleanup=True))



    def saif_parser (self, saif):
        '''
        Captures the t0, t1 and tc parameters for each component/variable and store
        them directly in the xml file of the netlist

        Parameters
        ----------
        saif : string
            file saif formatted file name
        '''
        with open(saif, 'r') as technology_file:
            content = technology_file.read()

            expreg = r'\((.+)\n.*\(T0 ([0-9]+)\).*\(T1 ([0-9]+)\).*\n.*\(TC ([0-9]+)\).*\n.*\)'
            saif_cells = findall(expreg, content)

            for saif_cell in saif_cells:

                t0 = int(saif_cell[1])
                t1 = int(saif_cell[2])
                total = int(t1 + t0)

                saif_cell_name = saif_cell[0]
                saif_cell_t0 = str( int((t0/total)*100) )
                saif_cell_t1 = str( int((t1/total)*100) )
                saif_cell_tc = saif_cell[3]

                if (saif_cell_name[0] == "w"):
                    my_saif_cell_name = "_" + saif_cell_name[1:] + "_"
                    cells = self.netl_root.find(f"./node/output[@wire='{my_saif_cell_name}']")

                    if (cells is not None):
                        cells.set('t0',saif_cell_t0)
                        cells.set('t1',saif_cell_t1)
                        cells.set('tc',saif_cell_tc)

                elif ((saif_cell_name[0],saif_cell_name[-1]) == ("_","_")): #Yosys 19.
                    my_saif_cell_name = "_" + saif_cell_name[1:-1] + "_"
                    cells = self.netl_root.find(f"./node/output[@wire='{my_saif_cell_name}']")

                    if (cells is not None):
                        cells.set('t0',saif_cell_t0)
                        cells.set('t1',saif_cell_t1)
                        cells.set('tc',saif_cell_tc)

                elif (saif_cell_name.replace('\\','') in self.outputs):
                    my_saif_cell_name = saif_cell_name.replace('\\','')
                    cells = self.netl_root.find(f"./node/output[@wire='{my_saif_cell_name}']")

                    if (cells is not None):
                        cells.set('t0',saif_cell_t0)
                        cells.set('t1',saif_cell_t1)
                        cells.set('tc',saif_cell_tc)

        return saif

    def exact_output (self, testbench, output_file):
        '''
        Simulates the actual circuit tree (with deletions)
        Creates an executable using icarus, end then execute it to obtain the
        output of the testbench

        Parameters
        ----------
        testbench : string
            path to the testbench file
        metric : string
            equation to compute the error
            options med, wce, wcre,mred, msed
        output_file : string
            Path to the output file where simulation results will be written.
            The user must provide the full file path and name. If the file
            exists, it will be overwritten.
        '''


        rtl = f"{self.output_folder}/{get_name(5)}.v"
        self.write_to_disk(rtl)

        top = self.topmodule
        current_dir=os.path.dirname(__file__)
        tech = f"{current_dir}/templates/" + self.tech_file

        # Executable is ran from the testbench folder, because the path to the
        # dataset is relative to the testbench file.
        out = os.path.dirname(testbench)

        """Better to temporarily change cwd when executing iverilog"""
        cwd=os.getcwd()
        os.chdir(current_dir)

        # - - - - - - - - - - - - - - - Execute icarus - - - - - - - - - - - - -
        # iverilog -l tech.v -o executable testbench.v netlist.v
        kon = f"iverilog -l \"{tech}.v\" -o \"{out}/{top}\" {testbench} \"{rtl}\""
        system(kon)

        # - - - - - - - - - - - - - Execute the testbench  - - - - - - - - - - -
        system(f"cd \"{out}\"; ./{top}")

        os.chdir(cwd)

        remove(rtl)
        remove(f"{out}/{top}")

        rename(out + "/output.txt", output_file)

        return


    def simulate(self, testbench, approximate_output):
        '''
        Simulates the actual circuit tree (with deletions)
        Creates an executable using icarus, end then execute it to obtain the
        output of the testbench

        Parameters
        ----------
        testbench : string
            path to the testbench file
        approximate_output : string
            Path to the output file where simulation results will be written.
            The user must provide the full file path and name. If the file
            exists, it will be overwritten.
        '''
        rtl = f"{self.output_folder}/{get_name(5)}.v"
        self.write_to_disk(rtl)

        top = self.topmodule
        tech = "./templates/" + self.tech_file

        # Executable is ran from the testbench folder, because the path to the
        # dataset is relative to the testbench file.
        out = os.path.dirname(testbench)

        """Better to temporarily change cwd when executing iverilog"""
        cwd=os.getcwd()
        current_dir=os.path.dirname(__file__)
        os.chdir(current_dir)

        # - - - - - - - - - - - - - - - Execute icarus - - - - - - - - - - - - -
        # iverilog -l tech.v -o executable testbench.v netlist.v
        kon = f"iverilog -l \"{tech}.v\" -o \"{out}/{top}\" {testbench} \"{rtl}\""
        system(kon)

        # - - - - - - - - - - - - - Execute the testbench  - - - - - - - - - - -
        system(f"cd \"{out}\"; ./{top}")
        os.chdir(cwd)

        rename(out + "/output.txt", approximate_output)

        remove(rtl)
        remove(f"{out}/{top}")


    def simulate_and_compute_error (self, testbench, exact_output, new_output, metric):
        '''
        Simulates the actual circuit tree (with deletions)
        Creates an executable using icarus, end then execute it to obtain the
        output of the testbench

        Parameters
        ----------
        testbench : string
            path to the testbench file
        exact_output : string
            Path to the output file of the original exact circuit to compare
            against. This file can be created with the `exact_output` method.
        new_output : string
            Path to the output file where simulation results will be written.
            The user must provide the full file path and name. If the file
            exists, it will be overwritten.
        metric : string
            equation to compute the error
            options med, wce, wcre,mred, msed

        Returns
        -------
        float
            error of the current circuit tree
        '''
        self.simulate(testbench, new_output)

        error = compute_error(metric, exact_output, new_output)

        return error

    def generate_dataset(self, filename, samples, distribution='uniform', **kwargs):
        '''

        Generates a dataset of randomly distributed data for each input of the circuit.
        By Default, data is written in columns of n-bit hexadecimal numbers, being each column an input and n its bitwidth.
        Will create a `dataset` file in the same folder where the original
        circuit RTL is located.

        Parameters
        ----------
        filename: string
            Path to the output dataset file.
            The user must provide the full file path and name. If the file
            exists, it will be overwritten.
        samples: int
            How many rows of data to generate.
        distribution: string
            The name of the desired random distribution. Could be:
                "gaussian" or "normal" for a normal distribution.
                "uniform" or "rectangular" for a uniform distribution.
                "triangular" for a triangular distribution.
                TODO: Add more distributions

        **kwargs: (optional)

        median: int
            The center of the distribution (works only for certain distributions)
        std: int
            Standard deviation of the destribution (only gaussian/normal distribution)
        limits: int tuple
            Lower and upper limit of the dataset. By default it takes the whole range of numbers: [0,2^n-1]
        format: string
            A format identifier to convert data into a desired base. Could be:
                x for lowercase Hexadecimal (default), use X for uppercase
                d for decimal
                b for binary
                o for octal
        '''


        data=[]

        format=kwargs['format'] if ('format' in kwargs) else 'x'


        '''Get inputs information'''
        inputs_info={}
        for i in self.raw_inputs:
            name=re.search(r' (\S+);', i)
            bits=re.findall(r'[\:[](\d+)', i)

            if bits:
                bitwidth=1+int(bits[0])-int(bits[1])
                inputs_info[name]=bitwidth
            else:
                inputs_info[name]=1

        '''Iterate inputs'''

        for bitwidth in inputs_info.values():
            rows=get_random(bitwidth,distribution,samples, **kwargs)
            format=f'0{bitwidth}b' if format=='b' else format #ensure right number of bits if binary
            data.append([f'{i:{format}}' for i in rows])
        data=list(zip(*data)) # Transpose data see: https://stackoverflow.com/questions/10169919/python-matrix-transpose-and-zip
        np.savetxt(filename,data,fmt='%s')

        return

    def write_tb(self, filename, dataset_file, iterations=None, timescale= '10ns / 1ps', delay=10, format='h', dump_vcd=None, show_progress=True):
        '''
        Writes a basic testbench for the circuit.

        Parameters
        ----------
        filename: string
            Path to the output testbench file.
            The user must provide the full file path and name. If the file
            exists, it will be overwritten.
        dataset_file: string
           Path to the dataset file which can be created with `generate_dataset`.
        iterations (optional): int
            How many iterations to do (how many inputs pass to the circuit, and outputs write to file).
            Requires dataset to be generated, by default it takes the number of rows.
        timescale: string
            A verilog timescale formatted as: timeunit / timeprecision
        delay: int
            Delay in time units. Applied at inputs initialization and after each iteration.
        format: string
            A verilog format string that indicates in which base the input dataset is represented.
                'h' for hexadecimal
                'o' for octal
                'd' for decimal
                'b' for binary
        show_progress: bool, default = True
            Whether the testbench should print its progress as it executes.
        dump_vcd (optional): str
            If provided, executing the testbench will create a vcd file at the
            given path.

        Returns
        -------
            path to generated file
        '''

        '''Check for existing dataset'''
        if iterations is None:
            if os.path.exists(dataset_file):
                file=open(dataset_file, 'r')
                iterations=len(file.read().splitlines())
                file.close()
            else:
                raise FileNotFoundError(f"Dataset file '{dataset_file}' not found. Either create it or manually pass an 'iterations' parameter to Circuit.write_tb.")


        '''Get inputs/outputs information'''
        inputs_info={}
        for i in self.raw_inputs:
            name=re.search(r' (\S+);', i).group(1)
            bits=re.findall(r'[\:[](\d+)', i)

            if bits:
                bitwidth=1+int(bits[0])-int(bits[1])
                inputs_info[name]=bitwidth
            else:
                inputs_info[name]=1

        outputs_info={}

        for o in self.raw_outputs:
            name=re.search(r' (\S+);', o).group(1)
            bits=re.findall(r'[\:[](\d+)', o)

            if bits:
                bitwidth=1+int(bits[0])-int(bits[1])
                outputs_info[name]=bitwidth
            else:
                outputs_info[name]=1

        '''Write the header and module definition'''
        text= f'/* Generated by AxLS */\n' \
              f'`timescale {timescale} \n' \
              f'\n' \
              f'module {self.topmodule}_tb(); \n' \
              f'\n'

        '''Define inputs/outpus reg/wires and variables'''

        for name, bitwidth in zip(outputs_info.keys(), outputs_info.values()):
            if bitwidth==1:
                text= f'{text}wire {name};\n'
            else:
                text= f'{text}wire [{bitwidth-1}:0] {name};\n'


        for name, bitwidth in zip(inputs_info.keys(), inputs_info.values()):
            if bitwidth==1:
                text= f'{text}reg {name};\n'
            else:
                text= f'{text}reg [{bitwidth-1}:0] {name};\n'


        text= f'{text}\n' \
              f'integer i, file, mem, temp;\n' \
              f'\n' \

        '''Instantiate DUT'''
        text= f'{text}{self.topmodule} U0('
        params=self.raw_parameters.split(', ')
        for p in params[0:-1]:
            text= f'{text}{p},'
        text= f'{text}{params[-1]});\n' \
              f'\n' \

        '''Initial statement'''
        text= f'{text}initial begin\n'

        if show_progress:
            text += '$display("-- Beginning Simulation --");\n\n'

        if dump_vcd:
            text=f'{text} $dumpfile("{dump_vcd}");\n' \
                 f' $dumpvars(0,{self.topmodule}_tb);\n'

        relative_dataset_path = os.path.relpath(dataset_file, start=os.path.dirname(filename))

        text=f'{text} file=$fopen("output.txt","w");\n' \
             f' mem=$fopen("{relative_dataset_path}", "r");\n'
        for i in inputs_info.keys():
            text=f'{text} {i} = 0;\n'
        text=f'{text} #{delay}\n' \
             f' for (i=0;i<{iterations};i=i+1) begin\n' \
             f'  temp=$fscanf(mem,"'
        for i in range(len(inputs_info)):
            text=f'{text}%{format} '
        text=f'{text}\\n"'
        for i in inputs_info.keys():
            text=f'{text},{i}'
        text=f'{text});\n' \
             f'  #{delay}\n' \
             f'  $fwrite(file, "'
        for o in range(len(outputs_info.keys())):
            text=f'{text}%d\\n '
        text=f'{text}",'
        for o in list(outputs_info.keys())[::-1][0:-1]:
            text= f'{text}{o},'
        text= f'{text}{list(outputs_info.keys())[0]});\n'

        if show_progress:
            text +=f'  $display("-- Progress: %d/{iterations} --",i+1);\n'

        text = f'{text}end\n' \
              f' $fclose(file);\n' \
              f' $fclose(mem);\n' \
              f' $finish;\n' \
              f'end\n' \
              f'endmodule\n'

        with open(os.path.join(filename), 'w') as file:
            file.write(text)
            file.close()

        return

    def generate_saif_from_vcd(
        self, saif: str, vcd_file_path: str, verbose: bool = False
    ) -> None:
        """
        Generates a SAIF file from a vcd file. A vcd file can be created by
        running a simulation with a testbench that was created by created by
        `write_tb` with a `dump_vcd` parameter.

        The SAIF file is then parsed and the netlist annotated with execution
        data.

        Parameters
        ----------
        saif: string
            Path to the saif file generated.
        vcd_file_path: string
            Path to the vcd file.
            The user must provide the full file path and name. If the file
            exists, it will be overwritten.
        verbose: bool
            Whether to print verbose output
        """
        saifversion = "2.0"
        direction = "backward"
        design = self.topmodule
        vendor = "AxPy Inc"
        program_name = "open_vcd2saif"
        version = "v0"
        divider = "/ "
        timescale = "1 ps"

        # 1st pass: get variables
        var_list = []
        level = 0

        count = 0
        total = 0

        def file_read(filename):
            for row in open(filename, "r"):
                yield row.split("\n")[0]

        vcd_file = file_read(vcd_file_path)

        for line in vcd_file:
            search = re.search(r"\$scope", line)
            if search is not None:
                ls = line.split()
                parent = ls[2]
                level += 1
                continue

            search = re.search(r"\$upscope", line)
            if search is not None:
                level -= 1
                continue

            search = re.search(r"\$var", line)
            if search is not None:
                ls = line.split()
                name = ls[4]
                alias = ls[3]
                var_len = int(ls[2])
                m = re.findall(r"\d+", ls[5])
                flag_mult = 0
                if len(m) == 2:
                    n0 = int(m[1])
                    flag_mult = 1
                elif len(m) == 1:
                    n0 = int(m[0])
                    flag_mult = 1
                else:
                    n0 = 1

                if var_len == 1:
                    var_list.append(
                        {
                            "name": name,
                            "alias": alias,
                            "parent": parent,
                            "level": level,
                            "len": 1,
                            "bit_index": n0,
                            "multi_bit": flag_mult,
                            "high": 0,
                            "low": 0,
                            "x": 0,
                            "ig": 0,
                            "last": "2",
                            "toggle": 0,
                        }
                    )
                else:
                    for i in range(var_len):
                        var_list.append(
                            {
                                "name": name,
                                "alias": alias,
                                "parent": parent,
                                "level": level,
                                "len": var_len,
                                "bit_index": i,
                                "multi_bit": flag_mult,
                                "high": 0,
                                "low": 0,
                                "x": 0,
                                "ig": 0,
                                "last": "2",
                                "toggle": 0,
                            }
                        )
                continue
            if verbose:
                count += 1
                print(f"Pass #1: {count}/{total}")

        # 2nd pass: get values
        time_step = 0
        last_step = 0

        count = 0
        vcd_file = file_read(vcd_file_path)

        for line in vcd_file:
            if line != "":
                if line[0] == "#":
                    time_step = int(line[1:])

                    # print('Time step: %d' % time_step)
                    time_diff = time_step - last_step
                    for var in var_list:
                        if var["last"] == "1":
                            var["high"] += time_diff
                        elif var["last"] == "0":
                            var["low"] += time_diff
                        elif var["last"] == "x":
                            var["x"] += time_diff
                    last_step = time_step

                elif line[0] == "b" and line[1] != "x":
                    val, alias = line.split()
                    val_len = len(val[1:])

                    bit_index = val_len - 1
                    for bit_char in val[1:]:
                        bit_val = bit_char
                        for var in var_list:
                            if alias == var["alias"]:
                                templateSize = "{0:0%db}" % (var["len"])
                                word = templateSize.format(int(val[1:], 2))
                                rev_word = word[::-1]
                                if (
                                    var["last"] != "2"
                                    and var["last"] != rev_word[var["bit_index"]]
                                ):
                                    var["toggle"] += 1
                                var["last"] = rev_word[var["bit_index"]]

                        bit_index -= 1

                elif line[0] == "0" or line[0] == "1" or line[0] == "x":
                    bit_val = line[0]
                    alias = line[1:]
                    for var in var_list:
                        if alias == var["alias"] and var["len"] == 1:
                            if var["last"] != "2" and var["last"] != bit_val:
                                var["toggle"] += 1
                            var["last"] = bit_val
            if verbose:
                count += 1
                print(f"Pass #2: {count}/{total}")

        duration = time_step - 1
        # 3rd pass: write file

        text_level = 0
        level = 0

        count = 0
        vcd_file = file_read(vcd_file_path)

        def get_time_stamp():
            now = datetime.datetime.now()
            year = '{:02d}'.format(now.year)
            month = '{:02d}'.format(now.month)
            day = '{:02d}'.format(now.day)
            hour = '{:02d}'.format(now.hour)
            minute = '{:02d}'.format(now.minute)
            second = '{:02d}'.format(now.second)
            date_string = '{}-{}-{} {}:{}:{}'.format(month, day, year, hour, minute, second)
            return date_string

        saifile = open(saif, "w")

        saifile.write("(SAIFILE\n")
        saifile.write('(SAIFVERSION "%s")\n' % saifversion)
        saifile.write('(DIRECTION "%s")\n' % direction)
        saifile.write('(DESIGN "%s")\n' % design)
        saifile.write('(DATE "%s")\n' % get_time_stamp())
        saifile.write('(VENDOR "%s")\n' % vendor)
        saifile.write('(PROGRAM_NAME "%s")\n' % program_name)
        saifile.write('(VERSION "%s")\n' % version)
        saifile.write("(DIVIDER %s)\n" % divider)
        saifile.write("(TIMESCALE %s)\n" % timescale)
        saifile.write("(DURATION %ld)\n" % duration)

        def saif_indent_level(level):
            space = ''
            for _ in range(level):
                space += '  '
            return space

        for line in vcd_file:
            search = re.search(r"\$scope", line)
            if search is not None:
                ls = line.split()
                name = ls[2]
                saifile.write(
                    "%s(INSTANCE %s\n" % (saif_indent_level(text_level), name)
                )
                text_level += 1
                level += 1
                saifile.write("%s(NET\n" % (saif_indent_level(text_level)))
                text_level += 1

                # put variables
                for var in var_list:
                    if var["parent"] == name and var["level"] == level:
                        if var["multi_bit"] == 0:
                            saifile.write(
                                "%s(%s\n" % (saif_indent_level(text_level), var["name"])
                            )
                        else:
                            saifile.write(
                                "%s(%s\\[%d\\]\n"
                                % (
                                    saif_indent_level(text_level),
                                    var["name"],
                                    var["bit_index"],
                                )
                            )

                        saifile.write(
                            "%s  (T0 %d) (T1 %d) (TX %d)\n"
                            % (
                                saif_indent_level(text_level),
                                var["low"],
                                var["high"],
                                var["x"],
                            )
                        )

                        saifile.write(
                            "%s  (TC %d) (IG %d)\n"
                            % (saif_indent_level(text_level), var["toggle"], var["ig"])
                        )

                        saifile.write("%s)\n" % (saif_indent_level(text_level)))

                text_level -= 1
                saifile.write("%s)\n" % (saif_indent_level(text_level)))
                continue

            search = re.search(r"\$upscope", line)
            if search is not None:
                text_level -= 1
                level -= 1
                saifile.write("%s)\n" % (saif_indent_level(text_level)))

            if verbose:
                count += 1
                print(f"Pass #3: {count}/{total}")

        saifile.write(")\n")
        saifile.close()

        self.saif_parser(saif)

    def resynth(self):
        '''
        Calls resynthesis function to reduce circuit structure using logic synthesis optimizations/mapping

        :return: path-like string
            path to resynthetized file
        '''
        rtl = f"{self.output_folder}/{get_name(5)}.v"
        self.write_to_disk(rtl)

        self.netl_file =resynthesis(rtl,self.tech_file,self.topmodule)

        netlist = Netlist(self.netl_file, self.technology)
        self.netl_root = netlist.root
        self.inputs = netlist.circuit_inputs
        self.outputs = netlist.circuit_outputs
        self.raw_inputs = netlist.raw_inputs
        self.raw_outputs = netlist.raw_outputs
        self.raw_parameters = netlist.raw_parameters

        os.remove(rtl)

        return self.netl_file

    def get_area(self, method = 'yosys'):
        '''
        Calls yosys script to estimate circuit area
        Add here any other method for area estimation implemented in the future

        :return: string
            area estimation value
        '''

        if method == 'yosys':
            rtl = f"{self.output_folder}/{get_name(5)}.v"
            self.write_to_disk(rtl)
            area=ys_get_area(rtl,self.tech_file,self.topmodule)
            os.remove(rtl)

            return area
        else:
            raise ValueError(f'{method} is not a valid/implemented area estimation method')
