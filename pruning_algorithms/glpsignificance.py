
def GetbySignificance(netlroot, output_significances=[]):
    '''

    On each call, the function returns one depricable node using significance as criteria.
    Significance is a metric that indicates a how important is a node in the structure of the circuit and its
    functionality.
    Significance is calculated propagating outputs significance to the inputs.

    See: Schlacther et al., "Design and Applications of Approximate Circuits by Gate-Level Pruning",2017.

    Parameters
    ----------
    netlroot: ElemntTree.Element
        root of the circuit tree object

    output_significances: list
        list of significances for circuit outputs,
        if empty it is assumed that significance of output node is 2^node (LSB has less significance that MSB)

    Returns
    -------
    array
        a list of nodes and its significance in ascendant order

    '''

    '''Label Nodes if necessary'''
    _=LabelCircuit(netlroot,output_significances)

    '''Get and sort all significances'''
    nodes=[]
    for n in netlroot.findall("./node"):
        nodes.append([n.attrib["var"],n.attrib["significance"]])
    nodes=sorted(nodes,key= lambda z: z[1])


    return nodes

def GetSignificance(netlroot, node, overwrite=False):
    '''
    A recursive function to calculate and set the significance attribute to each node in a circuit's tree

    Parameters
    ----------
    netlroot: ElementTree.Element
        circuit's tree root

    node: ElementTree.Element
        current node to get its significance value

    overwrite: boolean
        Whether to overwrite or not existing significance value in the nodes

    Returns
    -------
    significance: integer
        current node's significance value
    '''


    circuit_outputs=[o for o in netlroot.findall("./circuitoutputs/output")] #All circuit outputs
    co_names=[o.attrib["var"] for o in circuit_outputs] #circuit outputs names
    significance=0 #current node's significance

    for o in node.findall("output"): #for each output of the node...
        if o.attrib["wire"] in co_names: #if o matches with a circuit output, sum its significance
            significance+=int(netlroot.findall("./circuitoutputs/output[@var='"+o.attrib["wire"]+"']")[0].attrib["significance"])
        else:
            children=netlroot.findall("./node/input[@wire='"+o.attrib["wire"]+"']/..") #get nodes whose inputs are the same wire as the current output
            for child in children:
                if overwrite:
                    significance+=int(GetSignificance(netlroot,child))
                elif not 'significance' in child.keys():
                    significance+=int(GetSignificance(netlroot,child))
                else:
                    significance+=child.attrib['significance']

    node.attrib["significance"]=significance #set node's significance
    return significance

def LabelCircuit(netlroot,output_significances=[], overwrite=False):
    '''

    Labels a circuit by significance criterion

    Parameters
    ----------
    netlroot: ElemntTree.Element
        root of the circuit tree object
    
    overwrite: boolean
        Whether to overwrite existing labels

    output_significances: list
        list of significances for circuit outputs,
        if empty it is assumed that significance of output node is 2^node (LSB has less significance that MSB)

    '''

    outputs=[o for o in netlroot.findall("./circuitoutputs/output")] #All circuit outputs
    if output_significances==[]: #check if not custom output significances were given
        output_significances=[2**i for i in range(len(outputs))]
    elif len(output_significances)!=len(outputs): #if custom significances does not match...
        raise ValueError("Output significances length does not match with circuit number of outputs")

    for o,s in zip(outputs,output_significances):#set output significances
        o.attrib["significance"]=str(s)

    '''Get all the nodes connected to inputs'''
    inputs=[i for i in netlroot.findall("./circuitinputs/input")]
    parents=[]
    for i in inputs:
        [parents.append(p) for p in netlroot.findall("./node/input[@wire='"+i.attrib["var"]+"']/..") if p not in parents]

    '''Calculate significance for all the parent nodes (and thus, for all the children nodes due recursivity)'''
    for p in parents:
        GetSignificance(netlroot,p,overwrite)

    return 0

