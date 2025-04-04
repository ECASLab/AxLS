
def get_parents(n, root):
    '''
    Check if node's children has ancestry in the cut
    '''
    return [root.findall('node/output[@wire="'+i.attrib['wire']+'"]/..') for i in n.findall('input')]

def check_node_delete_status(n):
    #Auxiliary function to check if node is marked to be deleted
    if 'delete' in n.keys():
        #Return true if the node is not marked to be deleted, returns false otherwise
        return n.attrib['delete']!='yes'
    else:
        #By default include nodes that doesn't have the attribute 'delete'.
        #that attribute will be present only in nodes analyzed for pruning in previous iterations.
        return True

class Cut:
    '''
    A branch in the exploration tree of the circuit carving algorithm. Representing a set of nodes in the circuit's graph
    that could be pruned.

    Attributes
    -----------

    difference: int
        Difference value of the cut.

    nodes: list
        A list of nodes included in the cut.

    size: int
        How many nodes are in the cut.

    circuit_root:
        Root of the circuit tree.
    '''

    def __init__(self,netlroot):
        self.difference=0
        self.nodes=[]
        self.size=0
        self.circuit_root=netlroot

    def addNode(self,node, diff):
        '''

        Adds a new node to the cut

        Parameters
        ----------
        node: ElementTree.element
            a node to append in the cut
        diff: integer
            Difference to add in the cut.

        '''

        self.nodes.append(node)
        self.size=self.size+1
        self.difference+=diff

    def deleteNode(self,node, diff):
        '''

        delete a node in the cut

        Parameters
        ----------
        node: ElementTree.element
            a node to remove from the cut
        diff: integer
            Difference to substract  in the cut.

        '''

        self.nodes.remove(node)
        self.size=self.size-1
        self.difference-=diff

    def AddedDiff_aux(self,node, diff='significance'):
        '''
        auxiliary function to get cut difference after a node expansion

        Parameters
        ----------
        node: ElementTree.element
            a node to append in the cut.
        diff: string
            The name of the criteria used as difference, as it is in the attributes of node node.

        Returns
        -------
        integer:
            A difference value to add
        '''

        d=0 #Added Difference value
        if (self.nodes==[]): #Check if empty cut
            d+=node.attrib[diff]
            return d
        else:
            #Find outgoing edges
            outputs=[o for k in [n.findall('output') for n in self.nodes] for o in k]
            wires=[o.attrib['wire'] for o in outputs] #wires connected to each edge


            n_inputs= [n.attrib['wire'] for n in node.findall('input')] #inputs of node

            #Check if node is a children of the cut
            children=[c for c in self.circuit_root.findall('node/input[@wire="'+node.findall('output')[0].attrib['wire']+'"]/..')]#children of node node
            children=[c for c in children if check_node_delete_status(c)] #Exclude deleted nodes
            if not any([(i in wires) for i in n_inputs]):
                if children==[]: #if empty, node's output is also a circuit output
                    d+=float(self.circuit_root.findall(f'circuitoutputs/output[@var="{node.findall("output")[0].attrib["wire"]}"]')[0].attrib[diff])#its valid, and its significance correspond to the output's significance
                    return d
                else:
                    children=[c for c in children if c not in self.nodes] #filter children in cut

                    for c in children:
                        parents=[i for k in get_parents(c,self.circuit_root) for i in k ]
                        parents=[p for p in parents if check_node_delete_status(p)] #filter parents
                        parents.remove(node)
                        while parents!=[]:
                            p=parents.pop(0)
                            if p in self.nodes and p!=node:
                                children.remove(c)
                                break
                            else:
                                [parents.append(i) for k in get_parents(p,self.circuit_root) for i in k]

                    d+=sum([float(c.attrib[diff]) for c in children])
        return d

    def checkDiff(self,node, threshold: float, diff='significance'):
        '''

        Checks if adding a certain nod satisfies the Difference Threshold criterion

        Parameters
        ----------
        node: ElementTree.element
            a node to append in the cut.
        threshold: integer
            upper limit for cut difference value.
        diff: string
            The name of the criteria used as difference, as it is in the attributes of node node.

        Returns
        -------
        boolean:
            Whether the addition meets difference threshold criterion or not
        integer:
            A difference value to add

        '''

        d=self.AddedDiff_aux(node, diff)
        if self.difference+d<threshold:
            return True, d
        else:
            return False, 0

    def checkClosure(self, node):
        '''

        Checks if the cut C will be a closed cut if node is added.

        Parameters
        ----------
            node: ElementTree.element node
                A node element of circuit's tree

        Returns
        -------

        boolean
            Whether the cut will be close or not.

        list:
            Nodes that must be included with n to make the cut C close

        '''

        valid=True #bool to indicate closure
        must_include=[] #List of nodes that must be included to make cut close if n is added

        '''Check parents of node '''
        parents=[]
        for wire in node.findall('input'):
            [parents.append(n) for n in self.circuit_root.findall('./node/output[@wire="' + wire.attrib['wire'] + '"]/..')]
        parents=[p for p in parents if (check_node_delete_status(p) and (p not in self.nodes))] #filter parents

        for p in parents: #Check not in cut parents
            '''get p's children'''
            children=[c for c in self.circuit_root.findall(f'./node/input[@wire="{p.findall("output")[0].attrib["wire"]}"]/..') ]
            children.remove(node)
            children=[c for c in children if (check_node_delete_status(c) and (c not in self.nodes))] #filter children

            if (children==[]):
                valid=False
                must_include.append(p)

        '''Check children of node '''
        children=self.circuit_root.findall(f'./node/input[@wire="{node.findall("output")[0].attrib["wire"]}"]/..')
        children=[c for c in children if (check_node_delete_status(c) and (c not in self.nodes))]
        for c in children:
            '''get c's parents'''
            parents=[self.circuit_root.findall(f'./node/output[@wire="{i.attrib["wire"]}"]/..') for i in c.findall('input')]
            parents=[p for k in parents for p in k]
            parents.remove(node)
            parents=[p for p in parents if (check_node_delete_status(p) and (p not in self.nodes))]
            if (parents==[]):
                valid=False
                must_include.append(c)

        return valid, must_include

    def checkNodes(self, left_nodes, cut_threshold):
        '''

        Checks the Number of gates criterion for cut C.

        Parameters
        ----------
            left_nodes: int
                How many nodes left to be considered
            cut_threshold: int
                The number of nodes in the biggest cut found

        Returns
            bool:
                Whether the cut meets the criterion, and thus is worth to continue the exploration, or not.
        -------

        '''

        return len(self.nodes)+left_nodes>cut_threshold

    def expandCut(self, node, diff_threshold, diff='significance', added_nodes=[]):
        '''

        Tries to add a node, checking the closure criterion and adding other nodes if needed to maintain closure

        Parameters
        ----------
        node: ElementTree.element
            Node to add to the cut.
        added_nodes: list
            Nodes list of already added nodes by this function

        Returns
        -------
            bool:
                Whether the cut was succesfully expanded with node or not
            list:
                nodes added to the cut and their added difference value

        '''

        meets_diff,diff_to_add=self.checkDiff(node, threshold=diff_threshold, diff=diff)
        if meets_diff:
            meets_closure, nodes_to_add=self.checkClosure(node)
            self.addNode(node,diff_to_add)
            added_nodes.append([node,diff_to_add])
            if meets_closure:
                return True, added_nodes
            else:
                for n in nodes_to_add:
                    result, added_nodes=self.expandCut(n,diff_threshold,diff, added_nodes)
                    if not result:
                        if added_nodes!=[]:
                            [self.deleteNode(k[0],k[1]) for k in added_nodes]
                        return False, []#added nodes=[]

                return True, added_nodes #Succesfull expansion
        else:
            if added_nodes!=[]:
                [self.deleteNode(k[0],k[1]) for k in added_nodes]
            return False, []



