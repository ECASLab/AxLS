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

        expreg = r'module [a-zA-Z0-9_]*\s*\(([\s\S]+?)\);'
        parameters = re.search(expreg,content)
        self.raw_parameters = re.sub('\n','',parameters.group(1))

        self.raw_outputs, self.circuit_outputs = self.get_outputs(content, self.raw_parameters)
        self.raw_inputs, self.circuit_inputs = self.get_inputs(content, self.raw_parameters)

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

    def get_inputs(self, netlist_rtl, raw_parameters):
        """
        Extracts the circuit's input variables.

        Inputs are returned in two ways:
        - `circuit_inputs`: expanded, sorted MSB→LSB, and follow the order in `raw_parameters`.
        - `raw_inputs`: unexpanded lines, sorted to match the same order.

        This ordering ensures compatibility with Verilog-generating methods like
        the Decision Tree, which expect to receive bit-accurate and positionally
        correct inputs in order to replicate them.

        TODO: support one bit variables

        Parameters
        ----------
        netlist_rtl : str
            Content of the netlist file.
        raw_parameters : str
            Module's parameter list string.

        Returns
        -------
        tuple[list[str], list[str]]
            raw_inputs and circuit_inputs
        """
        raw_inputs = []
        circuit_inputs = []
        inputs = re.findall(
            r"input\s*(\[([0-9]*):([0-9]*)\])*\s*([a-zA-Z0-9]*)", netlist_rtl
        )
        for i in inputs:
            if i[0] != "":
                left = int(i[1])
                right = int(i[2])
                if left > right:
                    for x in range(left, right - 1, -1):
                        circuit_inputs.append(i[3] + "[" + str(x) + "]")
                else:
                    for x in range(left, right + 1):
                        circuit_inputs.append(i[3] + "[" + str(x) + "]")
                raw_inputs.append(f"input [{i[1]}:{i[2]}] {i[3]};")
            else:
                circuit_inputs.append(f"{i[3]}")
                raw_inputs.append(f"input {i[3]};")

        circuit_inputs = sort_expanded_vars(circuit_inputs, raw_parameters)
        raw_inputs = sort_raw_vars(raw_inputs, raw_parameters)
        return raw_inputs, circuit_inputs

    def get_outputs(self, netlist_rtl, raw_parameters):
        """
        Extracts the circuit's output variables.

        Outputs are returned in two ways:
        - `circuit_outputs`: expanded, sorted MSB→LSB, and follow the order in `raw_parameters`.
        - `raw_outputs`: unexpanded lines, sorted to match the same order.

        This ordering ensures compatibility with Verilog-generating methods like
        the Decision Tree, which expect to receive bit-accurate and positionally
        correct inputs in order to replicate them.

        TODO: support one bit variables

        Parameters
        ----------
        netlist_rtl : string
            content of the netlist file
        raw_parameters : str
            Module's parameter list string.


        Returns
        -------
        tuple[list[str], list[str]]
            raw_outputs and circuit_outputs
        """
        raw_outputs = []
        circuit_outputs = []
        outputs = re.findall(
            r"output\s*(\[([0-9]*):([0-9]*)\])*\s*([a-zA-Z0-9]*)", netlist_rtl
        )
        for o in outputs:
            if o[0] != "":
                left = int(o[1])
                right = int(o[2])
                if left > right:
                    for x in range(left, right - 1, -1):
                        circuit_outputs.append(f"{o[3]}[{str(x)}]")
                else:
                    for x in range(left, right + 1):
                        circuit_outputs.append(f"{o[3]}[{str(x)}]")
                raw_outputs.append(f"output [{o[1]}:{o[2]}] {o[3]};")
            else:
                circuit_outputs.append(f"{o[3]}")
                raw_outputs.append(f"output {o[3]};")

        circuit_outputs = sort_expanded_vars(circuit_outputs, raw_parameters)
        raw_outputs = sort_raw_vars(raw_outputs, raw_parameters)
        return raw_outputs, circuit_outputs


def expand_concat(expr):
    """
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
    """
    expr = expr.strip()
    if expr.startswith("{") and expr.endswith("}"):
        inner = expr[1:-1]
        parts = [p.strip() for p in inner.split(",")]
        bits = []
        for p in parts:
            bits.extend(expand_range(p))
        return bits
    else:
        return expand_range(expr)


def expand_range(expr):
    """
    Expands a Verilog-style range expression into a flat list of individual bits
    or constants.

    Parameters
    ----------
    name : string
        A Verilog signal, range or constant

    Returns
    -------
    List[string]
        A list of strings or bits.

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

        >>> expand_range("4'hd")
        [1, 1, 0, 1]
    """
    expr = expr.strip()
    if "'" in expr:
        return expand_constant(expr)
    elif "[" in expr:
        if ":" in expr:
            base, range_part = expr.split("[")
            range_part = range_part[:-1]
            start, end = map(int, range_part.split(":"))
            step = -1 if start > end else 1
            return [f"{base}[{i}]" for i in range(start, end + step, step)]
        else:
            return [expr]
    else:
        return [expr]


