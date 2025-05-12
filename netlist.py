import re
import xml.etree.cElementTree as ET


class NetlistNode:

    def __init__ (self, name, var):
        self.name = name
        self.var = var
        self.inputs = {}
        self.outputs = {}

    def addInput (self, input_name, input_value):
        self.inputs[input_name] = input_value

    def addOutput (self, output_name, output_value):
        self.outputs[output_name] = output_value


class Netlist:
    '''
    Representation of a verilog circuit

    Attributes
    ----------
    nodes : list

    root : ElementTree.Element
        root element of the circuit tree
    circuit_inputs : list
        list of the circuit inputs
    circuit_outputs : list
            list of the circuit inputs
    '''


    def __init__(self, netl_file, technology):
        '''
        Creates a Netlist object parsing the circuit from the netl_file and the
        modules of the technology library file

        Parameters
        ----------
        netl_file : string
            path to the netlist file
        technology : Technology
            list of tecnology libraries modules
        '''
        self.nodes = []
        self.assignments=[] #Special assignments, like constant outputs

        with open(netl_file, 'r') as circuit_file:
            content = circuit_file.read()

        self.raw_outputs, self.circuit_outputs = self.get_outputs(content)
        self.raw_inputs, self.circuit_inputs = self.get_inputs(content)

        expreg = r'module [a-zA-Z0-9_]*\s*\(([\s\S]+?)\);'
        parameters = re.search(expreg,content)
        self.raw_parameters = re.sub('\n','',parameters.group(1))

        assigns = parse_assigns(content)
        for a in assigns:
            self.assignments.append(a)

        # iterate over every instanced module
        expreg = r'([a-zA-Z0-9_]+) (.+) \(([\n\s\t.a-zA-Z0-9\(\[\]\),_]*)\);'
        instances = re.findall(expreg,content)
        for variable in instances:

            # FIRST: we get the instanciated cell name and parameters
            cell_name = variable[0]
            var = variable[1]
            parameters = variable[2].replace("\n","").replace(" ","")

            # SECOND: we get the cell information from the technology library
            # children input/output from cells with name='xxx'
            cell_inputs = technology.root.findall(
                f"./cell[@name='{cell_name}']/input")

            cell_outputs = technology.root.findall( \
                f"./cell[@name='{cell_name}']/output")

            # we are going to create our AST node object
            node = NetlistNode (cell_name, var)

            # THIRD: now we iterate over the parameters to know which of them
            # are inputs or outputs
            expreg2 = r'\.([^(,|\n)]+)\(([^(,|\n)]+)\)'
            params = re.findall(expreg2,parameters)
            for param in params:
                param_name = param[0]
                param_wire = param[1]

                # FOURTH: we are going to check if param is an input or output
                found = False
                for i in cell_inputs:
                    if param_name == i.text:
                        node.addInput (param_name, param_wire)
                        found = True
                for o in cell_outputs:
                    if param_name == o.text:
                        node.addOutput (param_name, param_wire)
                        found = True
                if (not found):
                    print ("[ERROR] no input or output for param: " + \
                        param_name + " at cell " + var + ' ' + cell_name)


            self.nodes.append(node)

        self.root = self.to_xml()


    def to_xml(self):
        '''
        Convert the circuit node list into a xml structure tree

        Returns
        -------
        ElementTree.Element
            references to the root element of the circuit nodes tree

        '''
        root = ET.Element("root")


        for n in self.nodes:
            node = ET.SubElement(root, "node")
            node.set('name',n.name)
            node.set('var',n.var)
            for key, value in n.inputs.items():
                input_element = ET.SubElement(node, "input")
                input_element.set('name', key)
                input_element.set('wire', value)
            for key, value in n.outputs.items():
                output_element = ET.SubElement(node, "output")
                output_element.set('name', key)
                output_element.set('wire', value)

        circuitinputs = ET.SubElement(root, "circuitinputs")
        circuitoutputs = ET.SubElement(root, "circuitoutputs")
        circuitassignments=ET.SubElement(root,'assignments')

        for o in self.circuit_outputs:
            output_element = ET.SubElement(circuitoutputs, "output")
            output_element.set('var', o)
        for i in self.circuit_inputs:
            input_element = ET.SubElement(circuitinputs, "input")
            input_element.set('var', i)
        for a in self.assignments:
            assignment_element=ET.SubElement(circuitassignments,"assign")
            assignment_element.set('var',a[0])
            assignment_element.set('val',a[1])

        return root


    def get_inputs(self, netlist_rtl):
        '''
        Extracts the input variables of the circuit
        TODO: support one bit variables

        Parameters
        ----------
        netlist_rtl : string
            content of the netlist file

        Returns
        -------
        array
            list of circuit intputs
        '''
        raw_inputs = []
        circuit_inputs = []
        inputs = re.findall(
            r'input\s*(\[([0-9]*):([0-9]*)\])*\s*([a-zA-Z0-9]*)',netlist_rtl)
        for i in inputs:
            if i[0] != '':
                left = int(i[1])
                right = int(i[2])
                if (left > right):
                    for x in range(right,left+1):
                        circuit_inputs.append(i[3]+'['+str(x)+']')
                else:
                    for x in range(left,right+1):
                        circuit_inputs.append(i[3]+'['+str(x)+']')
                raw_inputs.append(f"input [{i[1]}:{i[2]}] {i[3]};")
            else:
                circuit_inputs.append(f"{i[3]}")
                raw_inputs.append(f"input {i[3]};")
        return raw_inputs, circuit_inputs


    def get_outputs(self, netlist_rtl):
        '''
        Extracts the output variables of the circuit
        TODO: support one bit variables

        Parameters
        ----------
        netlist_rtl : string
            content of the netlist file

        Returns
        -------
        array
            list of circuit outputs
        '''
        raw_outputs = []
        circuit_outputs = []
        outputs = re.findall(
            r'output\s*(\[([0-9]*):([0-9]*)\])*\s*([a-zA-Z0-9]*)',netlist_rtl)
        for o in outputs:
            if o[0] != '':
                left = int(o[1])
                right = int(o[2])
                if (left > right):
                    for x in range(right,left+1):
                        circuit_outputs.append(f"{o[3]}[{str(x)}]")
                else:
                    for x in range(left,right+1):
                        circuit_outputs.append(f"{o[3]}[{str(x)}]")
                raw_outputs.append(f"output [{o[1]}:{o[2]}] {o[3]};")
            else:
                circuit_outputs.append(f"{o[3]}")
                raw_outputs.append(f"output {o[3]};")
        return raw_outputs, circuit_outputs

