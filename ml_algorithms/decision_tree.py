from collections import OrderedDict
from typing import List
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree._tree import Tree


class CircuitVariable:
    """Represents a circuit variable with a name and bit width."""

    def __init__(self, name: str, bits: int):
        self.name = name
        self.bits = bits


class DecisionTreeCircuit:
    """A decision tree classifier that learns circuits.

    This class wraps a sickit DecisionTreeClassifier with utilities to make it
    easy to train on circuit data generated by AxLS and synthesize the result
    into a verilog circuit.

    Parameters
    ----------
    circuit_inputs : list of str
        A list of the input variable names in Verilog style, e.g., ['cin', 'in1[3]', 'in1[2]', 'in1[1]', 'in1[0]', 'in2[3]', 'in2[2]', 'in2[1]', 'in2[0]'].

    circuit_outputs : list of str
        A list of the output variable names in Verilog style, e.g., ['out1[3]', 'out1[2]', 'out1[1]', 'out1[0]'].

    one_tree_per_output : bool, default=False
        By default this class trains 1 single multi-output classifier tree. But
        if this is set to True, then it will use multiple classifier trees, a
        different one for each circuit output.

    **kwargs : dict
        Keyword arguments to be passed to the scikit-learn
        DecisionTreeClassifier constructor. For a list of available parameters,
        please refer to the scikit-learn documentation:
        https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html

        Useful parameters include but are not limited to: max_depth,
    """

    clf: DecisionTreeClassifier | List[DecisionTreeClassifier]
    one_tree_per_output: bool
    inputs: List[CircuitVariable]
    outputs: List[CircuitVariable]
    _trained: bool

    circuit_inputs: List[str]
    circuit_outputs: List[str]

    def __init__(
        self,
        circuit_inputs: List[str],
        circuit_outputs: List[str],
        one_tree_per_output=False,
        **kwargs,
    ):
        self.circuit_inputs = circuit_inputs
        self.circuit_outputs = circuit_outputs
        self.inputs = _parse_circuit_variables(circuit_inputs)
        self.outputs = _parse_circuit_variables(circuit_outputs)
        self._trained = False
        self.one_tree_per_output = one_tree_per_output
        if one_tree_per_output:
            self.clf = [
                DecisionTreeClassifier(**kwargs)
                for _ in range(len(self.circuit_outputs))
            ]
        else:
            self.clf = DecisionTreeClassifier(**kwargs)

    def train(self, X: List[List[int]], y: List[List[int]]):
        """Train the decision tree classifier(s) with the training set (X, y).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The training input samples as integers.

        y : array-like of shape (n_samples, n_outputs)
            The target values as integers.
        """
        input_bit_widths = [input.bits for input in self.inputs]
        output_bit_widths = [output.bits for output in self.outputs]

        inputs = _to_binary(X, input_bit_widths)
        outputs = _to_binary(y, output_bit_widths)

        if isinstance(self.clf, DecisionTreeClassifier):
            self.clf.fit(inputs, outputs)
        else:
            for clf, outputs in zip(self.clf, outputs.transpose()):
                clf.fit(inputs, outputs)

        self._trained = True

    def to_verilog_file(self, topmodule: str, output_file: str):
        """
        Generate a synthesizable Verilog file representing the learned decision tree(s).

        Parameters
        ----------
        topmodule : str
            The name of the top-level Verilog module.
        output_file : str
            Path to the output file where the Verilog code will be written.
        """

        if not self._trained:
            raise RuntimeError(
                "This model instance is not trained yet. Call 'train' with appropriate arguments before using this method."
            )

        raw_parameters = ", ".join(
            [variable.name for variable in self.inputs + self.outputs]
        )
        raw_inputs = [
            f"input {variable.name};"
            if variable.bits == 1
            else f"input [{variable.bits}:0] {variable.name};"
            for variable in self.inputs
        ]
        raw_outputs = [
            f"output {variable.name};"
            if variable.bits == 1
            else f"output [{variable.bits - 1}:0] {variable.name};"
            for variable in self.outputs
        ]

        with open(output_file, "w") as f:
            f.write(f"module {topmodule} ({raw_parameters});\n")

            for input in raw_inputs:
                f.write(f"    {input}\n")
            for output in raw_outputs:
                f.write(f"    {output}\n")

            for i, output in enumerate(self.circuit_outputs):
                if isinstance(self.clf, DecisionTreeClassifier):
                    equation = _tree_2_equation(
                        self.clf.tree_, i, 0, self.circuit_inputs
                    )
                else:
                    equation = _tree_2_equation(
                        self.clf[i].tree_, 0, 0, self.circuit_inputs
                    )
                f.write(
                    f"    assign {output} = {equation};\n"
                )  # Directly assign the Boolean equation to 'f'
            f.write("endmodule\n")


