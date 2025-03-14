
import datetime
import os
import re
import sys

from graphviz import Digraph
from os import path, remove, system, rename
from random import randint
from re import sub, findall
import xml.etree.ElementTree as ET

from circuiterror import compute_error
from netlist import Netlist
from synthesis import synthesis, resynthesis, ys_get_area
from technology import Technology
from utils import get_name, get_random
import re
import numpy as np





class Circuit:
    '''
    Representation of a sintetized rtl circuit

    Attributes
    -----------
    rtl_file : str
        path to the circuit rtl file
    tech_file : str
        name of the technology library used to map the circuit
    topmodule : str
        name of the circuit we want to sintetize
    netl_file : str
        path of the sintetized netlist file
    tech_root : ElementTree.Element
        references to the root element of the Technology Library Cells tree
    '''


    def __init__(self, rtl, tech, saif = ""):
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
        '''


        self.rtl_file = rtl
        self.tech_file = tech
        self.topmodule = rtl.split('/')[-1].replace(".v","")
        self.netl_file = synthesis (rtl, tech, self.topmodule)
        self.technology = Technology(tech)
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
        if (node_to_delete != None):
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
        if (node_to_delete != None):
            node_to_delete.attrib.pop("delete")
        else:
            print(f"Node {node_var} not found")

    # this are some auxiliary functions for write_to_disk

    def is_node_deprecable(self, node):
        '''
        Check if a node can be deleted if it does not has children or all
        their children will be deleted too. If there are still some children
        the wire is going to be assigned to a constant

        Parameters
        ----------
        node : ElementTree.Element
            node we want to examine

        Returns
        -------
        boolean
            true if the node is deprecable
        '''

        root = self.netl_root

        node_output = node.findall("output")[0]
        wire = node_output.attrib["wire"]

        # children of node
        re = f"./node/input[@wire='{wire}']/.."
        just_children = root.findall(re)

        # children of node that had to be deleted too
        re = f"./node[@delete='yes']/input[@wire='{wire}']/.."
        node_children = root.findall(re)

        # if there are no children or all the children will be deleted too,
        # the node is deprecable and the wire needs to be ASSIGNED
        return len(just_children)==0 or len(node_children) < len(just_children)


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
        wires = [wire for wire in wires if not wire in self.inputs]
        wires = [wire for wire in wires if not wire in self.outputs]
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
        another list with the wires that will be grounded

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
            if self.is_node_deprecable(node):
                # the wire need to be ASSIGNED
                wire = node_output.attrib["wire"]
                constant = self.node_to_constant(node)
                wires_to_be_assigned[wire] = constant
            else:
                # the wire could be DELETED
                wire = node_output.attrib["wire"]
                wires_to_be_deleted.append(wire)
        return wires_to_be_deleted, wires_to_be_assigned



    def write_to_disk (self, filename=""):
        '''
        Write the xml circuit into a netlist file considering the nodes to be
        deleted (marked with an attribute delete='yes')

        Returns
        -------
        string
            path of the recently created netlist
        '''

        def format_io(node, io):
            ioputs = node.findall(f"{io}put")
            return [f".{x.attrib['name']}({x.attrib['wire']})" for x in ioputs]

        nodes_to_delete = self.get_nodes_to_delete()
        to_be_deleted, to_be_assigned = self.get_wires_to_be_deleted()

        filename = filename if filename != "" else str(randint(9999,999999))
        filepath = f"{self.output_folder}{path.sep}{filename}.v"

        with open(filepath, 'w') as netlist_file:

            def writeln(file, text):
                file.write(text + "\n")

            header = "/* Generated by poisonoak */"
            writeln(netlist_file, header)

            inputs = ','.join(set([i.split('[')[0] for i in self.inputs]))
            outputs = ','.join(set([o.split('[')[0] for o in self.outputs]))
            params = self.raw_parameters
            module = f"module {self.topmodule} ({params});"
            writeln(netlist_file, module)

            for wire in self.get_circuit_wires():
                if not wire in to_be_deleted:
                    writeln(netlist_file, f"\twire {wire};")
            used_outputs=[]
            for output in self.raw_outputs:
                if not (output in used_outputs):
                    writeln(netlist_file, "\t" + output)
                    used_outputs.append(output)
            for output in self.raw_inputs:
                if not (output in used_outputs):
                    writeln(netlist_file, "\t" + output)
                    used_outputs.append(output)

            for node_var in self.get_circuit_nodes():
                if not node_var in nodes_to_delete:
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
        return filepath


    def show (self, show_deletes=False, view=True):
        '''
        Displays the circuit as a graph

        Parameters
        ----------
        show_deletes : boolean
            nodes to be deleted will be colored in red
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

        name = f"{self.output_folder}{path.sep}{self.topmodule}"
        f.render(filename=name, view=view)
        return(f.render(filename=name, format='png'))



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

            expreg = r'\((.+)\n.*\(T0 ([0-9]+)\).*' + \
                '\(T1 ([0-9]+)\).*\n.*\(TC ([0-9]+)\).*\n.*\)'
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

                    if (cells != None):
                    	cells.set('t0',saif_cell_t0)
                    	cells.set('t1',saif_cell_t1)
                    	cells.set('tc',saif_cell_tc)

                elif ((saif_cell_name[0],saif_cell_name[-1]) == ("_","_")): #Yosys 19.
                    my_saif_cell_name = "_" + saif_cell_name[1:-1] + "_"
                    cells = self.netl_root.find(f"./node/output[@wire='{my_saif_cell_name}']")

                    if (cells != None):
                    	cells.set('t0',saif_cell_t0)
                    	cells.set('t1',saif_cell_t1)
                    	cells.set('tc',saif_cell_tc)

                elif (saif_cell_name.replace('\\','') in self.outputs):
                    my_saif_cell_name = saif_cell_name.replace('\\','')
                    cells = self.netl_root.find(f"./node/output[@wire='{my_saif_cell_name}']")

                    if (cells != None):
                    	cells.set('t0',saif_cell_t0)
                    	cells.set('t1',saif_cell_t1)
                    	cells.set('tc',saif_cell_tc)

        return saif
    def exact_output (self, testbench):
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
        orig_output : string
            path to the original results of the circuit
        new_output : string
            path to the new results file created after the simulation
        clean : bool
            if true, deletes all the generated files

        Returns
        -------
        float
            error of the current circuit tree
        '''


        name = get_name(5)
        rtl = self.write_to_disk(name)

        top = self.topmodule
        current_dir=os.path.dirname(__file__)
        tech = f"{current_dir}/templates/" + self.tech_file
        out = self.output_folder

        """Better to temporarily change cwd when executing iverilog"""
        cwd=os.getcwd()
        os.chdir(current_dir)

        # - - - - - - - - - - - - - - - Execute icarus - - - - - - - - - - - - -
        # iverilog -l tech.v -o executable testbench.v netlist.v
        kon = f"iverilog -l \"{tech}.v\" -o \"{out}/{top}\" {testbench} \"{rtl}\""
        result = system(kon)

        # - - - - - - - - - - - - - Execute the testbench  - - - - - - - - - - -
        result = system(f"cd \"{out}\"; ./{top}")

        os.chdir(cwd)

        remove(rtl)
        remove(f"{out}/{top}")
        rename(out + "/output.txt", out + "/output0.txt")


        return f'{out}/output0.txt'

    def simulate (self, testbench, metric, orig_output, new_output):
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
        orig_output : string
            path to the original results of the circuit
        new_output : string
            path to the new results file created after the simulation
        clean : bool
            if true, deletes all the generated files

        Returns
        -------
        float
            error of the current circuit tree
        '''


        name = get_name(5)
        rtl = self.write_to_disk(name)

        top = self.topmodule
        tech = "./templates/" + self.tech_file
        out = self.output_folder

        """Better to temporarily change cwd when executing iverilog"""
        cwd=os.getcwd()
        current_dir=os.path.dirname(__file__)
        os.chdir(current_dir)

        # - - - - - - - - - - - - - - - Execute icarus - - - - - - - - - - - - -
        # iverilog -l tech.v -o executable testbench.v netlist.v
        kon = f"iverilog -l \"{tech}.v\" -o \"{out}/{top}\" {testbench} \"{rtl}\""
        #print(kon)
        result = system(kon)

        # - - - - - - - - - - - - - Execute the testbench  - - - - - - - - - - -
        result = system(f"cd \"{out}\"; ./{top}")
        os.chdir(cwd)

        error = compute_error(metric, orig_output, new_output)

        remove(rtl)
        remove(f"{out}/{top}")

        return error

    def generate_dataset(self, samples, distribution='uniform', **kwargs):
        '''

        Generates a dataset of randomly distributed data for each input of the circuit.
        By Default, data is written in columns of n-bit hexadecimal numbers, being each column an input and n its bitwidth.

        Parameters
        ----------
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
        Returns
        -------
            path to the generated dataset
        '''


        dataset=''
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
        file=np.savetxt(f'{self.output_folder}/dataset',data,fmt='%s')

        return f'{self.output_folder}/dataset'

    def write_tb(self, iterations=None, timescale= '10ns / 1ps', delay=10, format='h', dump_vcd=False):
        '''
        Writes a basic testbench for the circuit. See template in ./templates/testbench
        Parameters
        ----------
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

        Returns
        -------
            path to generated file
        '''

        '''Check for existing dataset'''
        if os.path.exists(f'{self.output_folder}/dataset') and iterations==None:
            file=open(f'{self.output_folder}/dataset', 'r')
            iterations=len(file.read().splitlines())
            file.close()


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
        text= f'{text}initial begin\n $display("-- Beginning Simulation --");\n\n'
        if dump_vcd:
            text=f'{text} $dumpfile("./{self.topmodule}.vcd");\n' \
                 f' $dumpvars(0,{self.topmodule}_tb);\n'
        text=f'{text} file=$fopen("output.txt","w");\n' \
             f' mem=$fopen("dataset", "r");\n'
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
        text= f'{text}{list(outputs_info.keys())[0]});\n'\
            + f'  $display("-- Progress: %d/{iterations} --",i+1);\n'\
              f' end\n' \
              f' $fclose(file);\n' \
              f' $fclose(mem);\n' \
              f' $finish;\n' \
              f'end\n' \
              f'endmodule\n'

        with open(os.path.join(f'{self.output_folder}/{self.topmodule}_tb.v'), 'w') as file:
            file.write(text)
            file.close()

        return file.name

    def resynth(self):
        '''
        Calls resynthesis function to reduce circuit structure using logic synthesis optimizations/mapping

        :return: path-like string
            path to resynthetized file
        '''
        name=get_name(5)
        self.netl_file =resynthesis(self.write_to_disk(name),self.tech_file,self.topmodule)

        netlist = Netlist(self.netl_file, self.technology)
        self.netl_root = netlist.root
        self.inputs = netlist.circuit_inputs
        self.outputs = netlist.circuit_outputs
        self.raw_inputs = netlist.raw_inputs
        self.raw_outputs = netlist.raw_outputs
        self.raw_parameters = netlist.raw_parameters

        os.remove(f'{self.output_folder}/{name}.v')

        return self.netl_file

    def get_area(self, method = 'yosys'):
        '''
        Calls yosys script to estimate circuit area
        Add here any other method for area estimation implemented in the future

        :return: string
            area estimation value
        '''

        if method == 'yosys':
            name=get_name(5)
            area=ys_get_area(self.write_to_disk(name),self.tech_file,self.topmodule)
            os.remove(f'{self.output_folder}/{name}.v')

            return area
        else:
            raise ValueError(f'{method} is not a valid/implemented area estimation method')
