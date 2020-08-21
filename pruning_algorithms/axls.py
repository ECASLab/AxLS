
def GetInputsAux(netl_root, node, constants, path):
    '''
    Appends nodes that could be deleted to the path variable
    Those nodes can be deleted because their inputs are constant values

    Parameters
    ----------
    netl_root : ElementTree.Element
        root of the circuit tree
    node : ElementTree.Element
        node that we are processing
    constants : array
        list of wires that could be replaced by a constant value
    path : array
        list of ElementTree.Element nodes that can be deleted
    '''
    node_inputs = node.findall("input")
    node_inputs = [i for i in node_inputs if not i.attrib["wire"] in constants]
    if (len(node_inputs) == 0):
        # all input wires are constants
        if not node in path:
            path.append(node)
        for output in node.findall("output"):
            o = output.attrib["wire"]
            if (not o in constants):
                constants.append(o)
            children = netl_root.findall(f"./node/input[@wire='{o}']/..")
            for child in children:
                GetInputsAux(netl_root, child, constants, path)


def GetInputs(netl_root, inputs):
    '''
    Returns nodes that could be deleted because inputs[bit] are constant values

    Parameters
    ----------
    netl_root : ElementTree.Element
        root of the circuit tree
    inputs : array
        list of inputs variable names to be pruned

    Returns
    -------
    array
        List of elements that can be deleted
    '''
    path = []
    '''
    inputs = netl_root.findall("./circuitinputs/input")
    input_wires = [i.attrib["var"] for i in inputs]
    constants = []

    # get the input constants
    for b in range(0,bit+1):
        constant_wires = [w for w in input_wires if f"[{str(b)}]" in w]
        constants += constant_wires
    '''
    constants = inputs
    # start iterating from the nodes that have constant inputs
    for c in constants:
        children = netl_root.findall(f"./node/input[@wire='{c}']/..")
        for c in children:
            GetInputsAux(netl_root, c, constants, path)

    return path


def GetOutputsAux(netl_root, node, constants, path):
    '''
    Appends nodes that could be deleted to the path variable
    Those nodes can be deleted because their outputs only affect other constant

    Parameters
    ----------
    netl_root : ElementTree.Element
        root of the circuit tree
    node : ElementTree.Element
        node that we are processing
    constants : array
        list of wires that could be replaced by a constant value
    path : array
        list of ElementTree.Element nodes that can be deleted
    '''
    node_output = node.findall("output")[0].attrib["wire"]

    children = netl_root.findall(
        "./node/input[@wire='" + node_output + "']/..")

    children_to_keep = [c for c in children if not c.attrib["var"] in constants]

    if (len(children_to_keep) == 0):
        #node.set ("delete", "yes")
        if not node.attrib["var"] in constants:
            constants.append(node.attrib["var"])
        if not node in path:
            path.append(node)

        # keep going back
        for input in node.findall("input"):
            xpath = "./node/output[@wire='" + input.attrib["wire"] + "']/.."
            parents = netl_root.findall(xpath)
            for parent in parents:
                GetOutputsAux (netl_root, parent, constants, path)


def GetOutputs(netl_root, outputs):
    '''
    Returns nodes that could be deleted because outputs[bit] are constant values

    Parameters
    ----------
    netl_root : ElementTree.Element
        root of the circuit tree
    outputs : array
        list of output variable names to be pruned

    Returns
    -------
    array
        List of elements that can be deleted
    '''
    path = []

    constants = outputs
    for output in outputs:
        nodes = netl_root.findall(f"./node/output[@wire='{output}']/..")
        for node in nodes:
            GetOutputsAux(netl_root, node, constants, path)

    return path