def expand_range(name):
    '''
    Expands a Verilog-style bit range expression into a list of individual bits.

    Parameters
    ----------
    name : string
        A string like "a[3:0]" or "b[7]".

    Returns
    -------
    List[string]
        A list of strings like ["a[3]", "a[2]", "a[1]", "a[0]"].

    Examples
    -------
        >>> expand_range("a[3:1]")
        ['a[3]', 'a[2]', 'a[1]']

        >>> expand_range("x[1:3]")
        ['x[1]', 'x[2]', 'x[3]']

        >>> expand_range("y[5]")
        ['y[5]']

        >>> expand_range("z")
        ['z']
    '''
    m = re.match(r'(\w+)\[(\d+):(\d+)\]', name)
    if not m:
        return [name]
    var, hi, lo = m.groups()
    hi, lo = int(hi), int(lo)
    step = -1 if hi > lo else 1
    return [f"{var}[{i}]" for i in range(hi, lo + step, step)]

def expand_concat(expr):
    '''
    Expands a Verilog-style concatenation expression into a flat list of
    individual bits.

    Parameters
    ----------
    expr : string
        A Verilog signal, range, or concatenation like "{a[3:0], b[1], c}".

    Returns
    -------
    List[string]
        A list of strings like ["a[3]", "a[2]", "a[1]", "a[0]", "b[1]", "c"].

    Examples
    -------
        >>> expand_concat("{ a[2:1], b[0] }")
        ['a[2]', 'a[1]', 'b[0]']

        >>> expand_concat("{ x[1], y[3:2], z }")
        ['x[1]', 'y[3]', 'y[2]', 'z']

        >>> expand_concat("a[3]")
        ['a[3]']

        >>> expand_concat("b[1:0]")
        ['b[1]', 'b[0]']
    '''
    expr = expr.strip()
    if expr.startswith('{') and expr.endswith('}'):
        inner = expr[1:-1]
        parts = [p.strip() for p in inner.split(',')]
        bits = []
        for p in parts:
            bits.extend(expand_range(p))
        return bits
    else:
        return expand_range(expr)

def parse_assigns(content):
    '''
    Parses Verilog assign statements and expands any bit ranges into individual
    assignments.

    The following cases can result in `assign`s:
        - Inputs mapped directly to outputs
        - Ports mapped to wires by Yosys
        - Constant assignments in resynth

    Parameters
    ----------
    content : string
        A string containing one or more Verilog assign statements.

    Returns
    -------
    List[Tuple[string, string]]
        A list of (lhs, rhs) assignment pairs, one for each individual bit.

    Examples
    -------
        >>> code = """
        ... assign a[2] = b[2];
        ... assign foo[1:0] = bar[3:2];
        ... assign x = 0;
        ... assign { out[4:3], out[0:1] } = { in1[3], in2[1:0], in3[2] };
        ... """
        >>> parse_assigns(code)
        [('a[2]', 'b[2]'),
         ('foo[1]', 'bar[3]'), ('foo[0]', 'bar[2]'),
         ('x', '0'),
         ('out[4]', 'in1[3]'), ('out[3]', 'in2[1]'), ('out[0]', 'in2[0]'), ('out[1]', 'in3[2]')
        ]

    TODO: This method can't handle range or concatenated assignments to full
    variables. For example in the following case it will cause a "Bit width
    mismatch" error even if `out` is a 4 bit variable, because it doesn't know
    that:

        assign out = { in1[0:1], in2[0:1] }
    '''
    expreg = r'assign\s+(.*?)\s*=\s*(.*?);'
    assigns = re.findall(expreg, content)
    result = []
    for lhs, rhs in assigns:
        lhs_bits = expand_concat(lhs)
        rhs_bits = expand_concat(rhs)
        if len(lhs_bits) != len(rhs_bits):
            raise ValueError(f"Bit width mismatch: LHS {lhs_bits} != RHS {rhs_bits}")
        result.extend(zip(lhs_bits, rhs_bits))
    return result
