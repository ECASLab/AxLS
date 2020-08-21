
def GetOneNode(netl_root):
    '''
    Each time is called, return a node that could be replaced because its
    value is logic 0 or logic 1 almost always

    Nodes are ordered by the time they are on logic 0 or 1 and then returned

    Parameters
    ----------
    netl_root : ElementTree.Element
        root element of the circuit tree

    Returns
    -------
    array
        list of the node to be pruned, logic 1/0 and percentage of time it has
        this value wired
    '''
    nodes_info = []
    nodes = netl_root.findall("node")

    for node in nodes:
        var = node.attrib["var"]
        node_output = node.findall("output")[0]
        if "t1" in node_output.attrib:
            t1 = int(node_output.attrib["t1"])
            t0 = int(node_output.attrib["t0"])
            if t1 > t0:
                nodes_info.append([var, '1', t1])
            else:
                nodes_info.append([var, '0', t0])
    nodes_info = sorted(nodes_info, key=lambda z: z[2], reverse=True)

    while (len(nodes_info) > 0):
        result = nodes_info[0]
        nodes_info = nodes_info[1:]
        yield result