def _to_binary(x: List[List[int]], bit_widths: List[int]):
    """Convert a list of lists of integers to a binary representation.

    This function takes a list input rows `x` and a list of bit widths
    `bit_widths`, which provides the bit width of each input variable, and
    converts the input data into a binary representation. The resulting array
    has a column for each bit position, with each column containing 0s and 1s
    representing the binary values for that bit position.

    The bits go from MSB -> LSB.

    TODO: This function should be put in a common module to be used by future ML
    methods when new ones are added.

    Parameters
    ----------
    x : List[List[int]]
        A list of lists of integers, where each inner list represents a row of input data.
    bit_widths : List[int]
        A list of integers, where each value represents the number of bits to use for the
        corresponding column in the input data.

    Returns
    -------
    numpy.ndarray
        A 2D numpy array of shape (len(x), sum(bit_widths)), where each row
        represents the binary representation of the corresponding row in the
        input data `x`, and each column represents a specific bit position.

    Examples
    --------
    >>> _to_binary([[1, 1], [2, 2], [3, 0xF]], [2, 4])
    array([[0, 1, 0, 0, 0, 1],
           [1, 0, 0, 0, 1, 0],
           [1, 1, 1, 1, 1, 1]], dtype=uint8)
    """
    columns = np.transpose(np.array(x))
    result = []

    for column, width in zip(columns, bit_widths):
        if width <= 8:
            dtype = np.uint8
        if width <= 16:
            dtype = np.uint16
        if width <= 32:
            dtype = np.uint32
        if width <= 64:
            dtype = np.uint64
        else:
            dtype = np.object_

        column = np.array(column, dtype=dtype)
        shifts = np.arange(width - 1, -1, -1, dtype=dtype)

        column = column[:, None] >> shifts & 1

        result.append(np.array(column, dtype=np.uint8))

    result = np.column_stack(result)
    return result


def _parse_circuit_variables(variable_list: List[str]):
    """Parse a list of circuit variable names and bit widths.

    TODO: This function should be put in a common module to be used by future ML
    methods when new ones are added.

    Parameters
    ----------
    input_list : List[str]
        A list of strings representing circuit variables, where each variable can be
        either a single-bit variable (e.g., 'cin') or a multi-bit variable (e.g., 'in1[3]').

    Returns
    -------
    List[CircuitVariable]
        A list of `CircuitVariable` objects, where each object represents a
        circuit variable with a name and bit width.
    """
    variables = OrderedDict()
    for item in variable_list:
        if "[" in item:
            name = item.split("[")[0]
            if name not in variables:
                variables[name] = CircuitVariable(name, 1)
            else:
                variables[name] = CircuitVariable(name, variables[name].bits + 1)

        else:
            variables[item] = CircuitVariable(item, 1)

    return list(variables.values())


def _tree_2_equation(
    tree: Tree, output: int, node: int, circuit_inputs: list[str], depth=0
):
    """
    Recursively convert a decision tree node into a Boolean equation string.

    Parameters
    ----------
    tree : sklearn.tree._tree.Tree
        The underlying decision tree structure.
    output : int
        Output index to extract from multi-output trees.
    node : int
        Current node index in the tree.
    circuit_inputs : list of str
        Flat list of all bit-level input variable names.
    depth : int, optional
        Current recursion depth (used for internal tracing/debugging).

    Returns
    -------
    str or None
        A Boolean expression string for the subtree rooted at `node`, or None if
        the subtree always evaluates to 0.
    """
    if tree.feature[node] == -2:  # Leaf node
        result = tree.value[node][output].argmax()
        if result == 0:
            return None
        else:
            return "LEAF_NODE_1"

    else:  # Internal node
        left_result = _tree_2_equation(
            tree, output, tree.children_left[node], circuit_inputs, depth + 1
        )
        right_result = _tree_2_equation(
            tree, output, tree.children_right[node], circuit_inputs, depth + 1
        )

        feature = tree.feature[node]

        input = circuit_inputs[feature]
        negated_input = f"!{input}"

        match (left_result, right_result):
            case (None, None):
                return None

            case (None, "LEAF_NODE_1"):
                return input
            case ("LEAF_NODE_1", None):
                return negated_input
            case ("LEAF_NODE_1", "LEAF_NODE_1"):
                return "LEAF_NODE_1"

            case (str(left), "LEAF_NODE_1"):
                return f"{input} | ({left})"
            case ("LEAF_NODE_1", str(right)):
                return f"{negated_input} | ({right})"

            case (str(left), None):
                return f"{negated_input} & ({left})"
            case (None, str(right)):
                return f"{input} & ({right})"
            case (str(left), str(right)):
                return f"({negated_input} & ({left})) | ({input} & ({right}))"