def expand_constant(expr):
    """
    Expands a Verilog-style constant variable expression into a flat list of
    individual bits.

    Parameters
    ----------
    expr : string
        A Verilog constant like "3'h6". Currently only supports hexadecimal
        expressions, but that should be enough since that's how yosys assigns
        constants.

    Returns
    -------
    List[int]
        A list of bits like [1, 1, 0].

    Examples
    -------
        >>> expand_constant("1'h1")
        [1]

        >>> expand_constant("4'hd")
        [1, 1, 0, 1]
    """
    size, value = expr.split("'h")
    size = int(size)
    value = value.lower()

    int_value = int(value, 16)

    bits = [(int_value >> i) & 1 for i in range(size - 1, -1, -1)]

    return bits


def parse_assigns(content):
    '''
    Parses Verilog assign statements and expands any bit ranges into individual
    assignments.

    The following cases can result in `assign`s:
        - Inputs mapped directly to outputs
        - Ports mapped to wires by Yosys
        - Constant assignments in resynth

    If the LHS is a full variable and the RHS is a concatenation or range with
    multiple bits, the LHS is automatically expanded to match the RHS
    bit width. For example:

        assign out = { a[1], b[0] }

    ...will produce:

        [('out[1]', 'a[1]'),
         ('out[0]', 'b[0]')]

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
        ... assign out = { in1[0:1], in2[0:1] }
        ... """
        >>> parse_assigns(code)
        [('a[2]', 'b[2]'),
         ('foo[1]', 'bar[3]'), ('foo[0]', 'bar[2]'),
         ('x', '0'),
         ('out[4]', 'in1[3]'), ('out[3]', 'in2[1]'), ('out[0]', 'in2[0]'), ('out[1]', 'in3[2]'),
         ('out[3]', 'in1[0]'), ('out[2]', 'in1[1]'), ('out[1]', 'in2[1]'), ('out[0]', 'in2[0]')
        ]
    '''
    expreg = r"assign\s+(.*?)\s*=\s*(.*?);"
    assigns = re.findall(expreg, content)
    result = []
    for lhs, rhs in assigns:
        lhs_bits = expand_concat(lhs)
        rhs_bits = expand_concat(rhs)

        # if LHS is a single bare name but RHS is wide, expand LHS to match
        if len(lhs_bits) == 1 and lhs_bits[0] == lhs and len(rhs_bits) > 1:
            width = len(rhs_bits)
            # msb = width-1 down to 0
            lhs_bits = [f"{lhs}[{i}]" for i in range(width - 1, -1, -1)]

        if len(lhs_bits) != len(rhs_bits):
            raise ValueError(f"Bit width mismatch: LHS {lhs_bits} != RHS {rhs_bits}")

        result.extend(zip(lhs_bits, rhs_bits))
    return result


def extract_param_names(raw_parameters):
    """
    Extracts the names of input/output/inout parameters from a module definition string.

    Parameters
    ----------
    raw_parameters : str
        String of the module's parameter list, e.g. "input a, output [3:0] b".

    Returns
    -------
    list[str]
        Ordered list of parameter names as they appear in the string.
    """
    return re.findall(
        r"\b(?:input|output|inout)?\s*(?:\[.*?\]\s*)?(\w+)", raw_parameters
    )


def sort_expanded_vars(expanded_vars, raw_parameters):
    """
    Sorts a list of expanded signal names (e.g. in[3], in[2], ..., in[0])
    based on their order in the module definition and from MSB to LSB.

    Parameters
    ----------
    expanded_vars : list[str]
        List of bit-level signal names.
    raw_parameters : str
        Module parameter list string for determining signal order.

    Returns
    -------
    list[str]
        Sorted list of expanded variables.
    """
    param_order = extract_param_names(raw_parameters)
    order_map = {name: i for i, name in enumerate(param_order)}

    def sort_key(var):
        base, idx = re.match(r"(\w+)(?:\[(\d+)\])?", var).groups()
        return (order_map[base], -int(idx) if idx else 0)

    return sorted(expanded_vars, key=sort_key)


def sort_raw_vars(raw_list, raw_parameters):
    """
    Sorts unexpanded input/output/inout declarations by the order of their
    parameter names in the module definition.

    Parameters
    ----------
    raw_list : list[str]
        List of unexpanded variable declarations, e.g. "input [3:0] a;".
    raw_parameters : str
        Module parameter list string for determining signal order.

    Returns
    -------
    list[str]
        Sorted list of raw declarations.
    """
    param_order = extract_param_names(raw_parameters)
    order_map = {name: i for i, name in enumerate(param_order)}

    def sort_key(line):
        match = re.search(r"(\w+)\s*;", line)
        return order_map.get(match.group(1), float("inf")) if match else float("inf")

    return sorted(raw_list, key=sort_key)
