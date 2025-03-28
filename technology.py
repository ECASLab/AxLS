
import re
from re import split, match, findall
import xml.etree.cElementTree as ET
import xml.dom.minidom

from pathlib import Path

class TechLibCell:
    '''
    Intermediate representation of a technology library cell

    Attributes
    -----------
    name : str
        name of the technology library cell
    inputs : array
        inputs of the technology library cell
    outputs : array
        outputs of the technology library cell
    '''

    def __init__ (self, name, inputs, outputs):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs


class Technology:
    '''
    Representates the information of the technology file using an xml structure

    Attributes
    -----------
    cells : array
        list of Technology Library Cells
    root : ElementTree.Element
        object that references the root element of the Technology Library tree
    '''

    def __init__(self, tech):
        self.cells = []

        with open(f"{Path(__file__).parent}/templates/{tech}.v", 'r') as technology_file:
            content = technology_file.read()

            # split the technology file in modules
            modules = [f"module{l}module" for l in content.split('module')]

            for module in modules:
                if (not 'input' in module or not 'output' in module):
                    continue
                elif ('primitive' in module):
                    continue
                else:
                    # extract the module information
                    header = match(r'module (.+) \((.+)\);', module)
                    module_name = header.group(1)
                    module_inputs = findall(r'input[\s\t]+(.+);', module)
                    module_outputs = findall(r'output[\s\t]+(.+);', module)
                    # there was a fix to remove commas here

                    self.cells.append(
                        TechLibCell(module_name,module_inputs,module_outputs)
                    )

        self.root = self.to_xml()


    def to_xml(self):
        '''
        Converts the cells (modules) of the Technology Library into a xml file

        Returns
        -------
        ElementTree.Element
            Reference to the root node of the technology library modules tree

        '''

        root = ET.Element("root")
        for c in self.cells:
            cell = ET.SubElement(root, "cell")
            cell.set('name',c.name)
            for i in c.inputs:
                ET.SubElement(cell, "input").text = i
            for o in c.outputs:
                ET.SubElement(cell, "output").text = o



        return root