def FindCut(netlroot, diff_threshold, diff='significance', harshness_level=0):
    '''

    Parameters
    ----------
    netlroot: ElementrTree.element
        Root of the circuit where cuts will be explored
    diff_threshold: int
        Upper limit for difference metric in the cut
    diff: str
        Difference metric used as label for the cut
    harshness_level: int
        Determines how aggressive the exploration will be, in terms of how many times it wil attempt to expand a cut.
        A value of 0 means infinite, exploring the cuts as much as possible.


    Returns
    -------
        list:
            A list of cuts/nodes that could be pruned
    '''

    '''Use threshold to limit cut exploration (Nodes with a difference greater than the threshold would never produce valid cuts)'''
    cut_list=[]
    while True:
        all_nodes=netlroot.findall('./node') #get all nodes
        all_nodes=[n for n in all_nodes if float(n.attrib[diff])<diff_threshold] #filter nodes by difference
        all_nodes=[n for n in all_nodes if check_node_delete_status(n)] #filter deleted nodes
        all_nodes=[n for n in all_nodes if n not in [i for k in cut_list for i in k]]#filter nodes already considered in other cuts

        if all_nodes==[]:
            break

        all_nodes.sort(key=lambda n: float(n.attrib[diff]),reverse=True)#sort nodes by difference criteria, greater first

        '''Create a cut object'''
        cut=Cut(netlroot)
        biggest_cut=Cut(netlroot)
        cut_record=0
        banned_nodes=[]
        '''Attempt to add a node in the cut and make it bigger'''
        tries=0
        while (all_nodes!=[]):

            nodes_list=[n for n in all_nodes if n not in (biggest_cut.nodes + banned_nodes)]
            while nodes_list!=[]:
                for n in nodes_list:
                    result, added_nodes=cut.expandCut(n,diff_threshold,diff,[])
                    if not result:
                        banned_nodes.append(n)
                    else:
                        if cut.size>cut_record:
                            biggest_cut=None
                            biggest_cut=Cut(netlroot)
                            [biggest_cut.addNode(n,0) for n in cut.nodes]
                            biggest_cut.difference=cut.difference
                            cut_record=biggest_cut.size

                        elif cut_record==cut.size:
                            if cut.difference<biggest_cut.difference:
                                biggest_cut=None
                                biggest_cut=Cut(netlroot)
                                [biggest_cut.addNode(n,0) for n in cut.nodes]
                                biggest_cut.difference=cut.difference
                                biggest_cut.size=cut.size
                                cut_record=biggest_cut.size

                    [cut.deleteNode(n[0],n[1]) for n in added_nodes]

                cut=biggest_cut
                tries+=1
                nodes_list=[n for n in nodes_list if n not in (biggest_cut.nodes)]
                if (tries>=harshness_level) and (harshness_level!=0): #Hard exploration
                    break
            if biggest_cut.nodes==[]:
                break
            else:
                cut_list.append(biggest_cut.nodes)
                all_nodes=[n for n in all_nodes if n not in biggest_cut.nodes]

                #Clear for a new expansion
                cut=None
                cut=Cut(netlroot)
                biggest_cut=None
                biggest_cut=Cut(netlroot)
                cut_record=0
    return cut_list
